from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from rag.retriever import retrieve, build_prompt
from rag.vector_store import repo_is_indexed, search_chunks
from llm.router import generate, generate_stream

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    repo_name: str
    question: str
    provider: str | None = None
    stream: bool = False
    n_chunks: int = 8

class QueryResponse(BaseModel):
    answer: str
    repo_name: str
    question: str
    model_used: str
    chunks_used: int

@router.post("/", response_model=QueryResponse)
async def query_repo(request: QueryRequest):
    if not repo_is_indexed(request.repo_name):
        raise HTTPException(status_code=404, detail=f"Repo '{request.repo_name}' not indexed. POST /ingest first.")
    from api.routers.ingest import get_cached_graph
    graph = get_cached_graph(request.repo_name)
    context = retrieve(query=request.question, repo_name=request.repo_name, graph=graph, n_chunks=request.n_chunks)
    if not context.chunks:
        raise HTTPException(status_code=404, detail="No relevant code found.")
    prompt = build_prompt(request.question, context)
    if request.stream:
        def stream():
            for chunk in generate_stream(prompt, provider=request.provider):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(stream(), media_type="text/event-stream")
    response = generate(prompt, provider=request.provider)
    if response.error:
        raise HTTPException(status_code=503, detail=response.error)
    return QueryResponse(answer=response.text, repo_name=request.repo_name,
        question=request.question, model_used=response.model, chunks_used=len(context.chunks))

@router.get("/search/{repo_name}")
async def search_code(repo_name: str, q: str, n: int = 5):
    if not repo_is_indexed(repo_name):
        raise HTTPException(status_code=404, detail=f"Repo '{repo_name}' not indexed.")
    results = search_chunks(repo_name, q, n_results=n)
    return {"repo":repo_name,"query":q,"results":[{"name":r["metadata"].get("name"),
        "type":r["metadata"].get("type"),"file":r["metadata"].get("file"),
        "start_line":r["metadata"].get("start_line"),"score":r["score"]} for r in results]}
