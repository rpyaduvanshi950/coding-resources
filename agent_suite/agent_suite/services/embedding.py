"""Embedding utilities for profile and job semantic representation."""

from __future__ import annotations

import hashlib
from typing import Iterable, List

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from agent_suite.config import get_settings


class EmbeddingService:
    """Wrapper around LangChain embeddings with deterministic fallback."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: Embeddings | None = None

    @property
    def client(self) -> Embeddings:
        """Return configured embeddings provider."""

        if self._client is None:
            if self._settings.openai_api_key:
                self._client = OpenAIEmbeddings(model=self._settings.embeddings_model)
            else:  # pragma: no cover - environment specific
                self._client = _DeterministicEmbeddings()
        return self._client

    def embed_documents(self, documents: Iterable[str]) -> List[List[float]]:
        """Embed a sequence of documents."""

        return self.client.embed_documents(list(documents))

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""

        return self.client.embed_query(query)


class _DeterministicEmbeddings(Embeddings):
    """Fallback embedding generator used for offline/local testing."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:  # type: ignore[override]
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:  # type: ignore[override]
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255 for byte in digest[:32]]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:  # pragma: no cover - sync fallback
        return self.embed_documents(texts)

    async def aembed_query(self, text: str) -> List[float]:  # pragma: no cover - sync fallback
        return self.embed_query(text)


__all__ = ["EmbeddingService"]
