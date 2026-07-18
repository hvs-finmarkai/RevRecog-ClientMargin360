import os

import requests

from .base import LLMProvider


class GeminiProvider(LLMProvider):

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self.embedding_model = os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-004")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = int(os.environ.get("GEMINI_TIMEOUT", "60"))

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            response = requests.post(
                url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return ""
            return parts[0].get("text", "")
        except requests.Timeout:
            raise TimeoutError(
                f"Gemini request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Gemini API error: {e.response.status_code} - {e.response.text}")

    def embed(self, text: str) -> list[float]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        try:
            url = (
                f"{self.base_url}/models/{self.embedding_model}:embedContent?key={self.api_key}"
            )
            response = requests.post(
                url,
                json={
                    "model": f"models/{self.embedding_model}",
                    "content": {"parts": [{"text": text}]},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", {}).get("values", [])
        except requests.Timeout:
            raise TimeoutError(
                f"Gemini embedding request timed out after {self.timeout} seconds."
            )
        except requests.HTTPError as e:
            raise RuntimeError(f"Gemini API error: {e.response.status_code} - {e.response.text}")

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            url = f"{self.base_url}/models?key={self.api_key}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def get_model_name(self) -> str:
        return self.model
