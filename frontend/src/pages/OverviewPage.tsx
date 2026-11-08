import React from "react";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Users,
  TrendingUp,
  Activity,
  ArrowRight,
  Sparkles,
  RefreshCw
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { RiskSummary } from "../types";
import { RiskBadge } from "../components/RiskBadges";

interface OverviewPageProps {
  summary: RiskSummary | null;
  loading: boolean;
  onRefresh: () => void;
  onNavigateAnalyze: () => void;
  onNavigateListings: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  summary,
  loading,
  onRefresh,
  onNavigateAnalyze,
  onNavigateListings,
}) => {
  if (loading && !summary) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "60vh" }}>
        <RefreshCw className="animate-spin" size={32} color="var(--accent-cyan)" />
      </div>
    );
  }

  const pieData = [
    { name: "Low Risk", value: summary?.low_risk_listings || 0, color: "#10b981" },
    { name: "Medium Risk", value: summary?.medium_risk_listings || 0, color: "#f59e0b" },
    { name: "High Risk", value: summary?.high_risk_listings || 0, color: "#f43f5e" },
  ];

  const categoryData = summary?.category_risk_distribution || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Risk Intelligence Overview
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
            Real-time marketplace fraud analytics, anomaly tracking, and merchant surveillance
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button onClick={onRefresh} className="btn-secondary">
            <RefreshCw size={15} /> Refresh Data
          </button>
          <button onClick={onNavigateAnalyze} className="btn-primary">
            <Sparkles size={16} /> Run Fraud Scan
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
        gap: "1rem"
      }}>
        {/* Card 1 */}
        <div className="trust-card">
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>TOTAL ANALYZED</span>
            <Activity size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0" }}>
            {summary?.total_listings_analyzed || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Marketplace listings</span>
        </div>

        {/* Card 2 */}
        <div className="trust-card" style={{ borderLeft: "4px solid var(--risk-high)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--risk-high)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>HIGH RISK FLAGS</span>
            <ShieldAlert size={18} />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0", color: "var(--risk-high)" }}>
            {summary?.high_risk_listings || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Requires action / rejection</span>
        </div>

        {/* Card 3 */}
        <div className="trust-card" style={{ borderLeft: "4px solid var(--risk-medium)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--risk-medium)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>MEDIUM RISK</span>
            <AlertTriangle size={18} />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0", color: "var(--risk-medium)" }}>
            {summary?.medium_risk_listings || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Pending manual triage</span>
        </div>

        {/* Card 4 */}
        <div className="trust-card" style={{ borderLeft: "4px solid var(--risk-low)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--risk-low)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>CLEARED (LOW)</span>
            <ShieldCheck size={18} />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0", color: "var(--risk-low)" }}>
            {summary?.low_risk_listings || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Auto-approved safely</span>
        </div>

        {/* Card 5 */}
        <div className="trust-card">
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>TRACKED MERCHANTS</span>
            <Users size={18} color="var(--accent-purple)" />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0" }}>
            {summary?.total_merchants_tracked || 0}
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Risk profiles monitored</span>
        </div>

        {/* Card 6 */}
        <div className="trust-card">
          <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
            <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>AVG RISK SCORE</span>
            <TrendingUp size={18} color="var(--accent-blue)" />
          </div>
          <div style={{ fontSize: "1.8rem", fontWeight: 700, margin: "0.4rem 0" }}>
            {summary?.average_risk_score.toFixed(1) || 0} <span style={{ fontSize: "1rem", color: "var(--text-muted)" }}>/ 100</span>
          </div>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Marketplace baseline</span>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "2fr 1fr",
        gap: "1.25rem"
      }}>
        {/* Category Risk Bar Chart */}
        <div className="trust-card">
          <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.25rem" }}>
            Average Risk Score by Category
          </h2>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "1.25rem" }}>
            Identifies marketplace verticals facing elevated counterfeit and price manipulation exposure
          </p>
          <div style={{ width: "100%", height: 260 }}>
            <ResponsiveContainer>
              <BarChart data={categoryData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <XAxis dataKey="category" stroke="#64748b" fontSize={11} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748b" fontSize={11} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", borderRadius: "8px", fontSize: "0.8rem" }}
                  formatter={(value: any) => [`${value} pts`, "Avg Risk"]}
                />
                <Bar dataKey="avg_risk" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Level Distribution Donut */}
        <div className="trust-card">
          <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.25rem" }}>
            Risk Distribution
          </h2>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
            Active classification tiers
          </p>
          <div style={{ width: "100%", height: 180 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", borderRadius: "8px", fontSize: "0.8rem" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: "flex", justifyContent: "space-around", fontSize: "0.75rem", marginTop: "0.5rem" }}>
            {pieData.map((p) => (
              <div key={p.name} style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <div style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: p.color }} />
                <span style={{ color: "var(--text-secondary)" }}>{p.name}: <strong>{p.value}</strong></span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Alerts Feed & Top Keywords */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "1.5fr 1fr",
        gap: "1.25rem"
      }}>
        {/* Recent Critical Alerts */}
        <div className="trust-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div>
              <h2 style={{ fontSize: "1rem", fontWeight: 600 }}>Active Fraud Alerts</h2>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Critical threshold breaches requiring compliance intervention
              </p>
            </div>
            <button onClick={onNavigateListings} className="btn-secondary" style={{ fontSize: "0.75rem", padding: "0.35rem 0.75rem" }}>
              <span>View All</span> <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {(summary?.recent_alerts || []).slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0.65rem 0.85rem",
                  backgroundColor: "var(--bg-secondary)",
                  borderRadius: "8px",
                  borderLeft: "3px solid var(--risk-high)"
                }}
              >
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    <span style={{
                      fontSize: "0.65rem",
                      fontWeight: 700,
                      color: "var(--risk-high)",
                      backgroundColor: "var(--risk-high-bg)",
                      padding: "2px 5px",
                      borderRadius: "4px"
                    }}>
                      {alert.severity}
                    </span>
                    <span style={{ fontSize: "0.825rem", fontWeight: 500 }}>
                      {alert.message}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
                    Listing ID: <span className="font-mono">{alert.listing_id || "N/A"}</span> • Merchant: <span className="font-mono">{alert.merchant_id || "N/A"}</span>
                  </div>
                </div>
                <button
                  onClick={onNavigateListings}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent-cyan)",
                    cursor: "pointer",
                    fontSize: "0.75rem",
                    fontWeight: 600
                  }}
                >
                  Triage
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Top Triggered Keywords */}
        <div className="trust-card">
          <h2 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "0.25rem" }}>
            Top Triggered Fraud Keywords
          </h2>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "1rem" }}>
            Most frequent counterfeit and deceptive terms detected
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {(summary?.top_fraud_keywords || []).slice(0, 6).map((item, i) => (
              <div
                key={item.keyword}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "0.45rem 0.6rem",
                  backgroundColor: "var(--bg-secondary)",
                  borderRadius: "6px",
                  fontSize: "0.8rem"
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ color: "var(--text-muted)", fontSize: "0.75rem", fontWeight: 700, width: "16px" }}>
                    #{i + 1}
                  </span>
                  <span className="font-mono" style={{ color: "#fca5a5", fontWeight: 600 }}>
                    "{item.keyword}"
                  </span>
                </div>
                <span style={{
                  fontSize: "0.7rem",
                  backgroundColor: "rgba(255, 255, 255, 0.08)",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  fontWeight: 600
                }}>
                  {item.occurrences} hits
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
