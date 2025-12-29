import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Cohere Configuration
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

    # Qdrant Configuration
    QDRANT_URL = os.getenv("QDRANT_URL")  # Cloud instance URL
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # Cloud instance API key
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "physical_ai_robobook")

    # Local Qdrant Configuration (fallback when cloud is unavailable)
    LOCAL_QDRANT_PATH = os.getenv("LOCAL_QDRANT_PATH", "./local_qdrant_data")

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

    # Application Configuration
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))

    # Document processing
    CHUNK_SIZE = 500  # tokens
    OVERLAP_SIZE = 50  # tokens
    TOP_K = 5  # number of chunks to retrieve

    # Validation
    @classmethod
    def validate(cls):
        required_vars = [
            'COHERE_API_KEY',
            'QDRANT_URL',
            'QDRANT_API_KEY',
            'OPENROUTER_API_KEY'
        ]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on import
Config.validate()