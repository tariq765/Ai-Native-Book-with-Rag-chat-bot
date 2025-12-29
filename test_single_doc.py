import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_service import DocumentService
from qdrant_service import QdrantService
from embedding_service import EmbeddingService

# Test with just a single document to see if it works
try:
    print("Testing with a single document...")

    # Create services
    embedding_service = EmbeddingService()
    qdrant_service = QdrantService()

    # Create a simple test document
    test_doc = {
        'id': 'test_doc_1',
        'text': 'This is a test document about Physical AI and Humanoid Robotics. The textbook covers advanced robotics, machine learning applications in robotics, and humanoid robot development.',
        'source': 'test_document.md',
        'metadata': {
            'filename': 'test_document.md',
            'relative_path': 'test_document.md',
            'size': 100
        }
    }

    # Create collection
    qdrant_service.create_collection(vector_size=1024)

    # Generate embedding for the test document
    print("Generating embedding...")
    embedding = embedding_service.embed_texts([test_doc['text']])

    # Add embedding to document
    test_doc['embedding'] = embedding[0]

    # Upsert to Qdrant
    print("Upserting to Qdrant...")
    qdrant_service.upsert_documents([test_doc])

    print("Single document ingestion successful!")

    # Test search
    print("Testing search...")
    query_embedding = embedding_service.embed_query("What is this document about?")
    search_results = qdrant_service.search(query_vector=query_embedding, top_k=1)

    print(f"Search results: {len(search_results)} results found")
    if search_results:
        print(f"First result text: {search_results[0]['text'][:100]}...")

except Exception as e:
    print(f"Error during single document test: {e}")
    import traceback
    traceback.print_exc()