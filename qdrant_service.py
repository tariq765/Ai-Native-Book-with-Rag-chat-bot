from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from config import Config
import uuid
import os

class QdrantService:
    def __init__(self):
        # Try to use cloud Qdrant first, fall back to local if cloud is unavailable
        if Config.QDRANT_URL and Config.QDRANT_API_KEY:
            try:
                self.client = QdrantClient(
                    url=Config.QDRANT_URL,
                    api_key=Config.QDRANT_API_KEY,
                    timeout=60.0,  # Increase timeout to 60 seconds
                )
                self.collection_name = Config.QDRANT_COLLECTION_NAME
                print("Using cloud Qdrant instance")
            except Exception as e:
                print(f"Failed to connect to cloud Qdrant: {e}")
                print("Falling back to local Qdrant instance")
                self.client = QdrantClient(path=Config.LOCAL_QDRANT_PATH)
                self.collection_name = Config.QDRANT_COLLECTION_NAME
        else:
            # Use local Qdrant instance
            self.client = QdrantClient(path=Config.LOCAL_QDRANT_PATH)
            self.collection_name = Config.QDRANT_COLLECTION_NAME
            print("Using local Qdrant instance")

    def create_collection(self, vector_size: int = 1024):
        """
        Create a collection in Qdrant for storing document embeddings
        """
        try:
            # Check if collection already exists
            self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,  # Cohere embeddings are typically 1024 dimensions
                    distance=models.Distance.COSINE
                ),
            )
            print(f"Created collection {self.collection_name}")

    def upsert_documents(self, documents: List[Dict[str, Any]]):
        """
        Upsert documents into the Qdrant collection
        Each document should have: id, text, embedding, metadata
        """
        points = []
        for doc in documents:
            # Generate a proper ID (UUID) if not provided or if it's not a valid format
            doc_id = doc.get('id', str(uuid.uuid4()))
            if not self._is_valid_qdrant_id(doc_id):
                doc_id = str(uuid.uuid4())

            point = models.PointStruct(
                id=doc_id,
                vector=doc['embedding'],
                payload={
                    'text': doc['text'],
                    'source': doc.get('source', ''),
                    'metadata': doc.get('metadata', {}),
                    'chunk_id': doc.get('chunk_id', ''),
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def _is_valid_qdrant_id(self, id_val):
        """
        Check if the ID is a valid Qdrant ID (unsigned integer or UUID)
        """
        # Check if it's a UUID
        try:
            from uuid import UUID
            UUID(id_val)
            return True
        except ValueError:
            pass

        # Check if it's a numeric string (unsigned integer)
        try:
            return int(id_val) >= 0
        except ValueError:
            return False

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents based on the query vector
        """
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        results = []
        for result in search_results.points:
            results.append({
                'text': result.payload['text'],
                'source': result.payload['source'],
                'metadata': result.payload['metadata'],
                'score': result.score,
                'chunk_id': result.payload.get('chunk_id', ''),
            })

        return results

    def delete_collection(self):
        """
        Delete the entire collection (useful for re-indexing)
        """
        self.client.delete_collection(self.collection_name)