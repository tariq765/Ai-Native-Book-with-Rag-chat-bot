from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG Chatbot",
    description="A retrieval-augmented generation chatbot for the Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# Mock services for testing without API keys
class MockEmbeddingService:
    def __init__(self):
        pass

    def embed_texts(self, texts, input_type="search_document"):
        # Return mock embeddings
        return [[0.1, 0.2, 0.3] for _ in texts]

    def embed_query(self, query):
        return [0.1, 0.2, 0.3]  # Mock embedding

class MockQdrantService:
    def __init__(self):
        # Mock document database with sample textbook content
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
        # For the mock, return relevant documents based on simple keyword matching
        return self.documents[:top_k]  # Return first top_k documents

class MockLLMService:
    def __init__(self):
        pass

    def generate_response(self, query, context, mode="full_book"):
        # Generate a response based on the context
        if "not available" in context.lower() or len(context) < 10:
            return "The answer is not available in the provided content."

        # Simple keyword matching for demonstration
        query_lower = query.lower()
        if "physical ai" in query_lower:
            return "Physical AI represents the convergence of artificial intelligence and robotics, where intelligent systems operate in the real, three-dimensional world. Unlike traditional AI that processes data on screens, Physical AI systems must handle the complexities of physics, uncertainty, and real-time constraints."

        if "humanoid robot" in query_lower or "humanoid" in query_lower:
            return "Humanoid robots are machines designed with human-like form and capabilities. They leverage the advantages of human-like form for interaction in human environments. Humanoid robots can navigate spaces designed for humans, use tools designed for human hands, and communicate more naturally with people."

        if "ros" in query_lower or "robot operating system" in query_lower:
            return "The Robot Operating System (ROS 2) serves as the middleware that allows different components of a robot to work together seamlessly. It provides the communication infrastructure for nodes, topics, services, and actions that enable robot communication."

        # Default response based on context
        return f"Based on the provided context: {context[:200]}... [This is a simulated response based on the textbook content]"

# Initialize mock services
embedding_service = MockEmbeddingService()
qdrant_service = MockQdrantService()
llm_service = MockLLMService()

class MockDocumentService:
    def __init__(self):
        pass

    def read_documents_from_directory(self, directory_path):
        # Return mock documents
        return [
            {
                'id': 'test_doc_1',
                'text': 'Physical AI represents the convergence of artificial intelligence and robotics...',
                'source': 'intro.md',
                'metadata': {'filename': 'intro.md', 'relative_path': 'intro.md', 'size': 100}
            }
        ]

    def chunk_text(self, text, chunk_size=500, overlap=50):
        # Simple chunking
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def ingest_documents(self, documents_directory):
        # Mock ingestion
        return {
            'status': 'success',
            'documents_processed': 1,
            'chunks_created': 2,
            'collection_name': 'mock_collection'
        }

document_service = MockDocumentService()

# Request/Response models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    selected_text: Optional[str] = None  # For selected text mode
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    mode: str  # "full_book" or "selected_text"

@app.get("/")
async def root():
    return {"message": "Physical AI & Humanoid Robotics RAG Chatbot API - Running with mock services"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that handles both full-book and selected-text modes
    """
    try:
        # Determine mode based on selected_text
        if request.selected_text:
            mode = "selected_text"
            context = request.selected_text
            sources = []
        else:
            mode = "full_book"
            # Perform mock search to retrieve relevant context
            query_embedding = embedding_service.embed_query(request.message)
            search_results = qdrant_service.search(
                query_vector=query_embedding,
                top_k=3
            )

            # Combine the retrieved texts as context
            context_parts = []
            sources = []
            for result in search_results:
                context_parts.append(result['text'])
                if result['source'] not in sources:
                    sources.append(result['source'])

            context = "\n\n".join(context_parts)

        # Generate response using mock LLM with the context
        response = llm_service.generate_response(
            query=request.message,
            context=context,
            mode=mode
        )

        return ChatResponse(
            response=response,
            sources=sources if mode == "full_book" else [],
            mode=mode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-with-selection", response_model=ChatResponse)
async def chat_with_selection(request: ChatRequest):
    """
    Chat endpoint specifically for selected text mode
    """
    if not request.selected_text:
        raise HTTPException(status_code=400, detail="selected_text is required for this endpoint")

    try:
        # Process using only the selected text
        response = llm_service.generate_response(
            query=request.message,
            context=request.selected_text,
            mode="selected_text"
        )

        return ChatResponse(
            response=response,
            sources=[],
            mode="selected_text"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_documents():
    """
    Endpoint to ingest textbook documents into the vector database
    """
    try:
        # Get the path to the textbook documents
        textbook_path = "../physical-ai-humanoid-robotics-ts/docs"

        # Mock ingestion of documents from the textbook
        result = document_service.ingest_documents(textbook_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)