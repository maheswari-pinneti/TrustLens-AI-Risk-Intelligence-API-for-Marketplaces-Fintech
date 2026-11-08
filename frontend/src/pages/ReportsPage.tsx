import React, { useState, useEffect } from "react";
import {
  Download,
  Cpu,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  GitCompare,
  FileSpreadsheet
} from "lucide-react";
import { ApiClient } from "../api";
import { MlVsRulesComparison } from "../types";
import { RiskBadge } from "../components/RiskBadges";

export const ReportsPage: React.FC = () => {
  const [data, setData] = useState<MlVsRulesComparison | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await ApiClient.getMlVsRules();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Risk Analytics & ML Model Comparison
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
            Evaluate concordance between the deterministic rule engine and trained machine learning classifiers
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button onClick={loadData} className="btn-secondary">
            <RefreshCw size={15} /> Refresh Analysis
          </button>
          <a
            href={ApiClient.getExportCsvUrl()}
            download
            className="btn-primary"
            style={{ textDecoration: "none" }}
          >
            <Download size={16} /> Export CSV Audit Log
          </a>
        </div>
      </div>

      {/* Model Diagnostic KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1rem" }}>
        <div className="trust-card">
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>MODEL AGREEMENT RATE</div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--accent-cyan)", margin: "0.3rem 0" }}>
            {data?.agreement_rate_pct ? `${data.agreement_rate_pct.toFixed(1)}%` : "Loading..."}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Concordant rule vs ML classifications
          </span>
        </div>

        <div className="trust-card">
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>SAMPLES EVALUATED</div>
          <div style={{ fontSize: "2rem", fontWeight: 800, margin: "0.3rem 0" }}>
            {data?.total_analyzed || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
            Listings cross-validated
          </span>
        </div>

        <div className="trust-card" style={{ borderLeft: "4px solid var(--risk-low)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>FULL CONSENSUS</div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--risk-low)", margin: "0.3rem 0" }}>
            {data?.concordant_count || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Both engines agreed</span>
        </div>

        <div className="trust-card" style={{ borderLeft: "4px solid var(--risk-medium)" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 600 }}>DISCORDANT (EDGE CASES)</div>
          <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--risk-medium)", margin: "0.3rem 0" }}>
            {data?.discordant_count || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Warrants investigator review</span>
        </div>
      </div>

      {/* Cross-Validation Table */}
      <div className="trust-card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "1rem 1.25rem", borderBottom: "1px solid var(--border-color)", backgroundColor: "var(--bg-card)" }}>
          <h2 style={{ fontSize: "1rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <GitCompare size={18} color="var(--accent-blue)" /> Side-by-Side Diagnostic Breakdown
          </h2>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
            Compares rule engine points against the random forest probability distribution
          </p>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{
                backgroundColor: "var(--bg-secondary)",
                borderBottom: "1px solid var(--border-color)",
                color: "var(--text-muted)",
                fontSize: "0.75rem",
                textTransform: "uppercase"
              }}>
                <th style={{ padding: "0.85rem 1rem" }}>Listing</th>
                <th style={{ padding: "0.85rem 1rem" }}>Rule Risk Score</th>
                <th style={{ padding: "0.85rem 1rem" }}>Rule Risk Level</th>
                <th style={{ padding: "0.85rem 1rem" }}>ML Probability</th>
                <th style={{ padding: "0.85rem 1rem" }}>ML Prediction</th>
                <th style={{ padding: "0.85rem 1rem", textAlign: "right" }}>Consensus</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                    Loading comparison data...
                  </td>
                </tr>
              ) : (data?.comparison_samples || []).map((row) => (
                <tr key={row.listing_id} style={{ borderBottom: "1px solid var(--border-color)" }}>
                  <td style={{ padding: "0.85rem 1rem" }}>
                    <div style={{ fontWeight: 600, maxWidth: "280px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {row.title}
                    </div>
                    <div className="font-mono" style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                      {row.listing_id}
                    </div>
                  </td>

                  <td style={{ padding: "0.85rem 1rem" }}>
                    <span className="font-mono" style={{ fontWeight: 700 }}>
                      {row.rule_risk_score.toFixed(1)} / 100
                    </span>
                  </td>

                  <td style={{ padding: "0.85rem 1rem" }}>
                    <RiskBadge level={row.rule_risk_level} />
                  </td>

                  <td style={{ padding: "0.85rem 1rem" }}>
                    <span className="font-mono" style={{
                      fontWeight: 600,
                      color: row.ml_fraud_probability >= 50 ? "var(--risk-high)" : "var(--risk-low)"
                    }}>
                      {row.ml_fraud_probability.toFixed(1)}%
                    </span>
                  </td>

                  <td style={{ padding: "0.85rem 1rem" }}>
                    <span style={{
                      fontSize: "0.75rem",
                      fontWeight: 600,
                      padding: "2px 6px",
                      borderRadius: "4px",
                      backgroundColor: row.ml_prediction === "Fraudulent" ? "var(--risk-high-bg)" : "var(--risk-low-bg)",
                      color: row.ml_prediction === "Fraudulent" ? "var(--risk-high)" : "var(--risk-low)"
                    }}>
                      {row.ml_prediction}
                    </span>
                  </td>

                  <td style={{ padding: "0.85rem 1rem", textAlign: "right" }}>
                    {row.agreement ? (
                      <span style={{ color: "var(--risk-low)", fontSize: "0.75rem", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                        <CheckCircle size={14} /> Agreed
                      </span>
                    ) : (
                      <span style={{ color: "var(--risk-medium)", fontSize: "0.75rem", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                        <AlertTriangle size={14} /> Divergent
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
