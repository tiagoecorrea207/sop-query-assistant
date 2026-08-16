# Pharmaceutical SOP Query Assistant — Project 1

RAG-powered Q&A system over pharmaceutical SOPs and audit criteria documents.
Upload an audit criteria PDF, query the loaded SOPs, accumulate results, export to PDF.

## Stack

- FastAPI + Python 3.12
- LangChain (RetrievalQA · stuff chain)
- Claude (Anthropic) inference + HuggingFace `all-MiniLM-L6-v2` (embeddings)
- PostgreSQL + pgvector (vector store)
- LangSmith (tracing)
- React + TypeScript (frontend)
- WeasyPrint (PDF export)

## Architecture

```
React Frontend (:3000)
      │  REST + WebSocket
FastAPI Backend (:8000)
      │
      ├── Ingestion pipeline
      │     ├── 20 SOPs (.docx) — loaded at startup
      │     ├── Audit criteria — uploaded per session
      │     └── Web SOPs — fetched on demand
      │
      ├── RAG chain
      │     ├── Query → embedding → pgvector cosine search
      │     ├── Top-6 chunks → stuffed into prompt
      │     └── Claude inference → cited answer
      │
      └── PDF export (WeasyPrint)

PostgreSQL + pgvector (:5432)
```

## Quickstart

```bash
cp backend/.env.example backend/.env
# Fill in ANTHROPIC_API_KEY and LANGCHAIN_API_KEY

docker-compose up --build

# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

## Manual (no Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m db.seed

 main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## API endpoints

| Method | Path              | Purpose                          |
|--------|-------------------|----------------------------------|
| GET    | /health           | Backend status + chunk count     |
| POST   | /ingest-audit     | Upload audit criteria doc        |
| WS     | /query            | Streaming query (WebSocket)      |
| POST   | /export-pdf       | Export session to PDF            |
| POST   | /ingest-web-sop   | Add web SOP by URL               |

## Failure modes handled

1. Question out of context — similarity threshold guard before LLM call
2. Answer not found — prompt instructs NOT_FOUND response
3. Audit file not valid — LLM classifier at ingestion time
4. SOP file not valid — structural signal check at startup
5. Web SOP unreachable — httpx error handling, query continues
