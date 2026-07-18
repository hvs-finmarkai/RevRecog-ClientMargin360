import os

import requests

from .base import LLMProvider


class OllamaProvider(LLMProvider):

    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "llama3")
        self.timeout = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.ConnectionError:
            raise ConnectionError(
                f"Ollama is not running at {self.base_url}. "
                "Please start Ollama or switch to another provider."
            )
        except requests.Timeout:
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {e.response.status_code} - {e.response.text}")

    def embed(self, text: str) -> list[float]:
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except requests.ConnectionError:
            raise ConnectionError(
                f"Ollama is not running at {self.base_url}. "
                "Please start Ollama or switch to another provider."
            )
        except requests.Timeout:
            raise TimeoutError(
                f"Ollama embedding request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Ollama API error: {e.response.status_code} - {e.response.text}")

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def get_model_name(self) -> str:
        return self.model
