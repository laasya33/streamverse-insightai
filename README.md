# 🎬 StreamVerse InsightAI

A secure AI-powered internal analytics assistant for StreamVerse Entertainment, built for the Futures First Quantitative Engineer assessment.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
│              React Frontend :3000                        │
│   Chat UI │ Charts │ Tool Trace │ Suggested Questions   │
└────────────────────┬────────────────────────────────────┘
│ HTTP REST + X-API-Key Header
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend :8000                       │
│                                                          │
│  POST /api/chat/          GET /api/analytics/*          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │           AI Orchestration Layer                 │   │
│  │            (Groq LLaMA + Tool Calling)           │   │
│  └──────┬──────────────┬──────────────┬────────────┘   │
│         │              │              │                  │
│  ┌──────▼──────┐ ┌────▼─────┐ ┌────▼──────┐          │
│  │  SQL Tool   │ │ PDF Tool │ │ CSV Tool  │          │
│  │  (SQLite)   │ │(pdfplumb)│ │ (pandas)  │          │
│  └──────┬──────┘ └────┬─────┘ └────┬──────┘          │
│         │              │              │                  │
│  ┌──────▼──────┐ ┌────▼──────┐ ┌──▼────────────┐    │
│  │  SQLite DB  │ │ PDF Docs  │ │   CSV Files   │    │
│  │  (6 tables) │ │ (5 files) │ │   (6 files)   │    │
│  └─────────────┘ └───────────┘ └───────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Recharts |
| Backend | Python 3.11, FastAPI |
| AI Model | Groq LLaMA 3.1 (llama-3.1-8b-instant) |
| Database | SQLite (via pandas ingestion) |
| PDF Search | pdfplumber |
| CSV Analysis | pandas |
| Containerization | Docker + Docker Compose |

---

## Quick Start (Docker — Recommended)

### Prerequisites
- Docker Desktop installed
- Groq API key ([get one here](https://console.groq.com))

### Steps

```bash
# 1. Clone / unzip the project
cd streamverse-insightai

# 2. Create your .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and API_SECRET_KEY

# 3. Run everything
docker-compose up --build

# 4. Open browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## Quick Start (Manual — No Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set your API keys
cp .env.example .env
# Edit .env:
#   GROQ_API_KEY=gsk-...
#   API_SECRET_KEY=your-secret-key-here

# Run server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Set API URL and key
cp .env.example .env
# Edit .env:
#   REACT_APP_API_URL=http://localhost:8000
#   REACT_APP_API_SECRET_KEY=your-secret-key-here

# Run frontend
npm start
```

Open http://localhost:3000

---

## Environment Variables

### Backend `.env`
GROQ_API_KEY=gsk-...
API_SECRET_KEY=your-secret-key-here

### Frontend `.env`
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_SECRET_KEY=your-secret-key-here

> ⚠️ Both `API_SECRET_KEY` and `REACT_APP_API_SECRET_KEY` must be the same value.

---

## Example Questions to Try

| Question | Sources Used |
|----------|-------------|
| Which titles performed best in 2025? | SQL + CSV |
| Why is Stellar Run trending recently? | SQL + PDF |
| Compare Dark Orbit vs Last Kingdom | SQL + CSV |
| Which city had the strongest engagement? | SQL + CSV |
| What explains weak comedy performance? | SQL + PDF |
| What recommendations for leadership? | PDF + SQL |

---

## Project Structure
streamverse-insightai/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── database.py              # SQLite init and query runner
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routers/
│   │   ├── chat.py              # POST /api/chat/
│   │   └── analytics.py        # GET /api/analytics/*
│   ├── tools/
│   │   ├── sql_tool.py          # SQL query tool definition
│   │   ├── pdf_tool.py          # PDF search tool definition
│   │   └── csv_tool.py          # CSV analysis tool definition
│   ├── services/
│   │   └── ai_service.py        # Groq orchestration + tool loop
│   └── data/
│       ├── movies.csv
│       ├── viewers.csv
│       ├── watch_activity.csv
│       ├── reviews.csv
│       ├── marketing_spend.csv
│       ├── regional_performance.csv
│       └── pdfs/
│           ├── quarterly_executive_report.pdf
│           ├── campaign_performance_summary.pdf
│           ├── content_roadmap.pdf
│           ├── policy_guidelines.pdf
│           └── audience_behavior_report.pdf
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   ├── public/index.html
│   └── src/
│       ├── App.jsx              # Main layout
│       ├── index.js
│       ├── components/
│       │   ├── ChatMessage.jsx  # Message bubble + tool trace
│       │   ├── ChatInput.jsx    # Input bar + suggested questions
│       │   └── Charts.jsx       # Analytics dashboard
│       └── hooks/
│           └── useChat.js       # Chat state + API calls
├── docker-compose.yml
├── .env.example
└── README.md

---

## Security Design

- **API key authentication**: All requests to `/api/chat/` require a valid `X-API-Key` header. Invalid or missing keys are rejected with `403 Forbidden`
- **No raw data exposure**: All data access goes through typed tool functions
- **SQL injection prevention**: Only SELECT queries allowed; forbidden keywords (DROP, INSERT, DELETE, UPDATE) are blocked
- **PII protection**: Viewer IDs are never passed to the AI model directly
- **Secret management**: API keys stored in `.env` files, never hardcoded in source code
- **CORS**: Restricted to known frontend origins only
- **Input validation**: Pydantic models validate and sanitize all API inputs

---

## Assumptions & Tradeoffs

| Assumption | Rationale |
|-----------|-----------|
| SQLite over PostgreSQL | Simpler setup for demo; easily swappable for production |
| All CSV data loaded at startup | Acceptable for demo scale; production would use streaming ingestion |
| API key auth over JWT | Sufficient for internal tool; JWT would be added for multi-user production system |
| pdfplumber keyword search over vector embeddings | Faster setup; embeddings (e.g. ChromaDB) would improve semantic search quality |
| Single-user system | Multi-tenancy not required per task brief |
| Groq LLaMA over GPT-4 | Faster inference and free tier available; easily swappable via one config line |

---

## API Reference

| Endpoint | Method | Auth Required | Description |
|----------|--------|--------------|-------------|
| `/` | GET | ❌ | Health check |
| `/api/chat/` | POST | ✅ X-API-Key | Send a question, get AI answer |
| `/api/analytics/top-titles` | GET | ❌ | Top titles by views |
| `/api/analytics/genre-performance` | GET | ❌ | Genre metrics |
| `/api/analytics/city-engagement` | GET | ❌ | City engagement data |
| `/api/analytics/platform-stats` | GET | ❌ | Platform breakdown |
| `/api/analytics/marketing-roi` | GET | ❌ | Marketing channel ROI |
| `/docs` | GET | ❌ | Interactive API documentation |