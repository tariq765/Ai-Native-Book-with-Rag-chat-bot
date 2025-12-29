import cohere
from typing import List
from config import Config

class EmbeddingService:
    def __init__(self):
        self.client = cohere.Client(Config.COHERE_API_KEY)
        self.model = "embed-english-v3.0"  # Cohere's latest embedding model

    def embed_texts(self, texts: List[str], input_type: str = "search_document") -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere
        """
        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type=input_type
        )
        return [embedding for embedding in response.embeddings]

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query using Cohere
        """
        response = self.client.embed(
            texts=[query],
            model=self.model,
            input_type="search_query"
        )
        return response.embeddings[0]