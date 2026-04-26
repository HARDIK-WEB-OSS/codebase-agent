# Codebase Onboarding Agent

> Ask questions about any GitHub repository and get answers with exact file paths and line references.

## The Problem
New developers waste 2-4 weeks understanding a codebase.
Existing tools (Copilot, Cursor) answer line-level questions.
Nobody has built a tool that explains the whole system.

## How It Works
```
GitHub URL → clone repo → parse AST → build dependency graph
→ embed functions → store in ChromaDB
→ query arrives → vector search + graph traversal
→ CodeLlama answers with file paths + line numbers
```

## Stack
- **Ingestion**: gitpython, Python AST module
- **Graph**: NetworkX  
- **Embeddings**: sentence-transformers (local, free)
- **Vector Store**: ChromaDB (local, free)
- **LLM**: Ollama + CodeLlama 7B (local, free) / Groq fallback
- **API**: FastAPI
- **Frontend**: Vanilla HTML/JS

## Setup
(We'll fill this in as we build)
```

---

## Verify Your Structure

Your project root should now look exactly like this in VS Code:
```
codebase-agent/
├── .env              ← secrets, never committed
├── .gitignore        ← tells git what to ignore
├── README.md         ← project brain
├── api/
│   └── routers/
├── frontend/
├── ingestion/
├── llm/
├── rag/
└── tests/