import React from "react";
import { ScoreBreakdown } from "../types";

interface FactorBreakdownProps {
  breakdown: ScoreBreakdown;
}

export const FactorBreakdown: React.FC<FactorBreakdownProps> = ({ breakdown }) => {
  const factors = [
    { label: "Price Anomaly", points: breakdown.price_anomaly_score, max: 30, color: "#f43f5e" },
    { label: "Fraud Keywords", points: breakdown.fraud_keywords_score, max: 25, color: "#f59e0b" },
    { label: "Image Similarity", points: breakdown.image_similarity_score, max: 20, color: "#38bdf8" },
    { label: "Seller Reputation", points: breakdown.seller_reputation_score, max: 15, color: "#a855f7" },
    { label: "Listing Behavior", points: breakdown.listing_behavior_score, max: 10, color: "#10b981" },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
      {factors.map((f) => {
        const pct = Math.min(100, Math.max(0, (f.points / f.max) * 100));
        return (
          <div key={f.label}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: "0.25rem" }}>
              <span style={{ color: "var(--text-secondary)", fontWeight: 500 }}>{f.label}</span>
              <span className="font-mono" style={{ fontWeight: 600, color: f.points > 0 ? f.color : "var(--text-muted)" }}>
                {f.points.toFixed(1)} / {f.max} pts
              </span>
            </div>
            <div style={{
              height: "7px",
              backgroundColor: "rgba(255, 255, 255, 0.06)",
              borderRadius: "9999px",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: `${pct}%`,
                backgroundColor: f.color,
                borderRadius: "9999px",
                transition: "width 0.4s ease-out"
              }} />
            </div>
          </div>
        );
      })}
    </div>
  );
};
