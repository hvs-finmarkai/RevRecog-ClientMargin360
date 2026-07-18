import os

import requests

from .base import LLMProvider


class OpenAIProvider(LLMProvider):

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.embedding_model = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.base_url = "https://api.openai.com/v1"
        self.timeout = int(os.environ.get("OPENAI_TIMEOUT", "60"))

    def _headers(self) -> dict:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.Timeout:
            raise TimeoutError(
                f"OpenAI request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e.response.status_code} - {e.response.text}")

    def embed(self, text: str) -> list[float]:
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self._headers(),
                json={
                    "model": self.embedding_model,
                    "input": text,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except requests.Timeout:
            raise TimeoutError(
                f"OpenAI embedding request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"OpenAI API error: {e.response.status_code} - {e.response.text}")

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=10,
            )
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def get_model_name(self) -> str:
        return self.model
