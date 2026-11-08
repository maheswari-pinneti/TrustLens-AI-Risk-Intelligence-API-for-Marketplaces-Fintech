import React, { useState } from "react";
import {
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  Info,
  ShieldAlert
} from "lucide-react";
import { ApiClient } from "../api";
import { AnalyzeRequest, AnalyzeResponse } from "../types";
import { RiskBadge, RecommendationBadge } from "../components/RiskBadges";
import { FactorBreakdown } from "../components/FactorBreakdown";

const DEMO_PRESETS: { label: string; data: AnalyzeRequest }[] = [
  {
    label: "Fake Nike Jordans (Counterfeit)",
    data: {
      title: "Nike Air Jordan 1 Retro High Cheap Replica",
      description: "Brand new 1:1 replica shoes first copy ua quality whatsapp me for orders must go today",
      price: 45.0,
      market_price: 210.0,
      category: "Footwear & Apparel",
      merchant_id: "merch_quick_deals",
      seller_rating: 1.4,
      seller_account_age_days: 3,
      seller_complaints_count: 8
    }
  },
  {
    label: "Stolen iPhone 15 Pro (High Anomaly)",
    data: {
      title: "Apple iPhone 15 Pro Max 256GB Bypassed iCloud Locked",
      description: "Clean IMEI phone bypassed icloud cash only or telegram me wire transfer only urgent sale",
      price: 180.0,
      market_price: 1199.0,
      category: "Smartphones",
      merchant_id: "merch_burner_99",
      seller_rating: 1.2,
      seller_account_age_days: 1,
      seller_complaints_count: 5
    }
  },
  {
    label: "Authentic Sony Headphones (Genuine)",
    data: {
      title: "Sony WH-1000XM5 Wireless Noise Canceling Headphones",
      description: "Original retail packaging, bought from authorized retailer with proof of purchase and warranty.",
      price: 349.0,
      market_price: 399.0,
      category: "Electronics",
      merchant_id: "merch_verified_pro",
      seller_rating: 4.9,
      seller_account_age_days: 420,
      seller_complaints_count: 0
    }
  },
  {
    label: "Luxury Watch Superclone (Extreme Discrepancy)",
    data: {
      title: "Rolex Submariner Date AAA Grade Superclone",
      description: "Master copy mirror quality looks authentic clone watch no receipt cash only",
      price: 280.0,
      market_price: 14200.0,
      category: "Watches & Jewelry",
      merchant_id: "merch_stealth",
      seller_rating: 2.1,
      seller_account_age_days: 6,
      seller_complaints_count: 4
    }
  }
];

export const AnalyzePage: React.FC = () => {
  const [formData, setFormData] = useState<AnalyzeRequest>({
    title: "",
    description: "",
    price: 100,
    market_price: 500,
    category: "Footwear & Apparel",
    merchant_id: "merch_demo",
    seller_rating: 3.5,
    seller_account_age_days: 15,
    seller_complaints_count: 2
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelectPreset = (preset: AnalyzeRequest) => {
    setFormData(preset);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await ApiClient.analyzeListing(formData, true);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to analyze listing");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div>
        <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
          Live Listing Risk Intelligence Scanner
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
          Execute multi-dimensional fraud checks: price anomalies, counterfeit keywords, seller risk, and ML classification
        </p>
      </div>

      {/* Demo Preset Bar */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "0.6rem",
        overflowX: "auto",
        padding: "0.75rem 1rem",
        background: "var(--bg-secondary)",
        borderRadius: "8px",
        border: "1px solid var(--border-color)"
      }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", whiteSpace: "nowrap" }}>
          QUICK SCENARIOS:
        </span>
        {DEMO_PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            onClick={() => handleSelectPreset(p.data)}
            className="btn-secondary"
            style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem", whiteSpace: "nowrap" }}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Main Split Layout */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1.2fr 1fr",
        gap: "1.5rem"
      }}>
        {/* Form Panel */}
        <div className="trust-card">
          <h2 style={{ fontSize: "1.05rem", fontWeight: 600, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Layers size={18} color="var(--accent-cyan)" /> Listing Attributes
          </h2>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                Product Title *
              </label>
              <input
                type="text"
                required
                style={{ width: "100%" }}
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g. Nike Air Jordan 1 Retro High"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                Product Description *
              </label>
              <textarea
                required
                rows={3}
                style={{ width: "100%", resize: "vertical" }}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Paste full product listing copy..."
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Listing Price ($) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  style={{ width: "100%" }}
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) || 0 })}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Market Benchmark ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  style={{ width: "100%" }}
                  value={formData.market_price || ""}
                  onChange={(e) => setFormData({ ...formData, market_price: parseFloat(e.target.value) || undefined })}
                  placeholder="Estimated retail"
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Category
                </label>
                <select
                  style={{ width: "100%" }}
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  <option value="Footwear & Apparel">Footwear & Apparel</option>
                  <option value="Luxury Goods">Luxury Goods</option>
                  <option value="Smartphones">Smartphones</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Watches & Jewelry">Watches & Jewelry</option>
                  <option value="Perfume & Cosmetics">Perfume & Cosmetics</option>
                  <option value="General">General</option>
                </select>
              </div>
            </div>

            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "0.85rem", display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Seller Rating (0-5)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="5"
                  style={{ width: "100%" }}
                  value={formData.seller_rating ?? ""}
                  onChange={(e) => setFormData({ ...formData, seller_rating: parseFloat(e.target.value) })}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Account Age (Days)
                </label>
                <input
                  type="number"
                  min="0"
                  style={{ width: "100%" }}
                  value={formData.seller_account_age_days ?? ""}
                  onChange={(e) => setFormData({ ...formData, seller_account_age_days: parseInt(e.target.value) || 0 })}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 500, marginBottom: "0.3rem" }}>
                  Complaints Count
                </label>
                <input
                  type="number"
                  min="0"
                  style={{ width: "100%" }}
                  value={formData.seller_complaints_count ?? ""}
                  onChange={(e) => setFormData({ ...formData, seller_complaints_count: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            {error && (
              <div style={{ padding: "0.6rem 0.85rem", background: "var(--risk-high-bg)", color: "var(--risk-high)", border: "1px solid var(--risk-high-border)", borderRadius: "6px", fontSize: "0.8rem" }}>
                {error}
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary" style={{ justifyContent: "center", padding: "0.75rem" }}>
              {loading ? "Evaluating Risk Vectors..." : "Analyze Product Listing"}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="trust-card" style={{ display: "flex", flexDirection: "column" }}>
          <h2 style={{ fontSize: "1.05rem", fontWeight: 600, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Sparkles size={18} color="var(--accent-blue)" /> Risk Evaluation Report
          </h2>

          {!result ? (
            <div style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--text-muted)",
              textAlign: "center",
              padding: "2rem"
            }}>
              <Info size={40} style={{ opacity: 0.4, marginBottom: "0.75rem" }} />
              <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>No active scan results</p>
              <p style={{ fontSize: "0.75rem", marginTop: "0.25rem", maxWidth: "260px" }}>
                Select a preset scenario above or submit product attributes to generate explainable fraud analysis.
              </p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
              {/* Score Hero Box */}
              <div style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "1rem 1.25rem",
                borderRadius: "10px",
                backgroundColor: "var(--bg-secondary)",
                border: "1px solid var(--border-color)"
              }}>
                <div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>COMPOSITE RISK SCORE</div>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "0.3rem" }}>
                    <span style={{ fontSize: "2.4rem", fontWeight: 800 }}>{result.risk_score}</span>
                    <span style={{ fontSize: "1rem", color: "var(--text-muted)" }}>/ 100</span>
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.4rem" }}>
                  <RiskBadge level={result.risk_level} />
                  <RecommendationBadge recommendation={result.recommendation} />
                </div>
              </div>

              {/* ML Layer Indicator */}
              {result.ml_prediction && (
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.6rem 0.85rem",
                  borderRadius: "6px",
                  background: result.ml_prediction === "Fraudulent" ? "rgba(244, 63, 94, 0.1)" : "rgba(16, 185, 129, 0.1)",
                  border: `1px solid ${result.ml_prediction === "Fraudulent" ? "var(--risk-high-border)" : "var(--risk-low-border)"}`,
                  fontSize: "0.8rem"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <Cpu size={16} color={result.ml_prediction === "Fraudulent" ? "var(--risk-high)" : "var(--risk-low)"} />
                    <span>ML Classifier Prediction: <strong>{result.ml_prediction}</strong></span>
                  </div>
                  <span className="font-mono" style={{ fontWeight: 600 }}>
                    {result.ml_fraud_probability ? `${(result.ml_fraud_probability * 100).toFixed(1)}% prob` : ""}
                  </span>
                </div>
              )}

              {/* Point Contribution Breakdown */}
              <div>
                <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.6rem" }}>
                  WEIGHTED FACTOR CONTRIBUTION
                </div>
                <FactorBreakdown breakdown={result.score_breakdown} />
              </div>

              {/* Triggered Flags */}
              <div>
                <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.6rem" }}>
                  TRIGGERED RISK INDICATORS ({result.flags.length})
                </div>
                {result.flags.length === 0 ? (
                  <div style={{ fontSize: "0.8rem", color: "var(--risk-low)", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <CheckCircle2 size={16} /> No risk indicators triggered. Listing cleared.
                  </div>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                    {result.flags.map((flag, idx) => (
                      <div
                        key={idx}
                        style={{
                          fontSize: "0.78rem",
                          padding: "0.4rem 0.65rem",
                          backgroundColor: "var(--bg-secondary)",
                          borderRadius: "6px",
                          borderLeft: "3px solid var(--risk-high)",
                          display: "flex",
                          alignItems: "center",
                          gap: "0.4rem"
                        }}
                      >
                        <ShieldAlert size={14} color="var(--risk-high)" />
                        <span>{flag}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Summary Explainability */}
              {result.evidence?.summary_explanation && (
                <div style={{
                  padding: "0.75rem",
                  borderRadius: "8px",
                  backgroundColor: "rgba(59, 130, 246, 0.08)",
                  border: "1px solid rgba(59, 130, 246, 0.2)",
                  fontSize: "0.8rem",
                  color: "var(--text-secondary)"
                }}>
                  <strong style={{ color: "var(--text-primary)" }}>Reasoning: </strong>
                  {result.evidence.summary_explanation}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
