from qdrant_client import QdrantClient
from config import Config

# Test Qdrant connection
try:
    print("Attempting to connect to Qdrant...")
    client = QdrantClient(
        url=Config.QDRANT_URL,
        api_key=Config.QDRANT_API_KEY,
    )

    print("Connected to Qdrant successfully!")

    # Try to get collection info
    try:
        collection_info = client.get_collection(Config.QDRANT_COLLECTION_NAME)
        print(f"Collection '{Config.QDRANT_COLLECTION_NAME}' exists!")
        print(f"Points in collection: {collection_info.points_count}")
    except Exception as e:
        print(f"Collection '{Config.QDRANT_COLLECTION_NAME}' does not exist or error occurred: {e}")

except Exception as e:
    print(f"Failed to connect to Qdrant: {e}")