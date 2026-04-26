from dataclasses import dataclass, field
import networkx as nx
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.vector_store import search_chunks
from ingestion.graph_builder import get_neighbors

@dataclass
class RetrievedContext:
    query: str
    repo_name: str
    chunks: list[dict] = field(default_factory=list)
    graph_neighbors: list[str] = field(default_factory=list)
    context_text: str = ""

def retrieve(query: str, repo_name: str, graph=None, n_chunks: int = 8) -> RetrievedContext:
    ctx = RetrievedContext(query=query, repo_name=repo_name)
    ctx.chunks = search_chunks(repo_name, query, n_results=n_chunks)
    if graph is not None:
        for chunk in ctx.chunks[:3]:
            node_id = chunk["metadata"].get("file","") + "::" + chunk["metadata"].get("name","")
            if node_id in graph:
                ctx.graph_neighbors.extend(get_neighbors(graph, node_id, depth=1)[:5])
        ctx.graph_neighbors = list(set(ctx.graph_neighbors))
    ctx.context_text = _build_context(ctx)
    return ctx

def _build_context(ctx: RetrievedContext) -> str:
    parts = [f"Query: {ctx.query}\n", "="*60+"\n", "RELEVANT CODE:\n"]
    for i, chunk in enumerate(ctx.chunks, 1):
        m = chunk["metadata"]
        parts.append(f"\n[{i}] {m.get('type','code').upper()}: {m.get('name','unknown')}")
        parts.append(f"\nFile: {m.get('file','?')} | Line: {m.get('start_line','?')}-{m.get('end_line','?')} | Score: {chunk.get('score',0):.2f}")
        if m.get("docstring"): parts.append(f"\nDocstring: {m['docstring']}")
        parts.append(f"\n{chunk['text']}\n" + "-"*40)
    if ctx.graph_neighbors:
        parts.append(f"\nRELATED (graph):\n" + "".join(f"  - {n}\n" for n in ctx.graph_neighbors))
    return "".join(parts)

def build_prompt(query: str, context: RetrievedContext) -> str:
    return f"""You are an expert code analysis assistant. Answer using ONLY the provided context.
Always cite exact file paths and line numbers. If context is insufficient, say so.

CONTEXT:
{context.context_text}

QUESTION: {query}

ANSWER:"""
