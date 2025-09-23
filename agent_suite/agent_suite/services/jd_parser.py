"""Structured parsing for job descriptions."""

from __future__ import annotations

from typing import Any, Dict

import re

from structlog import get_logger

logger = get_logger(__name__)

RESPONSIBILITY_REGEX = re.compile(r"(?:responsibilities|what you will do)[:\n]\s*(.*)", re.IGNORECASE | re.DOTALL)
REQUIREMENT_REGEX = re.compile(r"(?:requirements|qualifications)[:\n]\s*(.*)", re.IGNORECASE | re.DOTALL)


class JobDescriptionParser:
    """Extract structured data from raw job descriptions."""

    def parse(self, description: str) -> Dict[str, Any]:
        """Parse description text into structured schema."""

        responsibilities = self._split_section(description, RESPONSIBILITY_REGEX)
        requirements = self._split_section(description, REQUIREMENT_REGEX)
        keywords = self._extract_keywords(description)
        logger.info(
            "jd_parser.parse",
            responsibilities=len(responsibilities),
            requirements=len(requirements),
            keywords=len(keywords),
        )
        return {
            "responsibilities": responsibilities,
            "requirements": requirements,
            "keywords": keywords,
        }

    def _split_section(self, description: str, pattern: re.Pattern[str]) -> list[str]:
        match = pattern.search(description)
        if not match:
            return []
        section = match.group(1)
        items = [item.strip(" -\n\t") for item in re.split(r"[\n\r]\s*[-*]?", section) if item.strip()]
        return items

    def _extract_keywords(self, description: str) -> list[str]:
        tokens = {token.lower().strip(".,") for token in description.split() if len(token) > 2}
        # filter out common stop words (very small list for demo purposes)
        stop_words = {"the", "and", "with", "will", "you", "for", "are"}
        return sorted(token for token in tokens if token not in stop_words)


__all__ = ["JobDescriptionParser"]
