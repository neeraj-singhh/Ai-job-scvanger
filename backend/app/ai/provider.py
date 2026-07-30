"""
AI provider abstraction.

Both job normalization (structured extraction) and embeddings go through
this interface so the rest of the app doesn't care whether we're calling
OpenAI or Gemini under the hood. Configure via `AI_PROVIDER` env var.
"""
from __future__ import annotations

import abc
import json

from app.core.config import Settings, get_settings
from app.core.exceptions import UpstreamProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIProvider(abc.ABC):
    @abc.abstractmethod
    async def extract_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        """Call the LLM and return parsed JSON. Raises UpstreamProviderError on failure."""
        raise NotImplementedError

    @abc.abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for the given text."""
        raise NotImplementedError

    @abc.abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Return embedding vectors for a batch of texts (more efficient than N calls)."""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    def __init__(self, settings: Settings):
        from openai import AsyncOpenAI  # local import keeps optional dep lazy

        if not settings.OPENAI_API_KEY:
            raise UpstreamProviderError("OPENAI_API_KEY is not configured")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL

    async def extract_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = resp.choices[0].message.content
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            raise UpstreamProviderError(f"OpenAI extraction failed: {exc}") from exc

    async def embed(self, text: str) -> list[float]:
        result = await self.embed_batch([text])
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            # Truncate defensively; embedding models have token limits.
            cleaned = [t[:8000] if t else " " for t in texts]
            resp = await self.client.embeddings.create(model=self.embedding_model, input=cleaned)
            return [d.embedding for d in resp.data]
        except Exception as exc:  # noqa: BLE001
            raise UpstreamProviderError(f"OpenAI embedding failed: {exc}") from exc


class GeminiProvider(AIProvider):
    def __init__(self, settings: Settings):
        import google.generativeai as genai  # local import keeps optional dep lazy

        if not settings.GEMINI_API_KEY:
            raise UpstreamProviderError("GEMINI_API_KEY is not configured")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._genai = genai
        self.model_name = settings.GEMINI_MODEL

    async def extract_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        try:
            model = self._genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt,
                generation_config={"response_mime_type": "application/json", "temperature": 0},
            )
            resp = await model.generate_content_async(user_prompt)
            return json.loads(resp.text)
        except Exception as exc:  # noqa: BLE001
            raise UpstreamProviderError(f"Gemini extraction failed: {exc}") from exc

    async def embed(self, text: str) -> list[float]:
        try:
            result = await self._genai.embed_content_async(
                model="models/text-embedding-004", content=text
            )
            return result["embedding"]
        except Exception as exc:  # noqa: BLE001
            raise UpstreamProviderError(f"Gemini embedding failed: {exc}") from exc

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # Gemini's SDK doesn't batch embeddings natively; fan out concurrently upstream if needed.
        return [await self.embed(t) for t in texts]


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.AI_PROVIDER == "openai":
        return OpenAIProvider(settings)
    if settings.AI_PROVIDER == "gemini":
        return GeminiProvider(settings)
    raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")
