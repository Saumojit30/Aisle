import re
import logging
from typing import Optional, Tuple, List, Dict

logger = logging.getLogger(__name__)

# Try importing Microsoft Presidio for enterprise NLP PII detection
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    _PRESIDIO_AVAILABLE = True
except ImportError:
    _PRESIDIO_AVAILABLE = False
    logger.warning("Microsoft Presidio not installed. Falling back to hybrid regex scanner.")


class ContentFilter:
    def __init__(self):
        self._presidio_analyzer = None
        self._presidio_anonymizer = None
        if _PRESIDIO_AVAILABLE:
            try:
                self._presidio_analyzer = AnalyzerEngine()
                self._presidio_anonymizer = AnonymizerEngine()
                logger.info("Microsoft Presidio PII Engine initialized successfully.")
            except Exception as e:
                logger.warning("Presidio engine init warning: %s. Using regex fallback.", str(e))

    PII_PATTERNS = {
        "email": re.compile(r'\b[\w.+-]+@[\w.-]+\.\w+\b'),
        "phone": re.compile(r'\b\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b'),
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
    }

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r'ignore previous instructions', re.IGNORECASE),
        re.compile(r'disregard prior rules', re.IGNORECASE),
        re.compile(r'you are now in developer mode', re.IGNORECASE),
        re.compile(r'system prompt override', re.IGNORECASE),
        re.compile(r'jailbreak', re.IGNORECASE),
    ]

    SENSITIVE_TOPICS = [
        "password", "login credential", "account takeover",
        "hack", "bypass", "exploit", "vulnerability",
        "phishing", "social security", "credit card number",
    ]

    def redact_pii(self, text: str) -> Tuple[str, List[Dict]]:
        findings = []

        # If Presidio is available and initialized, use NLP PII detection
        if self._presidio_analyzer and self._presidio_anonymizer:
            try:
                results = self._presidio_analyzer.analyze(text=text, entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "US_SSN", "IP_ADDRESS"], language='en')
                if results:
                    anonymized_result = self._presidio_anonymizer.anonymize(text=text, analyzer_results=results)
                    for res in results:
                        findings.append({
                            "type": res.entity_type.lower(),
                            "original": text[res.start:res.end],
                            "redacted": f"[{res.entity_type}_REDACTED]",
                        })
                    return anonymized_result.text, findings
            except Exception as e:
                logger.debug("Presidio scan failed, falling back to regex: %s", str(e))

        # Fallback to regex scanner
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

    def check_safety(self, text: str) -> Tuple[bool, Optional[str]]:
        # 1. Prompt Injection Checks
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if pattern.search(text):
                logger.warning("Prompt injection pattern blocked!")
                return False, "Security flag: Potential prompt manipulation detected."

        # 2. Sensitive Topic Checks
        lower = text.lower()
        for topic in self.SENSITIVE_TOPICS:
            if topic.lower() in lower:
                logger.warning("Sensitive topic detected: %s", topic)
                return False, f"Conversation flagged: sensitive topic '{topic}'."

        return True, None

    def sanitize(self, text: str) -> Tuple[str, List[Dict], bool, Optional[str]]:
        redacted, pii_findings = self.redact_pii(text)
        safe, msg = self.check_safety(redacted)
        return redacted, pii_findings, safe, msg


_content_filter: Optional[ContentFilter] = None


def get_content_filter() -> ContentFilter:
    global _content_filter
    if _content_filter is None:
        _content_filter = ContentFilter()
    return _content_filter
