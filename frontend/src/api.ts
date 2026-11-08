import {
  AnalyzeRequest,
  AnalyzeResponse,
  ListingItem,
  MerchantItem,
  RiskSummary,
  HealthStatus,
  MlVsRulesComparison,
  InvestigationStatus
} from "./types";

const API_BASE = "http://127.0.0.1:8000";

export class ApiClient {
  private static getHeaders(): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    const token = localStorage.getItem("trustlens_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    const apiKey = localStorage.getItem("trustlens_api_key") || "tl_live_admin_secret_key_998877";
    if (apiKey) {
      headers["X-API-Key"] = apiKey;
    }
    return headers;
  }

  static async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Health check failed");
    return res.json();
  }

  static async getRiskSummary(): Promise<RiskSummary> {
    const res = await fetch(`${API_BASE}/api/v1/risk/summary`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load risk summary");
    return res.json();
  }

  static async analyzeListing(data: AnalyzeRequest, persist = true): Promise<AnalyzeResponse> {
    const res = await fetch(`${API_BASE}/api/v1/analyze?persist=${persist}`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Analysis request failed");
    }
    return res.json();
  }

  static async batchAnalyze(listings: AnalyzeRequest[], persist = true): Promise<any> {
    const res = await fetch(`${API_BASE}/api/v1/analyze/batch?persist=${persist}`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ listings }),
    });
    if (!res.ok) throw new Error("Batch analysis failed");
    return res.json();
  }

  static async getListings(params: {
    skip?: number;
    limit?: number;
    risk_level?: string;
    category?: string;
    status?: string;
    search?: string;
  } = {}): Promise<{ total: number; items: ListingItem[] }> {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.set("skip", params.skip.toString());
    if (params.limit !== undefined) query.set("limit", params.limit.toString());
    if (params.risk_level) query.set("risk_level", params.risk_level);
    if (params.category) query.set("category", params.category);
    if (params.status) query.set("status", params.status);
    if (params.search) query.set("search", params.search);

    const res = await fetch(`${API_BASE}/api/v1/listings?${query.toString()}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch listings");
    return res.json();
  }

  static async getListing(listingId: string): Promise<ListingItem> {
    const res = await fetch(`${API_BASE}/api/v1/listings/${listingId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to load listing ${listingId}`);
    return res.json();
  }

  static async submitDecision(
    listingId: string,
    status: InvestigationStatus,
    reviewNotes?: string
  ): Promise<ListingItem> {
    const res = await fetch(`${API_BASE}/api/v1/listings/${listingId}/decision`, {
      method: "PATCH",
      headers: this.getHeaders(),
      body: JSON.stringify({ status, review_notes: reviewNotes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to update decision");
    }
    return res.json();
  }

  static async getMerchants(params: {
    skip?: number;
    limit?: number;
    risk_level?: string;
    search?: string;
  } = {}): Promise<{ total: number; items: MerchantItem[] }> {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.set("skip", params.skip.toString());
    if (params.limit !== undefined) query.set("limit", params.limit.toString());
    if (params.risk_level) query.set("risk_level", params.risk_level);
    if (params.search) query.set("search", params.search);

    const res = await fetch(`${API_BASE}/api/v1/merchants?${query.toString()}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch merchants");
    return res.json();
  }

  static async getMerchantDetails(merchantId: string): Promise<{
    merchant: MerchantItem;
    recent_listings: ListingItem[];
    total_listings_count: number;
  }> {
    const res = await fetch(`${API_BASE}/api/v1/merchants/${merchantId}`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to load merchant ${merchantId}`);
    return res.json();
  }

  static async getMlVsRules(): Promise<MlVsRulesComparison> {
    const res = await fetch(`${API_BASE}/api/v1/reports/ml-vs-rules`, {
      headers: this.getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load ML comparison");
    return res.json();
  }

  static getExportCsvUrl(): string {
    const apiKey = localStorage.getItem("trustlens_api_key") || "tl_live_admin_secret_key_998877";
    return `${API_BASE}/api/v1/reports/export-csv?api_key=${encodeURIComponent(apiKey)}`;
  }
}
