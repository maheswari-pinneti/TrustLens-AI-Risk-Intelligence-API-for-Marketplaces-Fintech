import React from "react";
import { ShieldCheck, Activity, Key, ExternalLink, Cpu } from "lucide-react";
import { HealthStatus } from "../types";

interface NavbarProps {
  health: HealthStatus | null;
  onOpenSettings: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onOpenSettings }) => {
  return (
    <header style={{
      height: "64px",
      borderBottom: "1px solid var(--border-color)",
      backgroundColor: "var(--bg-secondary)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 1.5rem",
      position: "sticky",
      top: 0,
      zIndex: 50
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "8px",
          background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 15px rgba(14, 165, 233, 0.4)"
        }}>
          <ShieldCheck size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "1.15rem", fontWeight: 800, letterSpacing: "-0.02em" }}>
              Trust<span style={{ color: "var(--accent-cyan)" }}>Lens</span>
            </span>
            <span style={{
              fontSize: "0.65rem",
              background: "rgba(59, 130, 246, 0.15)",
              color: "var(--accent-blue)",
              padding: "2px 6px",
              borderRadius: "4px",
              fontWeight: 700
            }}>
              API v1.0
            </span>
          </div>
          <p style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
            AI Risk & Fraud Intelligence Platform
          </p>
        </div>
      </div>

      {/* Right Controls & Health */}
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        {/* ML Status Pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.4rem",
          fontSize: "0.75rem",
          padding: "4px 8px",
          borderRadius: "6px",
          background: health?.ml_model_loaded ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
          color: health?.ml_model_loaded ? "var(--risk-low)" : "var(--risk-medium)",
          border: `1px solid ${health?.ml_model_loaded ? "var(--risk-low-border)" : "var(--risk-medium-border)"}`
        }}>
          <Cpu size={14} />
          <span>ML Model: {health?.ml_model_loaded ? "Active (RF 1.0.0)" : "Standby"}</span>
        </div>

        {/* API Health Pill */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "0.4rem",
          fontSize: "0.75rem",
          padding: "4px 8px",
          borderRadius: "6px",
          background: health?.status === "HEALTHY" ? "rgba(16, 185, 129, 0.1)" : "rgba(244, 63, 94, 0.1)",
          color: health?.status === "HEALTHY" ? "var(--risk-low)" : "var(--risk-high)",
          border: `1px solid ${health?.status === "HEALTHY" ? "var(--risk-low-border)" : "var(--risk-high-border)"}`
        }}>
          <Activity size={14} />
          <span>API: {health?.status || "Connecting..."}</span>
        </div>

        {/* Swagger Docs */}
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-secondary"
          style={{ fontSize: "0.75rem", padding: "0.4rem 0.75rem", textDecoration: "none" }}
        >
          <ExternalLink size={14} />
          <span>Swagger Docs</span>
        </a>

        {/* Active Key button */}
        <button
          onClick={onOpenSettings}
          className="btn-secondary"
          style={{ fontSize: "0.75rem", padding: "0.4rem 0.75rem" }}
          title="Manage API Keys"
        >
          <Key size={14} />
          <span className="font-mono">tl_live_admin...</span>
        </button>
      </div>
    </header>
  );
};
