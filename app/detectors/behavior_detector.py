"""
Listing Behavioral Patterns & Urgency Anomaly Detector
"""
import re
from typing import Dict, Any, Optional, List


class BehaviorDetector:
    """
    Detects listing behavioral anomalies such as excessive urgency/shouting,
    suspicious contact details in descriptions, burst velocity, and repeated patterns.
    """

    PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    URL_REGEX = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*")
    HANDLE_REGEX = re.compile(r"@[a-zA-Z0-9_]{3,30}")

    def analyze(
        self,
        title: str,
        description: str,
        listing_velocity_1h: Optional[int] = None,
        recent_price_drops_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluates behavioral indicators.
        Returns normalized score (0.0 to 1.0), flags, and detected pattern evidence.
        """
        flags = []
        behavior_points = 0.0
        patterns_detected = {}

        # 1. Uppercase Ratio / Shouting Analysis
        title_alpha = [c for c in title if c.isalpha()]
        if len(title_alpha) >= 10:
            upper_count = sum(1 for c in title_alpha if c.isupper())
            upper_ratio = upper_count / len(title_alpha)
            patterns_detected["title_uppercase_ratio"] = round(upper_ratio, 2)
            if upper_ratio > 0.65:
                behavior_points += 0.35
                flags.append(f"Excessive shouting in title ({int(upper_ratio * 100)}% uppercase letters)")
            elif upper_ratio > 0.40:
                behavior_points += 0.15

        # 2. Excessive Urgency Punctuation (e.g., "!!!!", "???", "$$$")
        exclamation_count = title.count("!") + description.count("!")
        question_count = title.count("?") + description.count("?")
        if exclamation_count >= 5:
            behavior_points += 0.25
            flags.append(f"High urgency punctuation detected ({exclamation_count} exclamation marks)")
        patterns_detected["exclamation_count"] = exclamation_count

        # 3. Direct Off-Platform Contact Leaks (Phone, Email, External URLs, Telegram handles)
        phones = self.PHONE_REGEX.findall(description)
        emails = self.EMAIL_REGEX.findall(description)
        urls = self.URL_REGEX.findall(description)
        handles = self.HANDLE_REGEX.findall(description)

        if phones:
            behavior_points += 0.45
            flags.append(f"Direct phone number leaked in description: {phones[0]}")
            patterns_detected["phone_numbers"] = phones[:3]

        if emails:
            behavior_points += 0.40
            flags.append(f"Direct email address leaked in description: {emails[0]}")
            patterns_detected["emails"] = emails[:3]

        if urls:
            behavior_points += 0.35
            flags.append("External URL / link embedded in product description")
            patterns_detected["urls"] = urls[:3]

        if handles:
            behavior_points += 0.25
            flags.append(f"Social media handle detected: {handles[0]}")
            patterns_detected["social_handles"] = handles[:3]

        # 4. Listing Velocity (Burst creation from same merchant)
        if listing_velocity_1h is not None:
            patterns_detected["listing_velocity_1h"] = listing_velocity_1h
            if listing_velocity_1h >= 20:
                behavior_points += 0.50
                flags.append(f"High listing velocity anomaly: {listing_velocity_1h} listings published in past hour")
            elif listing_velocity_1h >= 10:
                behavior_points += 0.30
                flags.append(f"Elevated listing velocity: {listing_velocity_1h} listings in past hour")

        # 5. Volatile Price Manipulation
        if recent_price_drops_count is not None and recent_price_drops_count >= 3:
            behavior_points += 0.30
            flags.append(f"Suspicious price volatility: {recent_price_drops_count} rapid price cuts recorded")
            patterns_detected["recent_price_drops"] = recent_price_drops_count

        normalized_score = min(1.0, max(0.0, behavior_points))

        return {
            "normalized_score": round(normalized_score, 4),
            "patterns": patterns_detected,
            "flags": flags
        }
