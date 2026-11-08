import React from "react";
import {
  LayoutDashboard,
  Sparkles,
  PackageSearch,
  Store,
  BarChart3,
  Sliders,
  AlertTriangle
} from "lucide-react";

export type NavTab = "overview" | "analyze" | "listings" | "merchants" | "reports" | "settings";

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  pendingCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab, pendingCount = 0 }) => {
  const navItems = [
    { id: "overview" as NavTab, label: "Overview", icon: LayoutDashboard },
    { id: "analyze" as NavTab, label: "Live Risk Scoring", icon: Sparkles, badge: "AI" },
    {
      id: "listings" as NavTab,
      label: "Listings & Triage",
      icon: PackageSearch,
      count: pendingCount > 0 ? pendingCount : undefined
    },
    { id: "merchants" as NavTab, label: "Merchant Intelligence", icon: Store },
    { id: "reports" as NavTab, label: "Risk Analytics & ML", icon: BarChart3 },
    { id: "settings" as NavTab, label: "API & Scoring Config", icon: Sliders },
  ];

  return (
    <aside style={{
      width: "240px",
      backgroundColor: "var(--bg-secondary)",
      borderRight: "1px solid var(--border-color)",
      display: "flex",
      flexDirection: "column",
      padding: "1.25rem 0.75rem",
      gap: "0.4rem"
    }}>
      <div style={{ padding: "0 0.5rem 0.75rem", fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.08em" }}>
        FRAUD INTELLIGENCE
      </div>

      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0.65rem 0.75rem",
              borderRadius: "8px",
              border: "none",
              background: isActive ? "rgba(59, 130, 246, 0.15)" : "transparent",
              color: isActive ? "#38bdf8" : "var(--text-secondary)",
              fontWeight: isActive ? 600 : 500,
              fontSize: "0.875rem",
              cursor: "pointer",
              transition: "all 0.15s ease",
              textAlign: "left"
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <Icon size={18} color={isActive ? "#38bdf8" : "var(--text-muted)"} />
              <span>{item.label}</span>
            </div>

            {item.badge && (
              <span style={{
                fontSize: "0.65rem",
                padding: "2px 6px",
                borderRadius: "4px",
                backgroundColor: "rgba(14, 165, 233, 0.2)",
                color: "var(--accent-cyan)",
                fontWeight: 700
              }}>
                {item.badge}
              </span>
            )}

            {item.count !== undefined && (
              <span style={{
                fontSize: "0.7rem",
                padding: "2px 6px",
                borderRadius: "9999px",
                backgroundColor: "var(--risk-high-bg)",
                color: "var(--risk-high)",
                border: "1px solid var(--risk-high-border)",
                fontWeight: 700
              }}>
                {item.count}
              </span>
            )}
          </button>
        );
      })}

      <div style={{ marginTop: "auto", padding: "1rem 0.5rem 0", borderTop: "1px solid var(--border-color)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "var(--text-muted)", fontSize: "0.75rem" }}>
          <AlertTriangle size={14} color="var(--risk-medium)" />
          <span>Automated Guardrails ON</span>
        </div>
      </div>
    </aside>
  );
};
