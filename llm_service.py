from openai import OpenAI
from typing import List, Dict, Any
from config import Config

class LLMService:
    def __init__(self):
        # Configure OpenRouter client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=Config.OPENROUTER_API_KEY
        )

    def generate_response(self, query: str, context: str, mode: str = "full_book") -> str:
        """
        Generate a response using the LLM with the provided context
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

        try:
            response = self.client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,  # Low temperature for more consistent, factual responses
                max_tokens=1000,
            )

            return response.choices[0].message.content

        except Exception as e:
            # If there's an error with the LLM, return a safe response
            print(f"LLM Error: {e}")
            return "The answer is not available in the provided content."

    def validate_response(self, response: str, context: str) -> bool:
        """
        Validate that the response is grounded in the provided context
        This is a basic implementation - in a real system, you might use more sophisticated validation
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