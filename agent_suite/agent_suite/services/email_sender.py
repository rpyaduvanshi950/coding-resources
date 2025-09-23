"""Email sending abstraction for Gmail/SMTP integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from structlog import get_logger

logger = get_logger(__name__)


@dataclass
class EmailResult:
    """Outcome of an email sending operation."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailSender:
    """Simplified email sender stub; integrate Gmail API/SMTP in production."""

    def send_email(self, sender: str, recipient: str, subject: str, body: str) -> EmailResult:
        if "@" not in recipient:
            return EmailResult(success=False, error="Invalid recipient")
        message_id = f"msg_{abs(hash((sender, recipient, subject))) % (10**10)}"
        logger.info("email.send", sender=sender, recipient=recipient, subject=subject)
        return EmailResult(success=True, message_id=message_id)


__all__ = ["EmailSender", "EmailResult"]
