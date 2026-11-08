"""
TrustLens Interactive Command Line Interface (CLI)
Provides terminal-based fraud analysis, database inspection, and model training utilities.
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database.connection import SessionLocal, init_db
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.services.merchant_service import MerchantService
from app.api.schemas.request import AnalyzeListingRequest
from app.ml.train import train_and_evaluate_model


def format_score(score: float, level: str) -> str:
    color_prefix = {
        "High": "\033[91m",    # Red
        "Medium": "\033[93m",  # Yellow
        "Low": "\033[92m"      # Green
    }.get(level, "\033[0m")
    reset = "\033[0m"
    return f"{color_prefix}{score:.1f}/100 [{level.upper()} RISK]{reset}"


def cmd_scan(args):
    init_db()
    db = SessionLocal()
    service = AnalysisService(db)

    title = args.title or args.opt_title
    if not title:
        print("\n❌ Error: Product title is required (e.g. scan 'Nike Shoes' -p 50 or scan --title 'Nike Shoes' -p 50)\n")
        return

    print("\n" + "=" * 65)
    print(" 🛡️  TRUSTLENS AI RISK INTELLIGENCE SCANNER")
    print("=" * 65)
    print(f"Title:         {title}")
    print(f"Price:         ${args.price:.2f}")
    if args.market_price:
        discount = ((args.market_price - args.price) / args.market_price) * 100
        print(f"Market Ref:    ${args.market_price:.2f} (Discount: {discount:.1f}%)")
    print(f"Category:      {args.category}")
    print("-" * 65)

    req = AnalyzeListingRequest(
        title=title,
        description=args.description or title,
        price=args.price,
        market_price=args.market_price,
        category=args.category,
        seller_rating=args.rating,
        seller_account_age_days=args.account_age,
        seller_complaints_count=args.complaints
    )

    result = service.analyze_listing(req, persist=args.persist)

    print(f"Risk Score:    {format_score(result.risk_score, result.risk_level.value)}")
    print(f"Decision:      {result.recommendation.value}")
    if result.ml_prediction:
        prob = f"({(result.ml_fraud_probability or 0.0) * 100:.1f}% confidence)" if result.ml_fraud_probability else ""
        print(f"ML Classifier: {result.ml_prediction} {prob}")

    print("\n[Factor Point Breakdown]")
    b = result.score_breakdown
    print(f"  • Price Anomaly:    {b.price_anomaly_score:5.1f} / 30.0 pts")
    print(f"  • Fraud Keywords:   {b.fraud_keywords_score:5.1f} / 25.0 pts")
    print(f"  • Image Similarity: {b.image_similarity_score:5.1f} / 20.0 pts")
    print(f"  • Seller Rating:    {b.seller_reputation_score:5.1f} / 15.0 pts")
    print(f"  • Behavior/Urgency: {b.listing_behavior_score:5.1f} / 10.0 pts")

    print("\n[Triggered Flags]")
    if not result.flags:
        print("  ✓ No risk flags triggered. Clean marketplace listing.")
    else:
        for idx, flag in enumerate(result.flags, 1):
            print(f"  [{idx}] ⚠️  {flag}")

    if result.evidence.get("summary_explanation"):
        print(f"\n[Forensic Summary]\n  {result.evidence['summary_explanation']}")

    print("=" * 65 + "\n")
    db.close()


def cmd_summary(args):
    init_db()
    db = SessionLocal()
    svc = ReportService(db)
    summary = svc.generate_risk_summary()

    print("\n" + "=" * 60)
    print(" 📊 TRUSTLENS MARKETPLACE SURVEILLANCE KPI SUMMARY")
    print("=" * 60)
    print(f"Total Listings Analyzed:  {summary['total_listings_analyzed']}")
    print(f"High Risk Flagged:        {summary['high_risk_listings']} (Requires Intervention)")
    print(f"Medium Risk:              {summary['medium_risk_listings']}")
    print(f"Low Risk Cleared:         {summary['low_risk_listings']}")
    print(f"Pending Investigations:   {summary['pending_investigation_count']}")
    print(f"Tracked Merchants:        {summary['total_merchants_tracked']}")
    print(f"Average Risk Score:       {summary['average_risk_score']:.1f} / 100")
    print("-" * 60)
    print("Top Triggered Fraud Keywords:")
    for kw in summary['top_fraud_keywords'][:6]:
        print(f"  • {kw['keyword']:<22} {kw['occurrences']} occurrences")
    print("=" * 60 + "\n")
    db.close()


def cmd_merchants(args):
    init_db()
    db = SessionLocal()
    svc = MerchantService(db)
    items, total = svc.list_merchants(limit=args.limit, risk_level=args.risk_level)

    print("\n" + "=" * 75)
    print(f" 🏪 TRUSTLENS MERCHANT RISK DIRECTORY (Showing {len(items)} of {total})")
    print("=" * 75)
    print(f"{'MERCHANT ID':<15} {'NAME':<24} {'RATING':<8} {'FLAGGED':<10} {'RISK SCORE':<12}")
    print("-" * 75)
    for m in items:
        ratio = f"{(m.flagged_listings / m.total_listings * 100):.0f}%" if m.total_listings > 0 else "0%"
        print(f"{m.merchant_id:<15} {m.name[:22]:<24} {m.rating:<8.1f} {ratio:<10} {format_score(m.risk_score, m.risk_level)}")
    print("=" * 75 + "\n")
    db.close()


def cmd_train(args):
    print("Initiating Machine Learning Training & Evaluation...")
    results = train_and_evaluate_model()
    metrics = results["evaluation_metrics"]
    print("\n" + "=" * 60)
    print(" 🧠 MODEL EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Algorithm:       {results['algorithm']}")
    print(f"Accuracy:        {metrics['accuracy']:.4f}")
    print(f"Precision:       {metrics['precision']:.4f}")
    print(f"Recall:          {metrics['recall']:.4f}")
    print(f"F1-Score:        {metrics['f1_score']:.4f}")
    print(f"ROC-AUC:         {metrics['roc_auc']:.4f}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="TrustLens AI Risk Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Scan command
    scan_p = subparsers.add_parser("scan", help="Scan a product listing for fraud risk")
    scan_p.add_argument("title", nargs="?", type=str, default=None, help="Product title (positional)")
    scan_p.add_argument("--title", "-t", dest="opt_title", type=str, default=None, help="Product title (flag syntax)")
    scan_p.add_argument("--description", "-d", type=str, default="", help="Product description")
    scan_p.add_argument("--price", "-p", type=float, required=True, help="Listing price")
    scan_p.add_argument("--market-price", "-m", type=float, default=None, help="Market reference benchmark price")
    scan_p.add_argument("--category", "-c", type=str, default="General", help="Product category")
    scan_p.add_argument("--rating", "-r", type=float, default=None, help="Seller rating (0-5)")
    scan_p.add_argument("--account-age", "-a", type=int, default=None, help="Seller account age in days")
    scan_p.add_argument("--complaints", type=int, default=None, help="Customer complaint count")
    scan_p.add_argument("--persist", action="store_true", default=False, help="Persist listing to database")

    # Summary command
    subparsers.add_parser("summary", help="Print executive fraud surveillance summary")

    # Merchants command
    m_p = subparsers.add_parser("merchants", help="List tracked merchants by risk")
    m_p.add_argument("--limit", type=int, default=15, help="Number of records to show")
    m_p.add_argument("--risk-level", type=str, default=None, help="Filter by Low, Medium, High")

    # Train command
    subparsers.add_parser("train", help="Retrain the Random Forest fraud classifier")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "summary":
        cmd_summary(args)
    elif args.command == "merchants":
        cmd_merchants(args)
    elif args.command == "train":
        cmd_train(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
