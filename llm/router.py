import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LLM_PROVIDER
from llm.ollama_client import LLMResponse

def generate(prompt: str, provider: str | None = None) -> LLMResponse:
    target = provider or LLM_PROVIDER
    if target == "groq":
        from llm import groq_client
        return groq_client.generate(prompt)
    from llm import ollama_client
    return ollama_client.generate(prompt)

def generate_stream(prompt: str, provider: str | None = None):
    target = provider or LLM_PROVIDER
    if target == "groq":
        from llm import groq_client
        yield from groq_client.generate_stream(prompt)
    else:
        from llm import ollama_client
        yield from ollama_client.generate_stream(prompt)
