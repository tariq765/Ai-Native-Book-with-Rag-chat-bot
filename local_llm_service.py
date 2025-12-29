from typing import List, Dict, Any
from config import Config
import subprocess
import sys

class LocalLLMService:
    def __init__(self):
        # Try to initialize a local LLM - using Ollama as a fallback
        try:
            import requests
            self.requests = requests
            self.has_local_llm = True
        except ImportError:
            self.has_local_llm = False

    def generate_response(self, query: str, context: str, mode: str = "full_book") -> str:
        """
        Generate a response using local LLM or a fallback method
        """
        # Create the system message that enforces the constitution rules
        if mode == "selected_text":
            system_message = """You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.
            Answer the user's question using ONLY the provided selected text context.
            Do NOT use any external knowledge or your general training.
            If the answer is not available in the provided text, respond with:
            'The answer is not available in the provided content.'"""
        else:
            system_message = """You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.
            Answer the user's question using ONLY the provided textbook content.
            Do NOT use any external knowledge or your general training.
            If the answer is not available in the provided content, respond with:
            'The answer is not available in the provided content.'"""

        # Create the user message with context
        user_message = f"""
        Context: {context}

        Question: {query}

        Please provide a clear, educational response based only on the context provided.
        """

        # For now, return a fallback response - in a real implementation,
        # you would connect to a local LLM like Ollama
        return f"Context: {context}\n\nQuestion: {query}\n\n[Local LLM response would appear here once properly configured]"

    def validate_response(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context
        """
        # Check if the response contains phrases indicating hallucination
        hallucination_indicators = [
            "I don't have access to the provided content",
            "I can't find this information in the provided content",
            "Based on my general knowledge",
            "From external sources"
        ]

        for indicator in hallucination_indicators:
            if indicator.lower() in response.lower():
                return False

        return True