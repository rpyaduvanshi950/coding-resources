"""Generate personalized communication artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from jinja2 import Environment, PackageLoader, select_autoescape


@dataclass
class CommunicationsResult:
    """Bundle of generated communication assets."""

    cover_letter: str
    recruiter_email: str


class CommunicationsBuilder:
    """Render cover letters and recruiter outreach emails."""

    def __init__(self) -> None:
        self._jinja_env = Environment(
            loader=PackageLoader("agent_suite", "templates"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def build(self, profile: Dict[str, Any], job: Dict[str, Any], tone: str = "professional") -> CommunicationsResult:
        cover_letter_template = self._jinja_env.get_template("cover_letter_template.j2")
        recruiter_email_template = self._jinja_env.get_template("recruiter_email_template.j2")
        context = {
            "profile": profile,
            "job": job,
            "tone": tone,
        }
        cover_letter = cover_letter_template.render(**context)
        recruiter_email = recruiter_email_template.render(**context)
        return CommunicationsResult(cover_letter=cover_letter, recruiter_email=recruiter_email)


__all__ = ["CommunicationsBuilder", "CommunicationsResult"]
