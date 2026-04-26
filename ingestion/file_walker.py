from dataclasses import dataclass, field
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_KB

SKIP_DIRS = {".git","__pycache__","node_modules",".venv","venv","env","dist","build",".next",".nuxt","coverage",".pytest_cache"}

@dataclass
class CodeFile:
    path: Path
    relative_path: str
    extension: str
    size_kb: float
    content: str = ""

@dataclass
class WalkResult:
    repo_name: str
    files: list[CodeFile] = field(default_factory=list)
    skipped_count: int = 0
    total_found: int = 0

def walk_repo(repo_path: Path) -> WalkResult:
    result = WalkResult(repo_name=repo_path.name)
    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in SKIP_DIRS for part in file_path.parts):
            result.skipped_count += 1
            continue
        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            result.skipped_count += 1
            continue
        result.total_found += 1
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            result.skipped_count += 1
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            result.skipped_count += 1
            continue
        result.files.append(CodeFile(
            path=file_path,
            relative_path=str(file_path.relative_to(repo_path)),
            extension=file_path.suffix,
            size_kb=round(size_kb, 2),
            content=content,
        ))
    return result

def get_file_tree(repo_path: Path, max_depth: int = 4) -> str:
    lines = [repo_path.name]
    def _walk(path, prefix, depth):
        if depth > max_depth:
            return
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        entries = [e for e in entries if e.name not in SKIP_DIRS and not e.name.startswith(".")]
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            lines.append(f"{prefix}{'└── ' if is_last else '├── '}{entry.name}")
            if entry.is_dir():
                _walk(entry, prefix + ("    " if is_last else "│   "), depth + 1)
    _walk(repo_path, "", 1)
    return "\n".join(lines)
