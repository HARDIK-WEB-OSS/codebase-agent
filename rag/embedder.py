from dataclasses import dataclass, field
import torch
from sentence_transformers import SentenceTransformer
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMBEDDING_MODEL, TORCH_DEVICE

@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)

_model = None

def _get_model():
    global _model
    if _model is None:
        device = TORCH_DEVICE if torch.cuda.is_available() else "cpu"
        print(f"Loading embedding model: {EMBEDDING_MODEL} on {device}")
        _model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    return _model

def embed_texts(texts: list[str], batch_size: int = 32) -> list[list[float]]:
    model = _get_model()
    embeddings = model.encode(texts, batch_size=batch_size,
        show_progress_bar=len(texts) > 50, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.tolist()

def chunks_from_graph_result(graph_result) -> list[Chunk]:
    chunks = []
    for pf in graph_result.parsed_files:
        for func in pf.functions:
            text = f"Function: {func.name}\nFile: {func.file_path}\nLine: {func.start_line}\n"
            if func.docstring:
                text += f"Docstring: {func.docstring}\n"
            text += f"\n{func.source}"
            chunks.append(Chunk(id=f"{func.file_path}::{func.name}::{func.start_line}", text=text,
                metadata={"type":"function","name":func.name,"file":func.file_path,
                    "start_line":func.start_line,"end_line":func.end_line,"docstring":func.docstring}))
        for cls in pf.classes:
            text = f"Class: {cls.name}\nFile: {cls.file_path}\nLine: {cls.start_line}\n"
            if cls.bases: text += f"Inherits: {', '.join(cls.bases)}\n"
            if cls.docstring: text += f"Docstring: {cls.docstring}\n"
            if cls.methods: text += f"Methods: {', '.join(cls.methods)}\n"
            chunks.append(Chunk(id=f"{cls.file_path}::{cls.name}::{cls.start_line}", text=text,
                metadata={"type":"class","name":cls.name,"file":cls.file_path,
                    "start_line":cls.start_line,"end_line":cls.end_line,
                    "docstring":cls.docstring,"methods":cls.methods,"bases":cls.bases}))
    return chunks
