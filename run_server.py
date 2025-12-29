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
    load_dotenv()  # Load .env file
    load_dotenv('.env.local')  # Load .env.local file (overrides .env if present)

    # Check if environment variables are set (not placeholder values)
    cohere_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    print("Checking environment variables...")

    cohere_set = cohere_key and cohere_key != 'your_actual_cohere_api_key_here'
    qdrant_url_set = qdrant_url and qdrant_url != 'https://your-cluster-url.qdrant.tech'
    qdrant_api_set = qdrant_api_key and qdrant_api_key != 'your_actual_qdrant_api_key_here'
    openrouter_set = openrouter_key and openrouter_key != 'your_actual_openrouter_api_key_here'

    print(f"COHERE_API_KEY set: {'Yes' if cohere_set else 'No'}")
    print(f"QDRANT_URL set: {'Yes' if qdrant_url_set else 'No'}")
    print(f"QDRANT_API_KEY set: {'Yes' if qdrant_api_set else 'No'}")
    print(f"OPENROUTER_API_KEY set: {'Yes' if openrouter_set else 'No'}")

    if not all([cohere_set, qdrant_url_set, qdrant_api_set, openrouter_set]):
        print("\nWarning: Some environment variables are still using placeholder values!")
        print("Please update your .env file with actual API keys before running the server.")
        print("\nYou need to get API keys from:")
        print("- Cohere: https://dashboard.cohere.com/")
        print("- Qdrant: https://qdrant.tech/ (or use a local instance)")
        print("- OpenRouter: https://openrouter.ai/")
        print("\nAfter getting your API keys, edit the .env file and replace the placeholder values.")
        return

    print("\nAll environment variables are properly set!")
    print("Starting the RAG chatbot backend server on http://localhost:8000")
    print("Press Ctrl+C to stop the server")

    # Run the server
    try:
        # Use uvicorn to run the FastAPI app
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting the server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped by user.")

if __name__ == "__main__":
    main()