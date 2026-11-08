import React, { useState, useEffect } from "react";
import {
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  ArrowUpRight,
  Eye,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { ApiClient } from "../api";
import { ListingItem, RiskLevel } from "../types";
import { RiskBadge, StatusBadge } from "../components/RiskBadges";

interface ListingsPageProps {
  onSelectListing: (listing: ListingItem) => void;
}

export const ListingsPage: React.FC<ListingsPageProps> = ({ onSelectListing }) => {
  const [listings, setListings] = useState<ListingItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [riskLevel, setRiskLevel] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [category, setCategory] = useState<string>("");
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const loadListings = async () => {
    setLoading(true);
    try {
      const res = await ApiClient.getListings({
        skip: page * pageSize,
        limit: pageSize,
        risk_level: riskLevel || undefined,
        status: status || undefined,
        category: category || undefined,
        search: search || undefined
      });
      setListings(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error("Failed to load listings", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadListings();
  }, [page, riskLevel, status, category]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    loadListings();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Listing Triage & Moderation
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
            Investigate suspicious listings, evaluate evidence, and record human compliance decisions
          </p>
        </div>
        <button onClick={loadListings} className="btn-secondary">
          <RefreshCw size={15} /> Refresh List
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="trust-card" style={{ padding: "0.85rem 1rem" }}>
        <form onSubmit={handleSearchSubmit} style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
          {/* Search Box */}
          <div style={{ position: "relative", flex: 1, minWidth: "220px" }}>
            <Search size={16} color="var(--text-muted)" style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)" }} />
            <input
              type="text"
              placeholder="Search by title, description, or listing ID..."
              style={{ width: "100%", paddingLeft: "2rem" }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Risk Level Filter */}
          <select value={riskLevel} onChange={(e) => { setRiskLevel(e.target.value); setPage(0); }}>
            <option value="">All Risk Tiers</option>
            <option value="High">High Risk Only</option>
            <option value="Medium">Medium Risk Only</option>
            <option value="Low">Low Risk Only</option>
          </select>

          {/* Status Filter */}
          <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(0); }}>
            <option value="">All Statuses</option>
            <option value="PENDING_REVIEW">Pending Review</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
            <option value="ESCALATED">Escalated</option>
          </select>

          {/* Category Filter */}
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(0); }}>
            <option value="">All Categories</option>
            <option value="Footwear & Apparel">Footwear & Apparel</option>
            <option value="Smartphones">Smartphones</option>
            <option value="Electronics">Electronics</option>
            <option value="Watches & Jewelry">Watches & Jewelry</option>
            <option value="Luxury Goods">Luxury Goods</option>
            <option value="Perfume & Cosmetics">Perfume & Cosmetics</option>
          </select>

          <button type="submit" className="btn-primary" style={{ padding: "0.6rem 1rem" }}>
            Filter
          </button>
        </form>
      </div>

      {/* Triage Table */}
      <div className="trust-card" style={{ padding: 0, overflow: "hidden" }}>
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
                <th style={{ padding: "0.85rem 1rem" }}>Category</th>
                <th style={{ padding: "0.85rem 1rem" }}>Price vs Market</th>
                <th style={{ padding: "0.85rem 1rem" }}>Risk Score</th>
                <th style={{ padding: "0.85rem 1rem" }}>ML Probability</th>
                <th style={{ padding: "0.85rem 1rem" }}>Flags</th>
                <th style={{ padding: "0.85rem 1rem" }}>Status</th>
                <th style={{ padding: "0.85rem 1rem", textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
                    Loading listings...
                  </td>
                </tr>
              ) : listings.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--text-muted)" }}>
                    No listings match the current filters.
                  </td>
                </tr>
              ) : (
                listings.map((item) => {
                  const discountPct = item.market_price && item.market_price > item.price
                    ? Math.round(((item.market_price - item.price) / item.market_price) * 100)
                    : null;

                  return (
                    <tr
                      key={item.listing_id}
                      style={{
                        borderBottom: "1px solid var(--border-color)",
                        transition: "background 0.15s"
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "var(--bg-card-hover)")}
                      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
                    >
                      <td style={{ padding: "0.85rem 1rem", maxWidth: "260px" }}>
                        <div style={{ fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {item.title}
                        </div>
                        <div style={{ fontSize: "0.7rem", color: "var(--text-muted)" }} className="font-mono">
                          {item.listing_id} • Merchant: {item.merchant_id}
                        </div>
                      </td>

                      <td style={{ padding: "0.85rem 1rem", color: "var(--text-secondary)" }}>
                        {item.category}
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <div className="font-mono" style={{ fontWeight: 600 }}>${item.price.toFixed(2)}</div>
                        {item.market_price ? (
                          <div style={{ fontSize: "0.7rem", color: discountPct && discountPct > 50 ? "var(--risk-high)" : "var(--text-muted)" }}>
                            Ref: ${item.market_price.toFixed(2)} {discountPct ? `(-${discountPct}%)` : ""}
                          </div>
                        ) : (
                          <span style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>No market ref</span>
                        )}
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <RiskBadge level={item.risk_level} score={item.risk_score} />
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        {item.ml_fraud_probability !== undefined && item.ml_fraud_probability !== null ? (
                          <span className="font-mono" style={{
                            color: item.ml_fraud_probability >= 0.5 ? "var(--risk-high)" : "var(--risk-low)",
                            fontWeight: 600
                          }}>
                            {(item.ml_fraud_probability * 100).toFixed(1)}%
                          </span>
                        ) : (
                          <span style={{ color: "var(--text-muted)" }}>—</span>
                        )}
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <span style={{
                          fontSize: "0.75rem",
                          fontWeight: 600,
                          padding: "2px 6px",
                          borderRadius: "4px",
                          backgroundColor: item.flags.length > 0 ? "rgba(244, 63, 94, 0.15)" : "rgba(255, 255, 255, 0.05)",
                          color: item.flags.length > 0 ? "var(--risk-high)" : "var(--text-muted)"
                        }}>
                          {item.flags.length} flag(s)
                        </span>
                      </td>

                      <td style={{ padding: "0.85rem 1rem" }}>
                        <StatusBadge status={item.status} />
                      </td>

                      <td style={{ padding: "0.85rem 1rem", textAlign: "right" }}>
                        <button
                          onClick={() => onSelectListing(item)}
                          className="btn-secondary"
                          style={{ fontSize: "0.75rem", padding: "0.3rem 0.65rem" }}
                        >
                          <Eye size={13} /> Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "0.85rem 1rem",
          backgroundColor: "var(--bg-secondary)",
          borderTop: "1px solid var(--border-color)",
          fontSize: "0.8rem",
          color: "var(--text-muted)"
        }}>
          <span>Showing {listings.length} of {total} total listings</span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              disabled={page === 0}
              onClick={() => setPage(p => Math.max(0, p - 1))}
              className="btn-secondary"
              style={{ fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}
            >
              Previous
            </button>
            <span style={{ alignSelf: "center", fontWeight: 600 }}>Page {page + 1}</span>
            <button
              disabled={(page + 1) * pageSize >= total}
              onClick={() => setPage(p => p + 1)}
              className="btn-secondary"
              style={{ fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
