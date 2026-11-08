# 01 - Project Overview

## 1. Executive Summary
**TrustLens** is a production-oriented AI Risk Intelligence API and compliance dashboard built to detect counterfeit product listings, severe price manipulation, duplicate catalog imagery, and merchant fraud patterns across e-commerce marketplaces and fintech platforms.

Online marketplaces process hundreds of thousands of listing events daily. Manual moderation is slow, unscalable, and error-prone. Fraudsters frequently exploit gaps by deploying burner merchant accounts, advertising "1:1 replica" or stolen goods at steep discounts, and siphoning buyers toward unmonitored off-platform wire transfers. TrustLens solves this challenge through an **explainable, multi-dimensional risk scoring engine** combined with machine learning validation.

---

## 2. Core Problem Dimensions

| Problem Dimension | Marketplace Impact | TrustLens Detection Mechanism |
| :--- | :--- | :--- |
| **Counterfeit & Replica Goods** | Trademark infringements, buyer chargebacks, platform liability. | Substring & token regex detector with configurable keyword severities (1:1, replica, mirror quality). |
| **Price Anomalies** | Fraudulent bait listings, stolen goods camouflage, price gouging. | Mathematical discount deviation analysis against market price benchmarks and category minimums. |
| **Catalog Image Duplication** | Reused stock photos across burner accounts, stolen intellectual property. | Perceptual 64-bit image hashing (dHash/pHash) and bitwise Hamming distance cross-referencing. |
| **Merchant Burner Accounts** | Hit-and-run sellers that abandon accounts before chargeback cycles. | Multi-factor tenure, customer dispute counts, historical flagged listing ratios. |
| **Off-Platform Leakage** | Buyers lured to Telegram, WhatsApp, or wire transfer scams. | Behavioral NLP scanning for emails, phone numbers, external URLs, and urgency manipulation. |

---

## 3. Key Design Philosophy
- **Explainability First**: Every risk score (0 to 100) is traceable down to individual mathematical points contributed by each factor.
- **Defense in Depth**: Rule-based guardrails catch deterministic policy violations immediately, while machine learning models identify non-linear feature interactions.
- **Human-in-the-Loop**: Triage workflows enable compliance investigators to inspect forensic evidence, add review notes, and disposition listings (`APPROVE`, `REJECT`, `ESCALATE`).
