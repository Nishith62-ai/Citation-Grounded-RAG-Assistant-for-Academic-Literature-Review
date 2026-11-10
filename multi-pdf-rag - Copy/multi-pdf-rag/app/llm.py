"""LLM provider abstraction supporting OpenAI and Gemini."""

import os
from abc import ABC, abstractmethod

from .config import (
    LLM_PROVIDER,
    OPENAI_MODEL,
    GEMINI_MODEL,
)


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, system: str, user: str) -> str:
        pass


class OpenAIProvider(LLMProvider):

    def __init__(self):
        from openai import OpenAI

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is missing.")

        self.client = OpenAI()

    def generate(self, system: str, user: str) -> str:

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )

        return response.choices[0].message.content.strip()


class GeminiProvider(LLMProvider):

    def __init__(self):
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing.")

        self.client = genai.Client(api_key=api_key)

    def generate(self, system: str, user: str) -> str:

        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user,
            config={
                "system_instruction": system,
                "temperature": 0,
            },
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()


PROVIDERS = {
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}

_instance = None


def get_llm() -> LLMProvider:

    global _instance

    if _instance is None:

        if LLM_PROVIDER not in PROVIDERS:
            raise RuntimeError(
                f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. "
                f"Options: {list(PROVIDERS)}"
            )

        _instance = PROVIDERS[LLM_PROVIDER]()

    return _instance