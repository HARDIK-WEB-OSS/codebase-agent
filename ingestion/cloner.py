import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import git
from config import REPOS_DIR, MAX_REPO_SIZE_MB

@dataclass
class CloneResult:
    success: bool
    repo_name: str
    path: Path | None = None
    size_mb: float = 0.0
    file_count: int = 0
    error: str | None = None

def _parse_repo_name(github_url: str) -> str:
    parsed = urlparse(github_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {github_url}")
    owner, repo = parts[0], parts[1]
    return f"{owner}_{repo.replace('.git', '')}"

def _get_dir_size_mb(path: Path) -> float:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)

def _count_files(path: Path) -> int:
    return sum(1 for f in path.rglob("*") if f.is_file())

def clone_repo(github_url: str, force: bool = False) -> CloneResult:
    try:
        repo_name = _parse_repo_name(github_url)
    except ValueError as e:
        return CloneResult(success=False, repo_name="unknown", error=str(e))
    clone_path = REPOS_DIR / repo_name
    if clone_path.exists():
        if force:
            shutil.rmtree(clone_path)
        else:
            return CloneResult(success=True, repo_name=repo_name, path=clone_path,
                size_mb=round(_get_dir_size_mb(clone_path), 2), file_count=_count_files(clone_path))
    print(f"Cloning {github_url} ...")
    try:
        git.Repo.clone_from(github_url, clone_path, depth=1)
    except git.exc.GitCommandError as e:
        if clone_path.exists():
            shutil.rmtree(clone_path)
        return CloneResult(success=False, repo_name=repo_name, error=f"Git clone failed: {e}")
    size_mb = _get_dir_size_mb(clone_path)
    if size_mb > MAX_REPO_SIZE_MB:
        shutil.rmtree(clone_path)
        return CloneResult(success=False, repo_name=repo_name,
            error=f"Repo too large: {size_mb:.1f}MB (max {MAX_REPO_SIZE_MB}MB)")
    return CloneResult(success=True, repo_name=repo_name, path=clone_path,
        size_mb=round(size_mb, 2), file_count=_count_files(clone_path))

def delete_repo(repo_name: str) -> bool:
    repo_path = REPOS_DIR / repo_name
    if repo_path.exists():
        shutil.rmtree(repo_path)
        return True
    return False

def list_cloned_repos() -> list[str]:
    if not REPOS_DIR.exists():
        return []
    return [d.name for d in REPOS_DIR.iterdir() if d.is_dir()]

if __name__ == "__main__":
    from rich import print as rprint
    result = clone_repo("https://github.com/pallets/flask")
    rprint(result)
