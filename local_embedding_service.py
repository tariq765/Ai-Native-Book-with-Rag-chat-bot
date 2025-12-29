from typing import List
from config import Config
from sentence_transformers import SentenceTransformer
import numpy as np

class LocalEmbeddingService:
    def __init__(self):
        # Using a lightweight but effective sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_texts(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using local model
        """
        embeddings = self.model.encode(texts)
        return [embedding.tolist() for embedding in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query using local model
        """
        embedding = self.model.encode([query])
        return embedding[0].tolist()