from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from config import Config
from document_service import DocumentService
from embedding_service import EmbeddingService
from qdrant_service import QdrantService
from llm_service import LLMService

# Load environment variables
load_dotenv()  # Load .env file
load_dotenv('.env.local')  # Load .env.local file (overrides .env if present)

app = FastAPI(
    title="Physical AI & Humanoid Robotics RAG Chatbot",
    description="A retrieval-augmented generation chatbot for the Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_service = DocumentService()
embedding_service = EmbeddingService()
qdrant_service = QdrantService()
llm_service = LLMService()

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
    return {"message": "Physical AI & Humanoid Robotics RAG Chatbot API"}

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
        else:
            mode = "full_book"
            # Perform vector search to retrieve relevant context
            query_embedding = embedding_service.embed_query(request.message)
            search_results = qdrant_service.search(
                query_vector=query_embedding,
                top_k=Config.TOP_K
            )

            # Combine the retrieved texts as context
            context_parts = []
            sources = []
            for result in search_results:
                context_parts.append(result['text'])
                if result['source'] not in sources:
                    sources.append(result['source'])

            context = "\n\n".join(context_parts)

        # Generate response using LLM with the context
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

        # Ingest documents from the textbook
        result = document_service.ingest_documents(textbook_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)