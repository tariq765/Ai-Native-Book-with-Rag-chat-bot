from llm_service import LLMService
import os

def test_llm_service():
    print("Testing LLM service...")

    # Check if environment variables are set
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    print(f"OPENROUTER_API_KEY is {'set' if openrouter_key else 'not set'}")

    if not openrouter_key or openrouter_key == "your_openrouter_api_key_here":
        print("Using mock response since no actual API key is provided")
        # Test the function with a mock approach
        llm_service = LLMService()

        # Test the validation function
        test_context = "Physical AI is a field that combines artificial intelligence with physical systems."
        test_response = "Based on the provided context, Physical AI is a field that combines artificial intelligence with physical systems."
        is_valid = llm_service.validate_response(test_response, test_context)
        print(f"Response validation result: {is_valid}")

        # Test with a hallucinated response
        hallucinated_response = "Based on my general knowledge, Physical AI is a field that..."
        is_valid_hallucination = llm_service.validate_response(hallucinated_response, test_context)
        print(f"Hallucination detection result: {is_valid_hallucination}")

        print("LLM service test completed!")
    else:
        print("Environment variables are properly set, ready for actual API calls")

if __name__ == "__main__":
    test_llm_service()