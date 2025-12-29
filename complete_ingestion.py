import time
from document_service import DocumentService
from qdrant_service import QdrantService

print("Starting incremental document ingestion...")

# Initialize services
qdrant_service = QdrantService()
document_service = DocumentService()

# Check current status
try:
    collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
    current_count = collection_info.points_count
    print(f"Current points in collection: {current_count}")
except Exception as e:
    print(f"Error checking collection: {e}")
    current_count = 0

# Read all documents
textbook_path = "../physical-ai-humanoid-robotics-ts/docs"
documents = document_service.read_documents_from_directory(textbook_path)
print(f"Found {len(documents)} documents")

# Chunk all documents
all_doc_chunks = []
for doc in documents:
    chunks = document_service.chunk_text(doc['text'])
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

total_chunks = len(all_doc_chunks)
print(f"Total chunks to process: {total_chunks}")

# Process remaining chunks (skip already processed ones)
start_from = current_count
if start_from >= total_chunks:
    print("All chunks already ingested!")
else:
    print(f"Will process chunks from {start_from} to {total_chunks}")

    # Process in very small batches with delay
    batch_size = 3  # Very small batches

    for batch_start in range(start_from, total_chunks, batch_size):
        batch_end = min(batch_start + batch_size, total_chunks)
        batch_chunks = all_doc_chunks[batch_start:batch_end]

        print(f"\nProcessing batch (chunks {batch_start+1}-{batch_end}/{total_chunks})...")

        # Generate embeddings for batch
        chunk_texts = [chunk['text'] for chunk in batch_chunks]

        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                # Get embeddings
                embeddings = document_service.embedding_service.embed_texts(chunk_texts)

                # Prepare documents with embeddings
                documents_with_embeddings = []
                for i, chunk_doc in enumerate(batch_chunks):
                    chunk_doc['embedding'] = embeddings[i]
                    documents_with_embeddings.append(chunk_doc)

                # Upsert to Qdrant
                qdrant_service.upsert_documents(documents_with_embeddings)
                print(f"[OK] Batch uploaded successfully! ({batch_end}/{total_chunks} chunks total)")
                break

            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 5 * retry_count
                    print(f"[ERROR] Error (attempt {retry_count}/{max_retries}): {str(e)[:100]}")
                    print(f"  Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    print(f"[SKIP] Failed after {max_retries} attempts. Skipping this batch.")
                    break

        # Delay between successful batches
        time.sleep(3)

print("\n" + "="*50)
print("Ingestion complete!")

# Final status
try:
    collection_info = qdrant_service.client.get_collection(qdrant_service.collection_name)
    final_count = collection_info.points_count
    print(f"Final points in collection: {final_count}/{total_chunks}")
except Exception as e:
    print(f"Error checking final status: {e}")
