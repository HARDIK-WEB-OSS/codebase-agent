import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GROQ_API_KEY, GROQ_MODEL
from llm.ollama_client import LLMResponse

def generate(prompt: str, model: str | None = None) -> LLMResponse:
    if not GROQ_API_KEY:
        return LLMResponse(text="", model="", error="GROQ_API_KEY not set in .env")
    try:
        from groq import Groq
        target = model or GROQ_MODEL
        r = Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model=target, messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=2048)
        return LLMResponse(text=r.choices[0].message.content, model=target)
    except Exception as e:
        return LLMResponse(text="", model=model or GROQ_MODEL, error=str(e))

def generate_stream(prompt: str, model: str | None = None):
    if not GROQ_API_KEY:
        yield "[ERROR] GROQ_API_KEY not set"
        return
    try:
        from groq import Groq
        target = model or GROQ_MODEL
        for chunk in Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model=target, messages=[{"role":"user","content":prompt}],
            temperature=0.1, max_tokens=2048, stream=True):
            delta = chunk.choices[0].delta.content
            if delta: yield delta
    except Exception as e:
        yield f"[ERROR] {e}"
