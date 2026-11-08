# 04 - Risk Scoring Engine

## 1. Mathematical Formulation

The composite risk score $S \in [0, 100]$ is computed as a weighted summation of five normalized sub-scores $s_i \in [0.0, 1.0]$:

$$S = \min\left(100, \sum_{i=1}^{5} w_i \cdot s_i\right)$$

Where:
- $w_1 = 30.0$ (Price Anomaly Weight)
- $w_2 = 25.0$ (Fraud Keywords Weight)
- $w_3 = 20.0$ (Image Similarity Weight)
- $w_4 = 15.0$ (Seller Reputation Weight)
- $w_5 = 10.0$ (Listing Behavioral Weight)
- $\sum_{i=1}^5 w_i = 100.0$

---

## 2. Risk Classification Boundaries

| Risk Level | Score Range | Operational Disposition | Description |
| :--- | :--- | :--- | :--- |
| **Low Risk** | 0.0 – 29.0 pts | `AUTO_APPROVE` | Attributes within safe marketplace baseline. Listing published immediately. |
| **Medium Risk** | 30.0 – 59.0 pts | `MANUAL_REVIEW` | Mild to moderate anomalies detected. Queued for investigator verification. |
| **High Risk** | 60.0 – 100.0 pts | `AUTO_REJECT` | Severe counterfeit indicators, extreme price deviation, or repeat fraud patterns. |

---

## 3. Factor Decomposition

### A. Price Anomaly ($w = 30$)
- Compares listing price $P$ against market price benchmark $M$:
  $$\text{Discount \%} = \frac{M - P}{M} \times 100$$
- $\text{Discount} \ge 90\% \implies s_1 = 1.0$ (Critical underpricing)
- $\text{Discount} \in [75\%, 90\%) \implies s_1 \in [0.85, 1.0]$
- $\text{Discount} \in [55\%, 75\%) \implies s_1 \in [0.55, 0.85]$
- Price Gouging ($P > 3.5 \times M$) $\implies s_1 = 0.65$

### B. Fraud Keywords ($w = 25$)
- Multi-token regex scanning with severity hierarchy:
  - $\text{HIGH (1.0)}$: `replica`, `1:1 replica`, `counterfeit`, `superclone`, `stolen`, `bypassed icloud`, `wire transfer only`.
  - $\text{MEDIUM (0.6)}$: `oem factory`, `factory reject`, `defective batch`, `dm on instagram`.
  - $\text{LOW (0.3)}$: `no receipt`, `must go today`, `urgent sale`.
- Title tokens receive a $1.2\times$ multiplier due to prominence.

### C. Image Perceptual Similarity ($w = 20$)
- 64-bit difference hash (dHash) and perceptual hash (pHash) bit comparison:
  $$\text{Similarity} = \frac{64 - \text{Hamming Distance}}{64}$$
- $\text{Distance} = 0 \implies s_3 = 1.0$ (100% exact duplicate)
- $\text{Distance} \le 4 \implies s_3 = 0.85$ (Compressed or cropped near-duplicate)

### D. Seller Reputation ($w = 15$)
- Multi-signal weighted formula:
  $$s_4 = 0.40 \cdot s_{\text{rating}} + 0.25 \cdot s_{\text{age}} + 0.20 \cdot s_{\text{complaints}} + 0.15 \cdot s_{\text{history}} + \text{unverified\_penalty}$$

### E. Listing Behavior ($w = 10$)
- Detects uppercase shouting ratio ($>65\%$), excessive punctuation ($>5$ exclamation marks), direct phone numbers, external URLs, and burst listing creation velocity.
