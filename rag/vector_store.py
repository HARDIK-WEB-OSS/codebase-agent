import chromadb
from chromadb.config import Settings
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHROMA_DIR
from rag.embedder import Chunk, embed_texts

def _get_client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))

def _col_name(repo_name: str) -> str:
    return repo_name.replace("-","_").replace(".","_")

def _sanitize_metadata(metadata: dict) -> dict:
    clean = {}
    for k, v in metadata.items():
        if isinstance(v, (str, int, float, bool)):
            clean[k] = v
        elif isinstance(v, list):
            clean[k] = ", ".join(str(x) for x in v)
        elif v is None:
            clean[k] = ""
        else:
            clean[k] = str(v)
    return clean

def store_chunks(repo_name: str, chunks: list[Chunk]) -> int:
    if not chunks: return 0
    client = _get_client()
    name = _col_name(repo_name)
    try: client.delete_collection(name)
    except: pass
    col = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})
    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)
    for i in range(0, len(chunks), 500):
        batch = chunks[i:i+500]
        col.add(
            ids=[c.id for c in batch],
            embeddings=embeddings[i:i+500],
            documents=[c.text for c in batch],
            metadatas=[_sanitize_metadata(c.metadata) for c in batch]
        )
    return len(chunks)

def search_chunks(repo_name: str, query: str, n_results: int = 10) -> list[dict]:
    client = _get_client()
    try: col = client.get_collection(_col_name(repo_name))
    except: return []
    qe = embed_texts([query])[0]
    r = col.query(query_embeddings=[qe], n_results=min(n_results, col.count()),
        include=["documents","metadatas","distances"])
    return [{"text":doc,"metadata":meta,"score":round(1-dist,4)}
        for doc,meta,dist in zip(r["documents"][0],r["metadatas"][0],r["distances"][0])]

def repo_is_indexed(repo_name: str) -> bool:
    try: return _get_client().get_collection(_col_name(repo_name)).count() > 0
    except: return False

def get_index_stats(repo_name: str) -> dict:
    try: return {"repo":repo_name,"chunks_indexed":_get_client().get_collection(_col_name(repo_name)).count()}
    except: return {"repo":repo_name,"chunks_indexed":0}
