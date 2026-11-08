import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle, Clock, XCircle, ArrowUpRight } from "lucide-react";
import { RiskLevel, Recommendation, InvestigationStatus } from "../types";

export const RiskBadge: React.FC<{ level: RiskLevel | string; score?: number }> = ({ level, score }) => {
  const norm = level.toLowerCase();
  let badgeClass = "badge-low";
  let Icon = CheckCircle;

  if (norm === "high") {
    badgeClass = "badge-high";
    Icon = AlertCircle;
  } else if (norm === "medium") {
    badgeClass = "badge-medium";
    Icon = AlertTriangle;
  }

  return (
    <span className={`trust-badge ${badgeClass}`}>
      <Icon size={12} />
      <span>{level}</span>
      {score !== undefined && <span style={{ opacity: 0.85 }}>({Math.round(score)})</span>}
    </span>
  );
};

export const RecommendationBadge: React.FC<{ recommendation: Recommendation | string }> = ({ recommendation }) => {
  let style: React.CSSProperties = {
    fontSize: "0.75rem",
    padding: "3px 8px",
    borderRadius: "6px",
    fontWeight: 600,
    display: "inline-flex",
    alignItems: "center",
    gap: "0.3rem"
  };

  if (recommendation === "AUTO_REJECT") {
    return (
      <span style={{ ...style, background: "rgba(244, 63, 94, 0.15)", color: "var(--risk-high)", border: "1px solid var(--risk-high-border)" }}>
        <XCircle size={12} /> AUTO REJECT
      </span>
    );
  }
  if (recommendation === "AUTO_APPROVE") {
    return (
      <span style={{ ...style, background: "rgba(16, 185, 129, 0.15)", color: "var(--risk-low)", border: "1px solid var(--risk-low-border)" }}>
        <CheckCircle size={12} /> AUTO APPROVE
      </span>
    );
  }
  return (
    <span style={{ ...style, background: "rgba(245, 158, 11, 0.15)", color: "var(--risk-medium)", border: "1px solid var(--risk-medium-border)" }}>
      <Clock size={12} /> MANUAL REVIEW
    </span>
  );
};

export const StatusBadge: React.FC<{ status: InvestigationStatus | string }> = ({ status }) => {
  const s = status.toUpperCase();
  let color = "var(--text-muted)";
  let bg = "rgba(100, 116, 139, 0.15)";

  if (s === "APPROVED") {
    color = "var(--risk-low)";
    bg = "var(--risk-low-bg)";
  } else if (s === "REJECTED") {
    color = "var(--risk-high)";
    bg = "var(--risk-high-bg)";
  } else if (s === "ESCALATED") {
    color = "#c084fc";
    bg = "rgba(192, 132, 252, 0.15)";
  } else if (s === "PENDING_REVIEW") {
    color = "var(--risk-medium)";
    bg = "var(--risk-medium-bg)";
  }

  return (
    <span style={{
      fontSize: "0.7rem",
      padding: "2px 8px",
      borderRadius: "4px",
      fontWeight: 600,
      color,
      backgroundColor: bg,
      textTransform: "uppercase"
    }}>
      {status.replace("_", " ")}
    </span>
  );
};
