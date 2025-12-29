import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_service import DocumentService

# Actually ingest documents
try:
    print("Starting document ingestion...")
    document_service = DocumentService()

    # Get the path to the textbook documents
    textbook_path = "../physical-ai-humanoid-robotics-ts/docs"

    print(f"Ingesting documents from: {textbook_path}")

    # Ingest documents from the textbook
    result = document_service.ingest_documents(textbook_path)

    print("Ingestion result:", result)

except Exception as e:
    print(f"Error during ingestion: {e}")
    import traceback
    traceback.print_exc()