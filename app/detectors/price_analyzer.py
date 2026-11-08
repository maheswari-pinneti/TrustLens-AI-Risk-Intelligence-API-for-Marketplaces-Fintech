"""
Price Anomaly & Market Valuation Detector Module
"""
from typing import Dict, Any, Optional


class PriceAnalyzer:
    """
    Evaluates listing price relative to market value, detecting severe underpricing,
    unrealistic discounts often used by counterfeit sellers, and extreme price gouging.
    """

    # Category fallback baseline estimates (USD) for when market_price is not provided
    CATEGORY_BENCHMARKS: Dict[str, Dict[str, float]] = {
        "electronics": {"min_reasonable": 25.0, "typical": 250.0},
        "footwear & apparel": {"min_reasonable": 20.0, "typical": 110.0},
        "luxury goods": {"min_reasonable": 150.0, "typical": 1200.0},
        "watches & jewelry": {"min_reasonable": 50.0, "typical": 600.0},
        "smartphones": {"min_reasonable": 80.0, "typical": 500.0},
        "perfume & cosmetics": {"min_reasonable": 15.0, "typical": 85.0},
        "general": {"min_reasonable": 5.0, "typical": 45.0},
    }

    def analyze(
        self,
        price: float,
        market_price: Optional[float] = None,
        category: Optional[str] = "General"
    ) -> Dict[str, Any]:
        """
        Analyzes the price against market reference or category standards.
        Returns a normalized score (0.0 to 1.0), discount percentage, and descriptive flags.
        """
        flags = []
        cat_key = (category or "general").strip().lower()
        benchmark = self.CATEGORY_BENCHMARKS.get(cat_key, self.CATEGORY_BENCHMARKS["general"])

        if price <= 0:
            return {
                "normalized_score": 1.0,
                "discount_percentage": 100.0,
                "price": price,
                "market_price": market_price,
                "anomaly_type": "INVALID_PRICE",
                "flags": ["Invalid listing price: price must be strictly greater than 0"]
            }

        # Case 1: Market price provided
        if market_price is not None and market_price > 0:
            discount_pct = ((market_price - price) / market_price) * 100.0
            
            if discount_pct >= 90.0:
                normalized_score = 1.0
                flags.append(f"Extreme price anomaly: {discount_pct:.1f}% discount compared to market benchmark (${market_price:,.2f})")
                anomaly_type = "CRITICAL_UNDERPRICING"
            elif discount_pct >= 75.0:
                # 75% to 89.9%
                normalized_score = 0.85 + ((discount_pct - 75.0) / 15.0) * 0.14
                flags.append(f"Severe price anomaly: {discount_pct:.1f}% discount indicates likely counterfeit or bait listing")
                anomaly_type = "SEVERE_UNDERPRICING"
            elif discount_pct >= 55.0:
                # 55% to 74.9%
                normalized_score = 0.55 + ((discount_pct - 55.0) / 20.0) * 0.29
                flags.append(f"High discount anomaly: {discount_pct:.1f}% discount requires verification")
                anomaly_type = "HIGH_DISCOUNT"
            elif discount_pct >= 35.0:
                normalized_score = 0.25 + ((discount_pct - 35.0) / 20.0) * 0.25
                flags.append(f"Moderate promotional discount: {discount_pct:.1f}% off market reference")
                anomaly_type = "MODERATE_DISCOUNT"
            elif discount_pct < -250.0:
                # Price is > 3.5x market price (possible scam or price gouging)
                normalized_score = 0.65
                flags.append(f"Extreme price inflation: listing price (${price:,.2f}) is over 3.5x market value (${market_price:,.2f})")
                anomaly_type = "PRICE_GOUGING"
            else:
                normalized_score = 0.0
                anomaly_type = "NORMAL_PRICING"

            return {
                "normalized_score": round(min(1.0, max(0.0, normalized_score)), 4),
                "discount_percentage": round(discount_pct, 2),
                "price": price,
                "market_price": market_price,
                "anomaly_type": anomaly_type,
                "flags": flags
            }

        # Case 2: Market price not provided - evaluate against category floor
        if price < benchmark["min_reasonable"]:
            normalized_score = 0.8
            flags.append(
                f"Suspiciously low category price: ${price:,.2f} is well below minimum expected value for {category} (standard min: ${benchmark['min_reasonable']:,.2f})"
            )
            anomaly_type = "BELOW_CATEGORY_MINIMUM"
        elif price < (benchmark["typical"] * 0.25):
            normalized_score = 0.45
            flags.append(
                f"Low category price: ${price:,.2f} is under 25% of typical {category} value (${benchmark['typical']:,.2f})"
            )
            anomaly_type = "BELOW_CATEGORY_TYPICAL"
        else:
            normalized_score = 0.0
            anomaly_type = "WITHIN_EXPECTED_RANGE"

        return {
            "normalized_score": round(normalized_score, 4),
            "discount_percentage": None,
            "price": price,
            "market_price": None,
            "anomaly_type": anomaly_type,
            "flags": flags
        }
