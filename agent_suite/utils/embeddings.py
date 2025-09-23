"""Utility helpers for deterministic lightweight embeddings."""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, List


def normalize(text: str) -> list[str]:
    """Lower-case and split text into tokens."""

    return [token for token in text.lower().replace("/", " ").replace("-", " ").split() if token]


def hashed_embedding(*segments: Iterable[str], dimensions: int = 64) -> List[float]:
    """Generate a deterministic embedding using a hashing trick.

    This avoids heavyweight ML dependencies while providing repeatable vectors for
    semantic comparisons and ranking inside unit tests.
    """

    vector = [0.0] * dimensions
    for segment in segments:
        for token, count in Counter(normalize(" ".join(segment))).items():
            index = hash(token) % dimensions
            vector[index] += float(count)

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


__all__ = ["hashed_embedding"]
