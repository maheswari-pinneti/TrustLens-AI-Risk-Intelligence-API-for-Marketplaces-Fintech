export type RiskLevel = "Low" | "Medium" | "High";
export type Recommendation = "AUTO_APPROVE" | "MANUAL_REVIEW" | "AUTO_REJECT";
export type InvestigationStatus = "PENDING_REVIEW" | "APPROVED" | "REJECTED" | "ESCALATED";

export interface ScoreBreakdown {
  price_anomaly_score: number;
  fraud_keywords_score: number;
  image_similarity_score: number;
  seller_reputation_score: number;
  listing_behavior_score: number;
  total_score: number;
}

export interface AnalyzeRequest {
  listing_id?: string;
  title: string;
  description: string;
  price: number;
  market_price?: number;
  currency?: string;
  category?: string;
  merchant_id?: string;
  seller_rating?: number;
  seller_account_age_days?: number;
  seller_complaints_count?: number;
  image_url?: string;
  image_base64?: string;
  image_hash?: string;
}

export interface AnalyzeResponse {
  listing_id: string;
  title: string;
  risk_score: number;
  risk_level: RiskLevel;
  recommendation: Recommendation;
  ml_prediction?: string;
  ml_fraud_probability?: number;
  flags: string[];
  score_breakdown: ScoreBreakdown;
  evidence: Record<string, any>;
  timestamp: string;
}

export interface ListingItem {
  id: number;
  listing_id: string;
  merchant_id: string;
  title: string;
  description: string;
  category: string;
  price: number;
  market_price?: number;
  currency: string;
  image_url?: string;
  image_hash?: string;
  risk_score: number;
  risk_level: RiskLevel;
  ml_fraud_probability?: number;
  ml_prediction?: string;
  flags: string[];
  score_breakdown: Record<string, any>;
  evidence: Record<string, any>;
  status: InvestigationStatus;
  review_notes?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface MerchantItem {
  id: number;
  merchant_id: string;
  name: string;
  email?: string;
  rating: number;
  total_listings: number;
  flagged_listings: number;
  account_age_days: number;
  complaints_count: number;
  is_verified: boolean;
  risk_score: number;
  risk_level: RiskLevel;
  created_at: string;
  updated_at: string;
}

export interface RiskSummary {
  total_listings_analyzed: number;
  total_merchants_tracked: number;
  high_risk_listings: number;
  medium_risk_listings: number;
  low_risk_listings: number;
  pending_investigation_count: number;
  resolved_investigation_count: number;
  average_risk_score: number;
  top_fraud_keywords: { keyword: string; occurrences: number }[];
  category_risk_distribution: { category: string; count: number; avg_risk: number }[];
  recent_alerts: {
    id: number;
    alert_id: string;
    severity: string;
    message: string;
    listing_id?: string;
    merchant_id?: string;
    is_resolved: boolean;
    created_at: string;
  }[];
}

export interface HealthStatus {
  status: string;
  environment: string;
  version: string;
  database_connected: boolean;
  ml_model_loaded: boolean;
  timestamp: string;
}

export interface MlVsRulesComparison {
  total_analyzed: number;
  concordant_count: number;
  discordant_count: number;
  agreement_rate_pct: number;
  comparison_samples: {
    listing_id: string;
    title: string;
    rule_risk_score: number;
    rule_risk_level: string;
    ml_fraud_probability: number;
    ml_prediction: string;
    agreement: boolean;
  }[];
}
