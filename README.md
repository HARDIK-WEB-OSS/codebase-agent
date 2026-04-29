# Codebase Onboarding Agent

> Ingest any GitHub repository. Ask questions. Get answers with exact file paths and line references.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## The Problem

New developers waste 2–4 weeks understanding an unfamiliar codebase. Existing tools like GitHub Copilot and Cursor answer line-level questions — they tell you what a function does. Nobody has built a tool that explains the whole system: what each module owns, how data flows end-to-end, and exactly what to touch when you need to change behavior X.

---

## How It Works

```
GitHub URL
    ↓
Clone repo (GitPython, depth=1)
    ↓
Parse code structure (Python AST)
→ Extract functions, classes, imports per file
    ↓
Build dependency graph (NetworkX)
→ Map which module calls which
    ↓
Generate embeddings (CodeBERT)
→ Function-level chunks, not arbitrary token splits
    ↓
Store in ChromaDB (local vector store)
    ↓
Query arrives
    ↓
Two-layer retrieval
→ Semantic search (ChromaDB) + graph traversal (NetworkX)
    ↓
Groq LLaMA 3.3 70B generates answer
→ With exact file paths and line references
```

---

## Why This Is Different From Generic RAG

Most RAG projects chunk documents every 500 tokens. For code, this destroys context — a function gets split in half and retrieval quality collapses.

This project chunks by **AST node** — each vector represents a complete function or class. Combined with a **dependency graph layer**, it can answer traversal questions like *"what happens when a user submits this form?"* that pure vector search cannot.

---

## Stack

| Layer | Tool | Reason |
|---|---|---|
| Repo ingestion | GitPython | Clone any public repo, `depth=1` for speed |
| Code parsing | Python `ast` module | Parse code as code, not text |
| Dependency graph | NetworkX | Map cross-file call relationships |
| Embeddings | CodeBERT (`microsoft/codebert-base`) | Trained on code, not general text |
| Vector store | ChromaDB | Local, persistent, zero cost |
| LLM | Groq LLaMA 3.3 70B | Fast inference, free tier |
| LLM fallback | Ollama + CodeLlama 7B | Fully offline, no API dependency |
| API | FastAPI | Async, auto-docs at `/docs` |
| Frontend | Vanilla HTML/JS | No framework overhead |

---

## Setup

### Prerequisites

- Python 3.11+
- Git
- NVIDIA GPU recommended (RTX 3050+ with CUDA) — falls back to CPU
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Clone
git clone https://github.com/HARDIK-WEB-OSS/codebase-agent
cd codebase-agent

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. PyTorch with GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. Dependencies
pip install -r requirements.txt

# 5. Environment variables
cp .env.example .env
# Open .env and add your GROQ_API_KEY
```

### Environment Variables

```bash
# .env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq                  # "groq" or "ollama"
OLLAMA_MODEL=codellama:7b          # only needed if LLM_PROVIDER=ollama
TORCH_DEVICE=cuda                  # "cuda" or "cpu"
```

### Run

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`  
Frontend: open `frontend/index.html` in browser

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/ingest/` | POST | Clone, parse, and index a GitHub repo |
| `/ingest/repos` | GET | List all indexed repos |
| `/ingest/{repo_name}` | DELETE | Remove a repo |
| `/query/` | POST | Ask a question about an indexed repo |
| `/query/search/{repo_name}` | GET | Raw semantic search |
| `/health` | GET | Health check |

### Ingest a repo

```bash
curl -X POST http://localhost:8000/ingest/ \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/pallets/flask"}'
```

### Ask a question

```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_name": "pallets_flask",
    "question": "How does Flask handle routing?",
    "provider": "groq"
  }'
```

---

## Project Structure

```
codebase-agent/
├── api/
│   ├── main.py              # FastAPI app, CORS, health check
│   └── routers/
│       ├── ingest.py        # POST /ingest — clone + parse + index
│       └── query.py         # POST /query — semantic search + LLM answer
├── ingestion/
│   ├── cloner.py            # GitPython repo cloning
│   ├── parser.py            # Python AST parsing
│   ├── file_walker.py       # Repo traversal, file filtering
│   └── graph_builder.py     # NetworkX dependency graph
├── rag/
│   ├── embedder.py          # CodeBERT embeddings
│   ├── vector_store.py      # ChromaDB operations
│   └── retriever.py         # Two-layer retrieval logic
├── llm/
│   ├── groq_client.py       # Groq API client
│   ├── ollama_client.py     # Ollama local client
│   └── router.py            # Provider switching logic
├── frontend/
│   └── index.html           # Chat UI
├── config.py                # Central configuration
└── requirements.txt
```

---

## Internals Worth Knowing

**Function-level chunking** — The `ast` module parses Python source into a tree. We walk the tree and extract `FunctionDef` and `ClassDef` nodes as individual chunks. Each chunk includes its source lines, docstring, and import context.

**Dependency graph** — After parsing, we build a directed graph where nodes are files/functions and edges represent `import` relationships and function calls. This lets us answer traversal questions by walking the graph, not just searching vectors.

**Two-layer retrieval** — A query first hits ChromaDB for semantic similarity. The top results are then expanded using graph neighbors — pulling in callers and callees that may not be semantically similar but are structurally relevant.

---

## License

MIT License. Use at your own risk. No warranty expressed or implied.
