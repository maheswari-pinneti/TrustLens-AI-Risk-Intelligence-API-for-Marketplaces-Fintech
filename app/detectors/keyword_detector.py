"""
Keyword Fraud & Counterfeit Detector Module
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from app.config import get_settings


class KeywordDetector:
    """
    Analyzes text fields (title, description) for known fraud, counterfeit,
    unauthorized goods, and off-platform transaction keywords.
    """

    DEFAULT_KEYWORDS: Dict[str, float] = {
        # Counterfeit / Replica (HIGH Severity)
        "replica": 1.0,
        "1:1 replica": 1.0,
        "counterfeit": 1.0,
        "fake": 0.9,
        "knockoff": 0.9,
        "clone": 0.9,
        "first copy": 0.9,
        "master copy": 0.9,
        "mirror quality": 0.85,
        "ua quality": 0.95,
        "unauthorized authentic": 1.0,
        "superclone": 1.0,
        "aa quality": 0.8,
        "aaa grade": 0.8,
        "looks authentic": 0.7,
        "not genuine": 1.0,
        "non genuine": 1.0,

        # Misleading / Stolen / Blocked (HIGH Severity)
        "bypassed icloud": 1.0,
        "icloud locked": 1.0,
        "imei blocked": 1.0,
        "blacklisted": 0.9,
        "stolen": 1.0,
        "customs seized": 0.8,
        "fell off truck": 0.8,

        # Off-Platform Suspicious Payment (HIGH Severity)
        "wire transfer only": 1.0,
        "telegram me": 0.9,
        "whatsapp me": 0.9,
        "cash only": 0.7,
        "pay offline": 0.95,
        "friends and family paypal": 0.9,
        "crypto only": 0.85,
        "zelle only": 0.85,
        "gift card payment": 0.95,
        "contact outside app": 0.95,
        "dm on instagram": 0.6,

        # Medium / Low Suspicious promotional language
        "oem factory": 0.5,
        "overrun": 0.5,
        "gray market": 0.4,
        "parallel import": 0.4,
        "factory reject": 0.5,
        "defective batch": 0.5,
        "b-grade": 0.5,
        "no receipt": 0.35,
        "no refund": 0.4,
        "urgent sale": 0.25,
        "must go today": 0.25,
        "won in lottery": 0.8,
    }

    def __init__(self, keywords_file: Optional[Path] = None):
        self.settings = get_settings()
        self.keywords: Dict[str, float] = dict(self.DEFAULT_KEYWORDS)
        
        # Load from configured file if exists
        target_file = keywords_file or self.settings.FRAUD_KEYWORDS_FILE
        if target_file and Path(target_file).exists():
            self._load_from_file(Path(target_file))

    def _load_from_file(self, file_path: Path) -> None:
        """Parses keyword:severity format from file."""
        severity_map = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if ":" in line:
                        parts = line.rsplit(":", 1)
                        kw = parts[0].strip().lower()
                        sev = parts[1].strip().upper()
                        weight = severity_map.get(sev, float(sev) if sev.replace('.', '', 1).isdigit() else 0.5)
                        self.keywords[kw] = weight
                    else:
                        self.keywords[line.lower()] = 0.8
        except Exception:
            # Fallback to defaults gracefully if file read fails
            pass

    def analyze(self, title: str, description: str) -> Dict[str, Any]:
        """
        Scans title and description for keywords.
        Returns normalized score (0.0 to 1.0), matched keyword details, and flags.
        """
        combined_text = f"{title} {description}".lower()
        # Clean special chars but preserve colons for expressions like 1:1
        cleaned_text = re.sub(r"[^\w\s:]", " ", combined_text)
        
        matches: List[Dict[str, Any]] = []
        max_severity = 0.0
        cumulative_severity = 0.0

        for keyword, severity in self.keywords.items():
            # Use regex word boundaries for single words, phrase match for multi-words
            pattern = r"(?:\b|_)" + re.escape(keyword) + r"(?:\b|_)"
            found_iter = list(re.finditer(pattern, cleaned_text))
            if found_iter:
                occurrences = len(found_iter)
                in_title = bool(re.search(pattern, title.lower()))
                # Title matches carry slightly more weight
                effective_severity = min(1.0, severity * (1.2 if in_title else 1.0))
                matches.append({
                    "keyword": keyword,
                    "severity": severity,
                    "occurrences": occurrences,
                    "found_in_title": in_title,
                    "effective_severity": round(effective_severity, 2)
                })
                max_severity = max(max_severity, effective_severity)
                cumulative_severity += effective_severity

        # Score formulation: combination of worst violation (70%) + presence of multiple triggers (30%)
        if not matches:
            normalized_score = 0.0
        else:
            multi_penalty = min(0.3, (len(matches) - 1) * 0.1)
            raw_score = (max_severity * 0.7) + multi_penalty + (min(0.2, cumulative_severity * 0.05))
            normalized_score = min(1.0, max(0.0, raw_score))

        flags = []
        for match in sorted(matches, key=lambda x: x["effective_severity"], reverse=True):
            location = "title and description" if match["found_in_title"] else "description"
            flags.append(f"Fraud keyword detected: '{match['keyword']}' (severity: {match['severity']}, in {location})")

        return {
            "normalized_score": round(normalized_score, 4),
            "matches_count": len(matches),
            "matched_keywords": [m["keyword"] for m in matches],
            "details": matches,
            "flags": flags
        }
