#!/usr/bin/env python3
"""
Script to run the RAG chatbot backend server
"""
import os
import subprocess
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Check if environment variables are set
    cohere_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    print("Checking environment variables...")
    print(f"COHERE_API_KEY set: {'Yes' if cohere_key and cohere_key != 'your_cohere_api_key_here' else 'No'}")
    print(f"QDRANT_URL set: {'Yes' if qdrant_url and qdrant_url != 'your_qdrant_url_here' else 'No'}")
    print(f"QDRANT_API_KEY set: {'Yes' if qdrant_api_key and qdrant_api_key != 'your_qdrant_api_key_here' else 'No'}")
    print(f"OPENROUTER_API_KEY set: {'Yes' if openrouter_key and openrouter_key != 'your_openrouter_api_key_here' else 'No'}")

    if not all([
        cohere_key and cohere_key != 'your_cohere_api_key_here',
        qdrant_url and qdrant_url != 'your_qdrant_url_here',
        qdrant_api_key and qdrant_api_key != 'your_qdrant_api_key_here',
        openrouter_key and openrouter_key != 'your_openrouter_api_key_here'
    ]):
        print("\n⚠️  Warning: Some environment variables are still using placeholder values!")
        print("Please update your .env file with actual API keys before running the server.")
        print("\nTo update the .env file:")
        print("1. Edit rag_backend/.env")
        print("2. Replace 'your_cohere_api_key_here' with your actual Cohere API key")
        print("3. Replace 'your_qdrant_url_here' with your actual Qdrant URL")
        print("4. Replace 'your_qdrant_api_key_here' with your actual Qdrant API key")
        print("5. Replace 'your_openrouter_api_key_here' with your actual OpenRouter API key")
        print("\nAfter updating, run this script again.")
        return

    print("\n✅ All environment variables are properly set!")
    print("Starting the RAG chatbot backend server...")

    # Run the server
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped by user.")

if __name__ == "__main__":
    main()