"""
Test script to demonstrate the RAG chatbot system functionality
This script shows how the different components work together
"""
import asyncio
import json
from typing import Dict, Any

# Mock implementations to demonstrate the system without external dependencies
class MockEmbeddingService:
    def __init__(self):
        print("Mock Embedding Service initialized")

    def embed_texts(self, texts, input_type="search_document"):
        # Return mock embeddings
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, query):
        return [0.1, 0.2, 0.3]  # Mock embedding

class MockQdrantService:
    def __init__(self):
        print("Mock Qdrant Service initialized")
        # Mock document database
        self.documents = [
            {
                "id": "1",
                "text": "Physical AI represents the convergence of artificial intelligence and robotics, where intelligent systems operate in the real, three-dimensional world. Unlike traditional AI that processes data on screens, Physical AI systems must handle the complexities of physics, uncertainty, and real-time constraints.",
                "source": "intro.md",
                "metadata": {"chapter": "Introduction", "section": "What is Physical AI"}
            },
            {
                "id": "2",
                "text": "Humanoid robots are machines designed with human-like form and capabilities. They leverage the advantages of human-like form for interaction in human environments. Humanoid robots can navigate spaces designed for humans, use tools designed for human hands, and communicate more naturally with people.",
                "source": "intro.md",
                "metadata": {"chapter": "Introduction", "section": "Why Humanoid Robots"}
            },
            {
                "id": "3",
                "text": "The Robot Operating System (ROS 2) serves as the middleware that allows different components of a robot to work together seamlessly. It provides the communication infrastructure for nodes, topics, services, and actions that enable robot communication.",
                "source": "module-1-ros2/intro.md",
                "metadata": {"chapter": "Module 1: ROS 2", "section": "Introduction"}
            }
        ]

    def create_collection(self, vector_size=1024):
        print(f"Mock collection created with vector size {vector_size}")

    def upsert_documents(self, documents):
        print(f"Mock upserted {len(documents)} documents")

    def search(self, query_vector, top_k=5):
        # In a real implementation, this would perform vector similarity search
        # For the mock, we'll return all documents
        print(f"Mock search performed with query vector, top_k={top_k}")
        return self.documents[:top_k]  # Return first top_k documents

class MockLLMService:
    def __init__(self):
        print("Mock LLM Service initialized")

    def generate_response(self, query, context, mode="full_book"):
        # In a real implementation, this would call the LLM
        # For the mock, we'll generate a simple response based on context
        print(f"Generating response for query: '{query[:30]}...' using {mode} mode")

        if "not available" in context.lower() or len(context) < 10:
            return "The answer is not available in the provided content."

        # Simple keyword matching for demonstration
        if "physical ai" in query.lower():
            return "Physical AI represents the convergence of artificial intelligence and robotics, where intelligent systems operate in the real, three-dimensional world. Unlike traditional AI that processes data on screens, Physical AI systems must handle the complexities of physics, uncertainty, and real-time constraints."

        if "humanoid robot" in query.lower():
            return "Humanoid robots are machines designed with human-like form and capabilities. They leverage the advantages of human-like form for interaction in human environments. Humanoid robots can navigate spaces designed for humans, use tools designed for human hands, and communicate more naturally with people."

        if "ros 2" in query.lower():
            return "The Robot Operating System (ROS 2) serves as the middleware that allows different components of a robot to work together seamlessly. It provides the communication infrastructure for nodes, topics, services, and actions that enable robot communication."

        # Default response
        return f"Based on the provided context, I can tell you that: {context[:200]}..."

def demonstrate_system():
    print("=== Physical AI & Humanoid Robotics RAG Chatbot System Demo ===\n")

    # Initialize mock services
    print("1. Initializing services...")
    embedding_service = MockEmbeddingService()
    qdrant_service = MockQdrantService()
    llm_service = MockLLMService()

    print("\n2. Demonstrating document ingestion...")
    qdrant_service.create_collection()
    qdrant_service.upsert_documents(qdrant_service.documents)

    print("\n3. Demonstrating chat functionality...")

    # Test query 1: Full book mode
    print("\n--- Test 1: Full Book Mode ---")
    query1 = "What is Physical AI?"
    print(f"User query: {query1}")

    # In real system: embed query, search Qdrant, get context
    query_embedding = embedding_service.embed_query(query1)
    search_results = qdrant_service.search(query_embedding, top_k=3)

    context_parts = []
    sources = []
    for result in search_results:
        context_parts.append(result['text'])
        if result['source'] not in sources:
            sources.append(result['source'])

    context = "\n\n".join(context_parts)
    print(f"Retrieved context from {len(sources)} sources")

    response1 = llm_service.generate_response(query1, context, mode="full_book")
    print(f"Assistant response: {response1}")

    # Test query 2: Selected text mode
    print("\n--- Test 2: Selected Text Mode ---")
    selected_text = "Humanoid robots are machines designed with human-like form and capabilities. They leverage the advantages of human-like form for interaction in human environments."
    query2 = "Why are humanoid robots designed with human-like form?"
    print(f"Selected text: {selected_text}")
    print(f"User query: {query2}")

    response2 = llm_service.generate_response(query2, selected_text, mode="selected_text")
    print(f"Assistant response: {response2}")

    # Test query 3: No context available
    print("\n--- Test 3: No Context Available ---")
    query3 = "What is the weather today?"
    print(f"User query: {query3}")

    response3 = llm_service.generate_response(query3, "not available", mode="full_book")
    print(f"Assistant response: {response3}")

    print("\n=== Demo Complete ===")
    print("\nThis demonstration shows how the RAG system would work:")
    print("- Embedding service converts text to vectors")
    print("- Qdrant service stores and retrieves relevant documents")
    print("- LLM service generates responses based on context")
    print("- The system follows the constitution by avoiding hallucination")

if __name__ == "__main__":
    demonstrate_system()