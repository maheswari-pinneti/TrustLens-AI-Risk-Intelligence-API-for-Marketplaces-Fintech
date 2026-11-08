import React, { useState, useEffect } from "react";
import {
  Store,
  Search,
  Star,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Eye,
  CheckCircle2,
  XCircle
} from "lucide-react";
import { ApiClient } from "../api";
import { MerchantItem, ListingItem } from "../types";
import { RiskBadge } from "../components/RiskBadges";

interface MerchantsPageProps {
  onSelectListing: (listing: ListingItem) => void;
}

export const MerchantsPage: React.FC<MerchantsPageProps> = ({ onSelectListing }) => {
  const [merchants, setMerchants] = useState<MerchantItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  // Selected merchant detail
  const [selectedMerchant, setSelectedMerchant] = useState<{
    merchant: MerchantItem;
    recent_listings: ListingItem[];
  } | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const loadMerchants = async () => {
    setLoading(true);
    try {
      const res = await ApiClient.getMerchants({
        skip: page * pageSize,
        limit: pageSize,
        risk_level: riskLevel || undefined,
        search: search || undefined
      });
      setMerchants(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMerchants();
  }, [page, riskLevel]);

  const handleInspectMerchant = async (merchantId: string) => {
    setLoadingDetail(true);
    try {
      const data = await ApiClient.getMerchantDetails(merchantId);
      setSelectedMerchant(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Merchant Intelligence & Risk Surveillance
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
            Analyze seller profiles, repeat complaint ratios, flagged listing histories, and trust ratings
          </p>
        </div>
        <button onClick={loadMerchants} className="btn-secondary">
          <RefreshCw size={15} /> Refresh Merchants
        </button>
      </div>

      {/* Search Toolbar */}
      <div className="trust-card" style={{ padding: "0.85rem 1rem", display: "flex", gap: "0.75rem", alignItems: "center" }}>
        <div style={{ position: "relative", flex: 1 }}>
          <Search size={16} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)" }} />
          <input
            type="text"
            placeholder="Search merchants by name, ID, or email..."
            style={{ width: "100%", paddingLeft: "2rem" }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (setPage(0), loadMerchants())}
          />
        </div>

        <select value={riskLevel} onChange={(e) => { setRiskLevel(e.target.value); setPage(0); }}>
          <option value="">All Seller Risk Tiers</option>
          <option value="High">High Risk Sellers</option>
          <option value="Medium">Medium Risk Sellers</option>
          <option value="Low">Low Risk / Verified</option>
        </select>

        <button onClick={() => { setPage(0); loadMerchants(); }} className="btn-primary" style={{ padding: "0.6rem 1rem" }}>
          Filter
        </button>
      </div>

      {/* Split layout if merchant selected */}
      <div style={{ display: "grid", gridTemplateColumns: selectedMerchant ? "1.4fr 1fr" : "1fr", gap: "1.25rem" }}>
        {/* Table */}
        <div className="trust-card" style={{ padding: 0, overflow: "hidden" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{
                backgroundColor: "var(--bg-secondary)",
                borderBottom: "1px solid var(--border-color)",
                color: "var(--text-muted)",
                fontSize: "0.75rem",
                textTransform: "uppercase"
              }}>
                <th style={{ padding: "0.85rem 1rem" }}>Merchant</th>
                <th style={{ padding: "0.85rem 1rem" }}>Rating</th>
                <th style={{ padding: "0.85rem 1rem" }}>Listings</th>
                <th style={{ padding: "0.85rem 1rem" }}>Flagged Ratio</th>
                <th style={{ padding: "0.85rem 1rem" }}>Account Age</th>
                <th style={{ padding: "0.85rem 1rem" }}>Complaints</th>
                <th style={{ padding: "0.85rem 1rem" }}>Risk Level</th>
                <th style={{ padding: "0.85rem 1rem", textAlign: "right" }}>Inspect</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
                    Loading merchant data...
                  </td>
                </tr>
              ) : merchants.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
                    No merchants found.
                  </td>
                </tr>
              ) : (
                merchants.map((m) => {
                  const flagRatio = m.total_listings > 0 ? (m.flagged_listings / m.total_listings) * 100 : 0;
                  return (
                    <tr
                      key={m.merchant_id}
                      style={{
                        borderBottom: "1px solid var(--border-color)",
                        transition: "background 0.15s",
                        backgroundColor: selectedMerchant?.merchant.merchant_id === m.merchant_id ? "var(--bg-card-hover)" : "transparent"
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-card-hover)")}
                      onMouseLeave={(e) => {
                        if (selectedMerchant?.merchant.merchant_id !== m.merchant_id) {
                          e.currentTarget.style.backgroundColor = "transparent";
                        }
                      }}
                    >
                      <td style={{ padding: "0.85rem 1rem" }}>
                        <div style={{ fontWeight: 600, display: "flex", alignItems: "center", gap: "0.4rem" }}>
                          {m.name}
                          {m.is_verified && <span title="Verified Merchant"><ShieldCheck size={14} color="var(--risk-low)" /></span>}
                        </div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }} className="font-mono">
                          {m.merchant_id}
                        </div>
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontWeight: 600 }}>
                          <Star size={13} fill="#f59e0b" color="#f59e0b" />
                          <span>{m.rating.toFixed(1)}</span>
                        </div>
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        {m.total_listings} items
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <span style={{
                          fontWeight: 600,
                          color: flagRatio > 30 ? "var(--risk-high)" : (flagRatio > 10 ? "var(--risk-medium)" : "var(--risk-low)")
                        }}>
                          {flagRatio.toFixed(0)}%
                        </span>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                          ({m.flagged_listings} flagged)
                        </div>
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        {m.account_age_days} days
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <span style={{ fontWeight: 600, color: m.complaints_count > 3 ? "var(--risk-high)" : "inherit" }}>
                          {m.complaints_count}
                        </span>
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <RiskBadge level={m.risk_level} score={m.risk_score} />
                      </td>

                      <td style={{ padding: "0.85rem 1rem", textAlign: "right" }}>
                        <button
                          onClick={() => handleInspectMerchant(m.merchant_id)}
                          className="btn-secondary"
                          style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem" }}
                        >
                          <Eye size={13} />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Selected Merchant Detail Drawer */}
        {selectedMerchant && (
          <div className="trust-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>
                  {selectedMerchant.merchant.name}
                </h3>
                <span className="font-mono" style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  {selectedMerchant.merchant.merchant_id}
                </span>
              </div>
              <RiskBadge level={selectedMerchant.merchant.risk_level} score={selectedMerchant.merchant.risk_score} />
            </div>

            <div style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "0.75rem",
              padding: "0.75rem",
              background: "var(--bg-secondary)",
              borderRadius: "8px",
              fontSize: "0.8rem"
            }}>
              <div>Rating: <strong>{selectedMerchant.merchant.rating.toFixed(1)} / 5.0</strong></div>
              <div>Tenure: <strong>{selectedMerchant.merchant.account_age_days} days</strong></div>
              <div>Total Catalog: <strong>{selectedMerchant.merchant.total_listings}</strong></div>
              <div>Complaints: <strong style={{ color: selectedMerchant.merchant.complaints_count > 3 ? "var(--risk-high)" : "inherit" }}>{selectedMerchant.merchant.complaints_count}</strong></div>
            </div>

            <div>
              <div style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", marginBottom: "0.5rem" }}>
                RECENT LISTINGS FROM THIS SELLER
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", maxHeight: "320px", overflowY: "auto" }}>
                {selectedMerchant.recent_listings.map((l) => (
                  <div
                    key={l.listing_id}
                    onClick={() => onSelectListing(l)}
                    style={{
                      padding: "0.5rem 0.75rem",
                      background: "var(--bg-secondary)",
                      borderRadius: "6px",
                      cursor: "pointer",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center"
                    }}
                  >
                    <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "180px", fontSize: "0.8rem", fontWeight: 500 }}>
                      {l.title}
                    </div>
                    <RiskBadge level={l.risk_level} score={l.risk_score} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
