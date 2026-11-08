"""
Input Sanitization & Attack Vector Detection Module
Protects against XSS, SQL Injection patterns, Prompt Injection, and Unicode exploitation.
"""
import re
import html
from typing import Tuple, List


# Pre-compiled Regex Patterns for Injection Detection
SQLI_PATTERNS = [
    re.compile(r"(\b(UNION(\s+ALL)?|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|EXEC|EXECUTE)\b)", re.IGNORECASE),
    re.compile(r"(--|/\*|\*/|#)", re.IGNORECASE),
    re.compile(r"(\bOR\b|\bAND\b)\s+[\w\'\"]+\s*=\s*[\w\'\"]+", re.IGNORECASE),
    re.compile(r"(\bSLEEP\s*\(\d+\)|\bBENCHMARK\s*\(|\bWAITFOR\s+DELAY\b)", re.IGNORECASE)
]

XSS_PATTERNS = [
    re.compile(r"<\s*script[^>]*>", re.IGNORECASE),
    re.compile(r"<\s*/\s*script\s*>", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),  # e.g., onerror=, onload=
    re.compile(r"<\s*(iframe|object|embed|svg|img|link|meta)\b[^>]*>", re.IGNORECASE)
]

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+developer\s+mode", re.IGNORECASE),
    re.compile(r"override\s+risk\s+(score|level|assessment)", re.IGNORECASE),
    re.compile(r"system\s*:\s*set\s+risk", re.IGNORECASE)
]


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """
    Sanitizes raw text input:
    - Truncates to maximum safe length
    - Strips dangerous ASCII/Unicode control characters and null bytes
    - Strips malicious active script/HTML tags (<script>, <iframe>, <object>, <embed>, <svg>)
    - Disarms javascript: URIs and inline HTML event attributes (onload, onerror, etc.)
    - Preserves normal punctuation and text structure for accurate NLP and risk evaluation
    """
    if not text:
        return ""

    # Truncate
    clean = str(text)[:max_length]

    # Remove null bytes and invisible control characters (preserve normal whitespace \n, \r, \t)
    clean = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", clean)

    # Strip dangerous HTML and script tags
    clean = re.sub(
        r"<\s*/?\s*(script|style|iframe|object|embed|applet|meta|link|svg)[^>]*>",
        "",
        clean,
        flags=re.IGNORECASE
    )

    # Disarm javascript: URIs
    clean = re.sub(r"javascript\s*:\s*", "blocked-script:", clean, flags=re.IGNORECASE)

    # Disarm event handlers like onerror=, onload=, onclick=
    clean = re.sub(r"\bon([a-z]{3,15})\s*=", r"disarmed-\1=", clean, flags=re.IGNORECASE)

    # Normalize excessive spacing
    clean = re.sub(r"[ \t]+", " ", clean).strip()

    return clean


def inspect_security_threats(text: str) -> Tuple[bool, List[str]]:
    """
    Audits input text against known attack signatures (SQLi, XSS, Prompt Injection).
    Returns (has_threat, threat_details).
    """
    if not text:
        return False, []

    threats = []

    # Check XSS
    for pat in XSS_PATTERNS:
        if pat.search(text):
            threats.append("Cross-Site Scripting (XSS) / Malicious Script pattern detected")
            break

    # Check SQLi
    for pat in SQLI_PATTERNS:
        if pat.search(text):
            threats.append("Potential SQL Injection (SQLi) syntax pattern detected")
            break

    # Check Prompt Injection
    for pat in PROMPT_INJECTION_PATTERNS:
        if pat.search(text):
            threats.append("Adversarial AI Prompt Injection attempt detected")
            break

    return (len(threats) > 0), threats
