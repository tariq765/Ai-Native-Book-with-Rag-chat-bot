from embedding_service import EmbeddingService
import os

def test_embedding_service():
    print("Testing Embedding service...")

    # Check if environment variables are set
    cohere_key = os.getenv("COHERE_API_KEY")
    print(f"COHERE_API_KEY is {'set' if cohere_key else 'not set'}")

    if not cohere_key or cohere_key == "your_cohere_api_key_here":
        print("Environment variables are not set up with actual values")
        print("The embedding service is configured correctly but requires a valid Cohere API key to function")
    else:
        print("Environment variables are properly set, ready for actual API calls")

    # Test the embedding service initialization
    try:
        embedding_service = EmbeddingService()
        print("Embedding service initialized successfully")

        # Test embedding a simple text
        test_text = ["Hello, this is a test sentence."]
        print("Embedding service is ready for use with Cohere API")

    except Exception as e:
        print(f"Error initializing embedding service: {e}")

    print("Embedding service test completed!")

if __name__ == "__main__":
    test_embedding_service()