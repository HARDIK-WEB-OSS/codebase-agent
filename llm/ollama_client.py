from dataclasses import dataclass
import httpx, ollama
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_FALLBACK_MODEL

@dataclass
class LLMResponse:
    text: str
    model: str
    error: str | None = None

def is_ollama_running() -> bool:
    try: return httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0).status_code == 200
    except: return False

def is_model_available(model_name: str) -> bool:
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        return any(model_name in m.model for m in client.list().models)
    except: return False

def generate(prompt: str, model: str | None = None) -> LLMResponse:
    if not is_ollama_running():
        return LLMResponse(text="", model="", error="Ollama not running. Start with: ollama serve")
    target = model or OLLAMA_MODEL
    if not is_model_available(target):
        if is_model_available(OLLAMA_FALLBACK_MODEL):
            target = OLLAMA_FALLBACK_MODEL
        else:
            return LLMResponse(text="", model=target, error=f"Model '{target}' not found. Run: ollama pull {target}")
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        r = client.generate(model=target, prompt=prompt, options={"temperature":0.1,"num_predict":2048})
        return LLMResponse(text=r.response, model=target)
    except Exception as e:
        return LLMResponse(text="", model=target, error=str(e))

def generate_stream(prompt: str, model: str | None = None):
    if not is_ollama_running():
        yield "[ERROR] Ollama not running."
        return
    target = model or OLLAMA_MODEL
    client = ollama.Client(host=OLLAMA_BASE_URL)
    try:
        for chunk in client.generate(model=target, prompt=prompt, stream=True, options={"temperature":0.1,"num_predict":2048}):
            yield chunk.response
    except Exception as e:
        yield f"[ERROR] {e}"
