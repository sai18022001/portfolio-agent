# AI Portfolio Research Agent

![CI](https://github.com/sai18022001/portfolio-agent/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![LangChain](https://img.shields.io/badge/LangChain-agent-green)
![Docker](https://img.shields.io/badge/Docker-containerized-blue)

An LLM-powered financial research agent that answers complex portfolio queries by reasoning over **live market data** and **financial documents** (10-Ks, earnings reports). Built with a multi-step reasoning architecture — the agent decides which tools to call, combines results, and synthesizes answers with source citations.

---

## Demo

> "Given Apple's current stock price and their 10-K risk factors, assess their risk profile."

The agent autonomously:
1. Calls the **RAG tool** → retrieves relevant chunks from Apple's 2025 10-K
2. Calls the **stock data tool** → fetches live AAPL price from Alpha Vantage
3. Synthesizes both into a structured risk assessment

---

## Key Metrics

| Metric | Value |
|---|---|
| RAG retrieval accuracy | 100% (6/6 company-specific queries) |
| PDF chunks indexed | 2,827 across 3 annual reports |
| Embedding speed | 826 embeddings/sec (all-MiniLM-L6-v2) |
| Vector dimensions | 384 per chunk |
| API response time | ~4s (stock) / ~10s (RAG + reasoning) |
| REST endpoints | 4 |
| Companies covered | Apple, Microsoft, Tesla (10-Ks) |

---

## Architecture

```
User → React Chat UI
         ↓
    FastAPI Backend (/chat, /session, /history)
         ↓
    LangChain Agent (Gemini)
         ├── RAG Tool
         │     └── Query embedding → cosine similarity → MongoDB
         │           └── 2,827 chunks from 3 financial PDFs
         └── Stock Tool
               └── Alpha Vantage API → real-time price + volume
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash |
| Agent framework | LangChain `AgentExecutor` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector search | Cosine similarity over MongoDB |
| Document store | MongoDB (chunks + conversation memory) |
| Stock data | Alpha Vantage API |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Vite |
| Containerization | Docker + docker-compose |
| CI | GitHub Actions (lint + tests + build) |

---

## Features

- **Multi-step reasoning** — agent decides which tools to call based on query intent
- **RAG pipeline** — semantic search over 2,827 PDF chunks with 100% retrieval accuracy on company-specific queries
- **Live market data** — real-time stock price, volume, and daily change via Alpha Vantage
- **Persistent memory** — conversation history stored in MongoDB, enabling follow-up questions across sessions
- **REST API** — 4 FastAPI endpoints with auto-generated Swagger docs
- **CI pipeline** — automated lint, tests, and frontend build on every push

---

## Quick Start

### Prerequisites
- Docker Desktop
- Gemini API key → [aistudio.google.com](https://aistudio.google.com)
- Alpha Vantage API key → [alphavantage.co](https://www.alphavantage.co/support/#api-key)

### Run with Docker

```bash
git clone https://github.com/sai18022001/portfolio-agent
cd portfolio-agent

# Fill in your API keys in .env

docker-compose up --build
```

Then ingest your PDFs into the Docker MongoDB:
```bash
docker exec -it portfolio_backend python rag/ingest.py
```

Open:
- Chat UI → http://localhost:5173
- API docs → http://localhost:8000/docs

### Run without Docker

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python rag/ingest.py         # ingest PDFs first
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
portfolio-agent/
├── backend/
│   ├── agent/
│   │   ├── agent.py        # LangChain AgentExecutor + Gemini
│   │   ├── tools.py        # RAG tool + stock data tool
│   │   └── memory.py       # MongoDB conversation memory
│   ├── rag/
│   │   ├── ingest.py       # PDF → chunks → embeddings → MongoDB
│   │   └── retriever.py    # cosine similarity semantic search
│   ├── db/
│   │   └── mongo.py        # MongoDB connection
│   ├── tests/
│   │   ├── test_api.py     # FastAPI endpoint tests
│   │   └── test_tools.py   # tool unit tests
│   └── main.py             # FastAPI app (4 endpoints)
├── frontend/
│   └── src/
│       └── App.jsx         # React chat UI
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── docker-compose.yml
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | Send message, get agent response |
| DELETE | `/session/{id}` | Clear conversation history |
| GET | `/session/{id}/history` | Retrieve past messages |

### Example request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are Apple main risks?", "session_id": "demo-001"}'
```

---

## Sample Queries

- *"What are Apple's main business risks according to their 2025 10-K?"*
- *"What is AAPL's current stock price and daily performance?"*
- *"Given Apple's risks and current price, what is their risk profile?"*
- *"What did Microsoft say about AI strategy in their annual report?"*
- *"Compare Tesla and Apple's supply chain risks"*

---

## Environment Variables

```bash
GEMINI_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
MONGODB_URI=mongodb://localhost:27017
DB_NAME=portfolio_agent
```

---

## How RAG Works

1. **Ingestion** — PDFs are split into 500-character overlapping chunks, embedded using `all-MiniLM-L6-v2` (384 dimensions), and stored in MongoDB
2. **Retrieval** — user query is embedded, cosine similarity is computed against all stored chunks, top-4 most relevant chunks are returned
3. **Generation** — retrieved chunks are injected into the Gemini prompt as context, grounding the answer in real document content

---

*Built as a portfolio project demonstrating LLM agent architecture, RAG pipelines, and full-stack deployment.*