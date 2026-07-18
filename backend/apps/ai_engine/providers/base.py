from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
