import React, { useState } from "react";
import {
  X,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  Cpu,
  Layers,
  Store,
  DollarSign
} from "lucide-react";
import { ListingItem, InvestigationStatus } from "../types";
import { RiskBadge, StatusBadge } from "./RiskBadges";
import { FactorBreakdown } from "./FactorBreakdown";
import { ApiClient } from "../api";

interface InvestigationModalProps {
  listing: ListingItem;
  onClose: () => void;
  onUpdated: (updated: ListingItem) => void;
}

export const InvestigationModal: React.FC<InvestigationModalProps> = ({
  listing,
  onClose,
  onUpdated,
}) => {
  const [notes, setNotes] = useState(listing.review_notes || "");
  const [submitting, setSubmitting] = useState(false);
  const [currentListing, setCurrentListing] = useState<ListingItem>(listing);

  const handleDecision = async (status: InvestigationStatus) => {
    setSubmitting(true);
    try {
      const updated = await ApiClient.submitDecision(currentListing.listing_id, status, notes);
      setCurrentListing(updated);
      onUpdated(updated);
    } catch (err: any) {
      alert(err.message || "Failed to update listing disposition");
    } finally {
      setSubmitting(false);
    }
  };

  const evidence = currentListing.evidence || {};
  const breakdown = currentListing.score_breakdown as any || {};

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(0, 0, 0, 0.75)",
      backdropFilter: "blur(4px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
      padding: "1.5rem"
    }}>
      <div style={{
        backgroundColor: "var(--bg-secondary)",
        border: "1px solid var(--border-color)",
        borderRadius: "14px",
        width: "100%",
        maxWidth: "850px",
        maxHeight: "90vh",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.6)",
        overflow: "hidden"
      }}>
        {/* Modal Header */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "1rem 1.5rem",
          borderBottom: "1px solid var(--border-color)",
          backgroundColor: "var(--bg-card)"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{
              width: "32px",
              height: "32px",
              borderRadius: "6px",
              backgroundColor: "rgba(244, 63, 94, 0.15)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <ShieldAlert size={18} color="var(--risk-high)" />
            </div>
            <div>
              <div style={{ fontSize: "1.1rem", fontWeight: 700 }}>
                Listing Risk Investigation
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }} className="font-mono">
                ID: {currentListing.listing_id} • Merchant: {currentListing.merchant_id}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <RiskBadge level={currentListing.risk_level} score={currentListing.risk_score} />
            <StatusBadge status={currentListing.status} />
            <button
              onClick={onClose}
              style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "4px" }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div style={{ padding: "1.5rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Product Overview Card */}
          <div className="trust-card" style={{ padding: "1rem" }}>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 600, marginBottom: "0.4rem" }}>
              {currentListing.title}
            </h3>
            <p style={{ fontSize: "0.825rem", color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: "0.75rem" }}>
              {currentListing.description}
            </p>

            <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8rem", borderTop: "1px solid var(--border-color)", paddingTop: "0.6rem" }}>
              <div>
                <span style={{ color: "var(--text-muted)" }}>Category: </span>
                <strong>{currentListing.category}</strong>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)" }}>Listing Price: </span>
                <strong className="font-mono">${currentListing.price.toFixed(2)}</strong>
              </div>
              <div>
                <span style={{ color: "var(--text-muted)" }}>Market Benchmark: </span>
                <strong className="font-mono">${currentListing.market_price ? currentListing.market_price.toFixed(2) : "N/A"}</strong>
              </div>
            </div>
          </div>

          {/* Grid Breakdown */}
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "1.25rem" }}>
            {/* Factor Scores */}
            <div className="trust-card" style={{ padding: "1rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.85rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Layers size={16} color="var(--accent-cyan)" /> Weighted Factor Attribution
              </div>
              <FactorBreakdown breakdown={{
                price_anomaly_score: breakdown.price_anomaly_score || 0,
                fraud_keywords_score: breakdown.fraud_keywords_score || 0,
                image_similarity_score: breakdown.image_similarity_score || 0,
                seller_reputation_score: breakdown.seller_reputation_score || 0,
                listing_behavior_score: breakdown.listing_behavior_score || 0,
                total_score: breakdown.total_score || currentListing.risk_score
              }} />
            </div>

            {/* ML & Forensic Evidence */}
            <div className="trust-card" style={{ padding: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <Cpu size={16} color="var(--accent-purple)" /> Machine Learning Diagnostics
              </div>

              <div style={{
                padding: "0.65rem 0.85rem",
                borderRadius: "6px",
                background: currentListing.ml_prediction === "Fraudulent" ? "var(--risk-high-bg)" : "var(--risk-low-bg)",
                border: `1px solid ${currentListing.ml_prediction === "Fraudulent" ? "var(--risk-high-border)" : "var(--risk-low-border)"}`,
                fontSize: "0.8rem"
              }}>
                <div>Classifier: <strong>{currentListing.ml_prediction || "Analyzed"}</strong></div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>
                  Fraud Probability: {currentListing.ml_fraud_probability ? `${(currentListing.ml_fraud_probability * 100).toFixed(1)}%` : "N/A"}
                </div>
              </div>

              {/* Seller metrics */}
              <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
                <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>Seller Metrics On Record:</div>
                <div>• Rating: {evidence.seller?.rating ? `${evidence.seller.rating}/5.0` : "Unknown"}</div>
                <div>• Account Tenure: {evidence.seller?.account_age_days ? `${evidence.seller.account_age_days} days` : "Unknown"}</div>
                <div>• Recorded Complaints: {evidence.seller?.complaints_count ?? 0} disputes</div>
              </div>
            </div>
          </div>

          {/* Triggered Flags */}
          <div className="trust-card" style={{ padding: "1rem" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <ShieldAlert size={16} color="var(--risk-high)" /> Triggered Flags & Evidence Details ({currentListing.flags.length})
            </div>
            {currentListing.flags.length === 0 ? (
              <p style={{ fontSize: "0.8rem", color: "var(--risk-low)" }}>No risk rules triggered.</p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                {currentListing.flags.map((flag, i) => (
                  <div
                    key={i}
                    style={{
                      fontSize: "0.8rem",
                      padding: "0.45rem 0.75rem",
                      backgroundColor: "var(--bg-primary)",
                      borderRadius: "6px",
                      borderLeft: "3px solid var(--risk-high)"
                    }}
                  >
                    {flag}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Investigator Action Form */}
          <div style={{
            backgroundColor: "var(--bg-card)",
            padding: "1rem",
            borderRadius: "10px",
            border: "1px solid var(--border-color)",
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem"
          }}>
            <label style={{ fontSize: "0.85rem", fontWeight: 600 }}>
              Investigator Review Notes & Disposition Action
            </label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Record forensic review findings, counterfeit verification, or customer dispute outcome..."
              style={{ width: "100%" }}
            />

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleDecision("REJECTED")}
                style={{
                  background: "var(--risk-high)",
                  color: "white",
                  border: "none",
                  padding: "0.55rem 1rem",
                  borderRadius: "6px",
                  fontWeight: 600,
                  fontSize: "0.8rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}
              >
                <XCircle size={15} /> Confirm Reject
              </button>

              <button
                type="button"
                disabled={submitting}
                onClick={() => handleDecision("ESCALATED")}
                style={{
                  background: "rgba(192, 132, 252, 0.2)",
                  color: "#c084fc",
                  border: "1px solid rgba(192, 132, 252, 0.4)",
                  padding: "0.55rem 1rem",
                  borderRadius: "6px",
                  fontWeight: 600,
                  fontSize: "0.8rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}
              >
                <AlertTriangle size={15} /> Escalate to Tier 2
              </button>

              <button
                type="button"
                disabled={submitting}
                onClick={() => handleDecision("APPROVED")}
                style={{
                  background: "var(--risk-low)",
                  color: "white",
                  border: "none",
                  padding: "0.55rem 1rem",
                  borderRadius: "6px",
                  fontWeight: 600,
                  fontSize: "0.8rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem"
                }}
              >
                <CheckCircle size={15} /> Approve Listing
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
