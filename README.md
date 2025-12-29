# Physical AI & Humanoid Robotics RAG Chatbot

This is a Retrieval-Augmented Generation (RAG) chatbot for the Physical AI & Humanoid Robotics textbook. The system integrates:

- **Cohere** for embeddings
- **Qdrant** for vector storage
- **OpenRouter** for LLM reasoning
- **FastAPI** for backend services
- **Docusaurus** for frontend integration

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Docusaurus    │◄──►│   FastAPI       │◄──►│   Vector DB     │
│   Frontend      │    │   Backend       │    │   (Qdrant)      │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ Chatbot   │  │    │  │ Embedding │  │    │  │ Document  │  │
│  │ Component │◄─┼────┼──┤ Service   │◄─┼────┼──┤ Chunks    │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    │  ┌───────────┐  │    │  ┌───────────┐  │
                       │  │ LLM       │  │    │  │ Embeddings│  │
                       │  │ Service   │◄─┼────┼──┤           │  │
                       │  └───────────┘  │    │  └───────────┘  │
                       └─────────────────┘    └─────────────────┘
```

## Features

- **Document-based Q&A**: Answers questions based on the Physical AI & Humanoid Robotics textbook
- **Selected-text mode**: Answers questions based only on user-selected text
- **Context enforcement**: Strictly follows the constitution to avoid hallucination
- **Source citations**: References specific documents when possible

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get API keys for the required services:
   - **Cohere API Key**: Sign up at [cohere.com](https://cohere.com) and get your API key
   - **Qdrant Cloud**: Create an account at [qdrant.tech](https://qdrant.tech) or use a local instance
   - **OpenRouter API Key**: Sign up at [openrouter.ai](https://openrouter.ai) and get your API key

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

5. Ingest the textbook documents:
   ```bash
   curl -X POST http://localhost:8000/ingest
   ```

6. Start chatting:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Physical AI?", "selected_text": null}'
   ```

## API Endpoints

- `GET /` - Health check
- `POST /chat` - Main chat endpoint
- `POST /chat-with-selection` - Chat with selected text only
- `POST /ingest` - Ingest textbook documents

## Constitution Compliance

This chatbot strictly follows the constitution.md rules:
- Answers only from provided context
- Never uses external knowledge
- Says "The answer is not available in the provided content" when information is not found
- Prioritizes truth over fluency

## Frontend Integration

The chatbot is integrated into the Docusaurus site via a React component that:
- Appears as a floating chat button
- Detects text selection on the page
- Allows users to ask questions about selected text
- Maintains conversation history