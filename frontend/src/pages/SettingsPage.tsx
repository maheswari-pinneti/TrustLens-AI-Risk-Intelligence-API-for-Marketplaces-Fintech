import React, { useState } from "react";
import { Key, Copy, Check, Sliders, ExternalLink, ShieldCheck, RefreshCw } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const [apiKey, setApiKey] = useState(
    localStorage.getItem("trustlens_api_key") || "tl_live_admin_secret_key_998877"
  );
  const [copied, setCopied] = useState(false);

  // Threshold weights (sum = 100)
  const [weights, setWeights] = useState({
    price: 30,
    keywords: 25,
    image: 20,
    seller: 15,
    behavior: 10
  });

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSaveApiKey = () => {
    localStorage.setItem("trustlens_api_key", apiKey);
    alert("API Key updated in local storage.");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", maxWidth: "900px" }}>
      <div>
        <h1 style={{ fontSize: "1.6rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
          API Credentials & Risk Scoring Configuration
        </h1>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.2rem" }}>
          Manage developer credentials, rate limits, and calibrate risk factor weights
        </p>
      </div>

      {/* API Key Manager Card */}
      <div className="trust-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <h2 style={{ fontSize: "1.05rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Key size={18} color="var(--accent-cyan)" /> Live API Secret Key
        </h2>
        <p style={{ fontSize: "0.825rem", color: "var(--text-secondary)" }}>
          Authenticate REST requests via header: <code className="font-mono" style={{ color: "#38bdf8" }}>X-API-Key: {apiKey}</code>
        </p>

        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <input
            type="text"
            className="font-mono"
            style={{ flex: 1, backgroundColor: "var(--bg-primary)" }}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <button onClick={handleCopy} className="btn-secondary">
            {copied ? <Check size={16} color="var(--risk-low)" /> : <Copy size={16} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
          <button onClick={handleSaveApiKey} className="btn-primary">
            Save Key
          </button>
        </div>

        <div style={{
          display: "flex",
          gap: "1.5rem",
          fontSize: "0.75rem",
          color: "var(--text-muted)",
          borderTop: "1px solid var(--border-color)",
          paddingTop: "0.75rem"
        }}>
          <div>Rate Limit: <strong>120 req / min</strong></div>
          <div>Scope: <strong>Full Admin & Compliance Triage</strong></div>
          <div>Environment: <strong>Development & Testing</strong></div>
        </div>
      </div>

      {/* Configurable Risk Weights */}
      <div className="trust-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: "1.05rem", fontWeight: 600, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Sliders size={18} color="var(--accent-purple)" /> Risk Scoring Factor Weights
          </h2>
          <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Total: 100 Maximum Points</span>
        </div>

        <p style={{ fontSize: "0.825rem", color: "var(--text-secondary)" }}>
          Customize the point contribution of each fraud detection dimension. Changes adjust how composite risk scores are calculated.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              <span>Price Anomaly Weight</span>
              <strong className="font-mono">{weights.price} pts</strong>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={weights.price}
              onChange={(e) => setWeights({ ...weights, price: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "var(--accent-cyan)" }}
            />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              <span>Fraud Keywords Weight</span>
              <strong className="font-mono">{weights.keywords} pts</strong>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={weights.keywords}
              onChange={(e) => setWeights({ ...weights, keywords: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "#f59e0b" }}
            />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              <span>Image Perceptual Similarity Weight</span>
              <strong className="font-mono">{weights.image} pts</strong>
            </div>
            <input
              type="range"
              min="0"
              max="50"
              value={weights.image}
              onChange={(e) => setWeights({ ...weights, image: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "#38bdf8" }}
            />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              <span>Seller Reputation Weight</span>
              <strong className="font-mono">{weights.seller} pts</strong>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={weights.seller}
              onChange={(e) => setWeights({ ...weights, seller: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "#a855f7" }}
            />
          </div>

          <div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "0.3rem" }}>
              <span>Listing Behavior & Urgency Weight</span>
              <strong className="font-mono">{weights.behavior} pts</strong>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              value={weights.behavior}
              onChange={(e) => setWeights({ ...weights, behavior: parseInt(e.target.value) })}
              style={{ width: "100%", accentColor: "#10b981" }}
            />
          </div>
        </div>
      </div>

      {/* Developer Resources & API Docs */}
      <div className="trust-card" style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <h2 style={{ fontSize: "1.05rem", fontWeight: 600 }}>Developer Resources & OpenAPI</h2>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            style={{ textDecoration: "none" }}
          >
            <ExternalLink size={15} /> Interactive Swagger UI
          </a>
          <a
            href="http://127.0.0.1:8000/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            style={{ textDecoration: "none" }}
          >
            <ExternalLink size={15} /> ReDoc Specification
          </a>
          <a
            href="http://127.0.0.1:8000/openapi.json"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            style={{ textDecoration: "none" }}
          >
            <ExternalLink size={15} /> OpenAPI 3.1 JSON Schema
          </a>
        </div>
      </div>
    </div>
  );
};
