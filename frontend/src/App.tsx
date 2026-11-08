import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { Sidebar, NavTab } from "./components/Sidebar";
import { OverviewPage } from "./pages/OverviewPage";
import { AnalyzePage } from "./pages/AnalyzePage";
import { ListingsPage } from "./pages/ListingsPage";
import { MerchantsPage } from "./pages/MerchantsPage";
import { ReportsPage } from "./pages/ReportsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { InvestigationModal } from "./components/InvestigationModal";
import { ApiClient } from "./api";
import { HealthStatus, RiskSummary, ListingItem } from "./types";

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>("overview");
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [summary, setSummary] = useState<RiskSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [selectedListing, setSelectedListing] = useState<ListingItem | null>(null);

  const fetchHealthAndSummary = async () => {
    try {
      const h = await ApiClient.getHealth();
      setHealth(h);
    } catch (e) {
      console.warn("Could not reach backend health endpoint:", e);
    }

    setLoadingSummary(true);
    try {
      const s = await ApiClient.getRiskSummary();
      setSummary(s);
    } catch (e) {
      console.warn("Could not load risk summary:", e);
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    fetchHealthAndSummary();
    const interval = setInterval(fetchHealthAndSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", backgroundColor: "var(--bg-primary)" }}>
      {/* Top Navigation */}
      <Navbar
        health={health}
        onOpenSettings={() => setActiveTab("settings")}
      />

      {/* Main Body Split */}
      <div style={{ display: "flex", flex: 1 }}>
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          pendingCount={summary?.pending_investigation_count}
        />

        {/* Content Pane */}
        <main style={{ flex: 1, padding: "1.75rem", overflowY: "auto", maxWidth: "1400px" }}>
          {activeTab === "overview" && (
            <OverviewPage
              summary={summary}
              loading={loadingSummary}
              onRefresh={fetchHealthAndSummary}
              onNavigateAnalyze={() => setActiveTab("analyze")}
              onNavigateListings={() => setActiveTab("listings")}
            />
          )}

          {activeTab === "analyze" && <AnalyzePage />}

          {activeTab === "listings" && (
            <ListingsPage onSelectListing={(l) => setSelectedListing(l)} />
          )}

          {activeTab === "merchants" && (
            <MerchantsPage onSelectListing={(l) => setSelectedListing(l)} />
          )}

          {activeTab === "reports" && <ReportsPage />}

          {activeTab === "settings" && <SettingsPage />}
        </main>
      </div>

      {/* Forensic Investigation Modal */}
      {selectedListing && (
        <InvestigationModal
          listing={selectedListing}
          onClose={() => setSelectedListing(null)}
          onUpdated={(updated) => {
            setSelectedListing(updated);
            fetchHealthAndSummary();
          }}
        />
      )}
    </div>
  );
}

export default App;
