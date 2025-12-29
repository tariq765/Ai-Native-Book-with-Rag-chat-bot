import os
import re
import time
from typing import List, Dict, Any
from pathlib import Path
from config import Config
from embedding_service import EmbeddingService
from qdrant_service import QdrantService

class DocumentService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def read_documents_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Read all markdown documents from the specified directory
        """
        documents = []
        path = Path(directory_path)

        for file_path in path.rglob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Create document object
                doc = {
                    'id': str(file_path),
                    'text': content,
                    'source': str(file_path.relative_to(path)),
                    'metadata': {
                        'filename': file_path.name,
                        'relative_path': str(file_path.relative_to(path)),
                        'size': len(content)
                    }
                }
                documents.append(doc)

        return documents

    def chunk_text(self, text: str, chunk_size: int = Config.CHUNK_SIZE, overlap: int = Config.OVERLAP_SIZE) -> List[str]:
        """
        Split text into overlapping chunks
        """
        # Simple sentence-based chunking
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk + " " + sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Handle sentences that are longer than chunk_size by splitting them
                if len(sentence) > chunk_size:
                    # Split long sentence into smaller parts
                    parts = [sentence[i:i+chunk_size] for i in range(0, len(sentence), chunk_size)]
                    chunks.extend(parts[:-1])  # Add all but the last part to chunks
                    current_chunk = parts[-1]  # Keep the last part as the start of the next chunk
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Add overlap between chunks
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # Add overlap from the previous chunk
                    prev_chunk_words = chunks[i-1].split()
                    overlap_text = ' '.join(prev_chunk_words[-overlap:])
                    chunk = overlap_text + ' ' + chunk
                overlapped_chunks.append(chunk)
            return overlapped_chunks

        return chunks

    def ingest_documents(self, documents_directory: str):
        """
        Ingest documents from the specified directory into the vector database
        """
        # Read documents
        documents = self.read_documents_from_directory(documents_directory)

        # Create collection in Qdrant
        # Note: We need to determine the embedding dimension, which for Cohere is typically 1024
        self.qdrant_service.create_collection(vector_size=1024)

        all_doc_chunks = []

        for doc in documents:
            # Chunk the document
            chunks = self.chunk_text(doc['text'])

            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    'id': f"{doc['id']}_chunk_{i}",
                    'text': chunk,
                    'source': doc['source'],
                    'metadata': {
                        **doc['metadata'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                }
                all_doc_chunks.append(chunk_doc)

        # Process in batches to avoid timeout
        batch_size = 5  # Process 5 chunks at a time to avoid timeout
        total_chunks = len(all_doc_chunks)

        print(f"Processing {total_chunks} chunks in batches of {batch_size}...")

        for batch_start in range(0, total_chunks, batch_size):
            batch_end = min(batch_start + batch_size, total_chunks)
            batch_chunks = all_doc_chunks[batch_start:batch_end]

            print(f"Processing batch {batch_start//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size} (chunks {batch_start+1}-{batch_end})...")

            # Generate embeddings for batch
            chunk_texts = [chunk['text'] for chunk in batch_chunks]
            embeddings = self.embedding_service.embed_texts(chunk_texts)

            # Prepare documents with embeddings for upsert
            documents_with_embeddings = []
            for i, chunk_doc in enumerate(batch_chunks):
                chunk_doc['embedding'] = embeddings[i]
                documents_with_embeddings.append(chunk_doc)

            # Upsert batch to Qdrant with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.qdrant_service.upsert_documents(documents_with_embeddings)
                    print(f"Batch {batch_start//batch_size + 1} uploaded successfully!")
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"Error uploading batch (attempt {attempt + 1}/{max_retries}): {e}")
                        print("Waiting 5 seconds before retry...")
                        time.sleep(5)
                    else:
                        print(f"Failed to upload batch after {max_retries} attempts")
                        raise

            # Add delay between batches to avoid rate limiting
            time.sleep(2)

        return {
            'status': 'success',
            'documents_processed': len(documents),
            'chunks_created': len(all_doc_chunks),
            'collection_name': self.qdrant_service.collection_name
        }