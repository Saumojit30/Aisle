import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ContentFilter:
    PII_PATTERNS = {
        "email": re.compile(r'\b[\w.+-]+@[\w.-]+\.\w+\b'),
        "phone": re.compile(r'\b\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    }

    SENSITIVE_TOPICS = [
        "password", "login credential", "account takeover",
        "hack", "bypass", "exploit", "vulnerability",
        "phishing", "social security", "credit card number",
    ]

    def redact_pii(self, text: str) -> tuple[str, list[dict]]:
        findings = []
        for label, pattern in self.PII_PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append({
                    "type": label,
                    "original": match.group(),
                    "redacted": f"[{label.upper()}_REDACTED]",
                })
        redacted = text
        for label, pattern in self.PII_PATTERNS.items():
            redacted = pattern.sub(f"[{label.upper()}_REDACTED]", redacted)
        if findings:
            logger.info("Redacted %d PII items: %s", len(findings), [f["type"] for f in findings])
        return redacted, findings

    def check_safety(self, text: str) -> tuple[bool, Optional[str]]:
        lower = text.lower()
        for topic in self.SENSITIVE_TOPICS:
            if topic.lower() in lower:
                logger.warning("Sensitive topic detected: %s", topic)
                return False, f"Conversation flagged: sensitive topic '{topic}'."
        return True, None

    def sanitize(self, text: str) -> tuple[str, list[dict], bool, Optional[str]]:
        redacted, pii_findings = self.redact_pii(text)
        safe, msg = self.check_safety(redacted)
        return redacted, pii_findings, safe, msg


_content_filter: Optional[ContentFilter] = None


def get_content_filter() -> ContentFilter:
    global _content_filter
    if _content_filter is None:
        _content_filter = ContentFilter()
    return _content_filter
