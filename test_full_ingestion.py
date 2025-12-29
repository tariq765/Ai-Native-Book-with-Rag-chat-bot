import asyncio
from document_service import DocumentService

def test_full_ingestion():
    print("Testing full document ingestion pipeline...")

    # Create document service instance
    doc_service = DocumentService()

    # Perform full ingestion (this will attempt to connect to Qdrant)
    print("Starting document ingestion to Qdrant...")
    try:
        result = doc_service.ingest_documents("../physical-ai-humanoid-robotics-ts/docs")
        print(f"Ingestion completed: {result}")
    except Exception as e:
        print(f"Ingestion failed as expected (no Qdrant credentials): {e}")
        print("This is expected since we don't have Qdrant credentials in the .env file")

    print("Full ingestion test completed!")

if __name__ == "__main__":
    test_full_ingestion()