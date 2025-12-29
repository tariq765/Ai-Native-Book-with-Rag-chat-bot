import asyncio
from document_service import DocumentService

def test_ingestion():
    print("Testing document ingestion...")

    # Create document service instance
    doc_service = DocumentService()

    # Test reading documents
    print("Reading documents from physical-ai-humanoid-robotics-ts/docs...")
    documents = doc_service.read_documents_from_directory("../physical-ai-humanoid-robotics-ts/docs")

    print(f"Found {len(documents)} documents")

    # Show first few documents
    for i, doc in enumerate(documents[:3]):
        print(f"Document {i+1}: {doc['source']}")
        print(f"  Size: {doc['metadata']['size']} characters")
        print(f"  Content preview: {doc['text'][:100]}...")
        print()

    # Test chunking
    if documents:
        print("Testing chunking on first document...")
        first_doc_text = documents[0]['text']
        chunks = doc_service.chunk_text(first_doc_text)

        print(f"Original text length: {len(first_doc_text)}")
        print(f"Number of chunks created: {len(chunks)}")

        if chunks:
            print(f"First chunk length: {len(chunks[0])}")
            print(f"First chunk preview: {chunks[0][:100]}...")

    print("Ingestion test completed successfully!")

if __name__ == "__main__":
    test_ingestion()