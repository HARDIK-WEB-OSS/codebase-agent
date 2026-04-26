from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ingestion.cloner import clone_repo, list_cloned_repos, delete_repo
from ingestion.graph_builder import build_graph
from rag.embedder import chunks_from_graph_result
from rag.vector_store import store_chunks, get_index_stats, repo_is_indexed

router = APIRouter(prefix="/ingest", tags=["ingestion"])
_graph_cache: dict = {}

class IngestRequest(BaseModel):
    github_url: str
    force: bool = False

class IngestResponse(BaseModel):
    success: bool
    repo_name: str
    file_count: int = 0
    chunks_indexed: int = 0
    size_mb: float = 0.0
    error: str | None = None

@router.post("/", response_model=IngestResponse)
async def ingest_repo(request: IngestRequest):
    clone_result = clone_repo(request.github_url, force=request.force)
    if not clone_result.success:
        raise HTTPException(status_code=400, detail=clone_result.error)
    if not request.force and repo_is_indexed(clone_result.repo_name):
        stats = get_index_stats(clone_result.repo_name)
        return IngestResponse(success=True, repo_name=clone_result.repo_name,
            file_count=clone_result.file_count, chunks_indexed=stats["chunks_indexed"], size_mb=clone_result.size_mb)
    graph_result = build_graph(clone_result.path)
    _graph_cache[clone_result.repo_name] = graph_result.graph
    chunks = chunks_from_graph_result(graph_result)
    stored = store_chunks(clone_result.repo_name, chunks)
    return IngestResponse(success=True, repo_name=clone_result.repo_name,
        file_count=clone_result.file_count, chunks_indexed=stored, size_mb=clone_result.size_mb)

@router.get("/repos")
async def list_repos():
    return {"repos": [{"repo_name":r,"indexed":get_index_stats(r)["chunks_indexed"]>0,
        "chunks":get_index_stats(r)["chunks_indexed"]} for r in list_cloned_repos()]}

@router.delete("/{repo_name}")
async def remove_repo(repo_name: str):
    if not delete_repo(repo_name):
        raise HTTPException(status_code=404, detail=f"Repo '{repo_name}' not found")
    _graph_cache.pop(repo_name, None)
    return {"deleted": repo_name}

def get_cached_graph(repo_name: str):
    return _graph_cache.get(repo_name)
