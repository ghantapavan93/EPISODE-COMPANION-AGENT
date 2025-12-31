from abc import ABC, abstractmethod
import os
from typing import Optional
import logging

from langchain_ollama import ChatOllama
# from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    @abstractmethod
    def get_llm(self):
        pass

class OllamaClient(LLMClient):
    def __init__(self, model_name: str = "qwen2.5:7b-instruct"):
        self.model_name = model_name
    
    def get_llm(self):
        return ChatOllama(model=self.model_name, temperature=0.7)

class OpenAIClient(LLMClient):
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        
    def get_llm(self):
        # Placeholder for actual implementation
        # return ChatOpenAI(model=self.model_name, temperature=0.7)
        raise NotImplementedError("OpenAI backend not fully configured yet.")

class GeminiClient(LLMClient):
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.model_name = model_name
        
    def get_llm(self):
        # Placeholder for actual implementation
        # return ChatGoogleGenerativeAI(model=self.model_name, temperature=0.7)
        raise NotImplementedError("Gemini backend not fully configured yet.")

def get_llm_client(backend: str = "ollama", model_name: Optional[str] = None) -> LLMClient:
    """Factory to get the appropriate LLM client."""
    backend = backend.lower()
    
    if backend == "ollama":
        model = model_name or "qwen2.5:7b-instruct"
        return OllamaClient(model_name=model)
    elif backend == "openai":
        model = model_name or "gpt-4o"
        return OpenAIClient(model_name=model)
    elif backend == "gemini":
        model = model_name or "gemini-1.5-pro"
        return GeminiClient(model_name=model)
    else:
        logger.warning(f"Unknown backend '{backend}', defaulting to Ollama.")
        return OllamaClient()
