from groq import Groq
from app.core.config import settings

class BaseLLMService:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

class GroqLLMService(BaseLLMService):
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set")
        self.client = Groq(api_key=settings.groq_api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a grounded research assistant. "
                        "Answer only from the provided context. "
                        "If evidence is insufficient, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
            max_tokens=settings.groq_max_tokens,
        )
        return response.choices[0].message.content.strip()

class LLMServiceFactory:
    @staticmethod
    def get_service():
        backend = (settings.llm_backend or "groq").lower()

        if backend == "groq":
            return GroqLLMService()

        raise ValueError(f"Unsupported LLM backend: {backend}")