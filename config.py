import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:7b")
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "mistral:7b")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" | "groq"

TORCH_DEVICE = os.getenv("TORCH_DEVICE", "cuda")

DATA_DIR = BASE_DIR / "data"
REPOS_DIR = DATA_DIR / "repos"
CHROMA_DIR = DATA_DIR / "chroma"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
REPOS_DIR.mkdir(exist_ok=True)
CHROMA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "microsoft/codebert-base")

MAX_REPO_SIZE_MB = int(os.getenv("MAX_REPO_SIZE_MB", "500"))
MAX_FILE_SIZE_KB = int(os.getenv("MAX_FILE_SIZE_KB", "500"))

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c", ".cs",
    ".rb", ".php",
}

APP_ENV = os.getenv("APP_ENV", "development")  # "development" | "production"
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
DEBUG = APP_ENV == "development"


def verify_config() -> dict:
    issues = []

    if LLM_PROVIDER == "groq" and not GROQ_API_KEY:
        issues.append("GROQ_API_KEY missing in .env")

    if LLM_PROVIDER not in ("ollama", "groq"):
        issues.append(f"LLM_PROVIDER '{LLM_PROVIDER}' invalid — must be 'ollama' or 'groq'")

    if TORCH_DEVICE == "cuda":
        try:
            import torch
            if not torch.cuda.is_available():
                issues.append("TORCH_DEVICE=cuda but CUDA unavailable — falling back to CPU")
        except ImportError:
            issues.append("torch not installed")

    return {
        "status": "ok" if not issues else "warnings",
        "issues": issues,
        "settings": {
            "llm_provider": LLM_PROVIDER,
            "ollama_model": OLLAMA_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "torch_device": TORCH_DEVICE,
            "app_env": APP_ENV,
            "data_dir": str(DATA_DIR),
            "repos_dir": str(REPOS_DIR),
            "chroma_dir": str(CHROMA_DIR),
        }
    }


if __name__ == "__main__":
    from rich import print as rprint
    rprint(verify_config())
    