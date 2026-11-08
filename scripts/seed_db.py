"""
Database Seeding Script: Loads sample merchants and listings into SQLite
"""
import sys
import csv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database.connection import init_db, SessionLocal
from app.database.models import User, Merchant, Listing
from app.security.authentication import hash_password
from app.services.analysis_service import AnalysisService
from app.api.schemas.request import AnalyzeListingRequest


def seed_database(limit_listings: int = 150):
    print("Initializing Database tables...")
    init_db()
    db = SessionLocal()

    # 1. Admin & Investigator Users
    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@trustlens.internal",
            hashed_password=hash_password("AdminSecurePass123!"),
            role="admin",
            api_key="tl_live_admin_secret_key_998877",
            is_active=True
        )
        db.add(admin)
        print("Seeded admin user (admin / AdminSecurePass123!)")

    if not db.query(User).filter(User.username == "investigator").first():
        investigator = User(
            username="investigator",
            email="investigator@trustlens.internal",
            hashed_password=hash_password("InvestigateSecure2026!"),
            role="investigator",
            api_key="tl_live_investigator_key_554433",
            is_active=True
        )
        db.add(investigator)
        print("Seeded investigator user (investigator / InvestigateSecure2026!)")

    db.commit()

    # 2. Seed Merchants
    merchants_file = ROOT_DIR / "data" / "sample_merchants.csv"
    if merchants_file.exists():
        with open(merchants_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if not db.query(Merchant).filter(Merchant.merchant_id == row["merchant_id"]).first():
                    m = Merchant(
                        merchant_id=row["merchant_id"],
                        name=row["name"],
                        email=row["email"],
                        rating=float(row["rating"]),
                        total_listings=int(row["total_listings"]),
                        flagged_listings=int(row["flagged_listings"]),
                        account_age_days=int(row["account_age_days"]),
                        complaints_count=int(row["complaints_count"]),
                        is_verified=bool(int(row["is_verified"])),
                        risk_score=float(row["risk_score"]),
                        risk_level=row["risk_level"]
                    )
                    db.add(m)
                    count += 1
            db.commit()
            print(f"Seeded {count} merchants.")

    # 3. Seed and Evaluate Sample Listings
    listings_file = ROOT_DIR / "data" / "sample_listings.csv"
    if listings_file.exists():
        service = AnalysisService(db)
        with open(listings_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)[:limit_listings]
            seeded = 0
            for row in rows:
                existing = db.query(Listing).filter(Listing.listing_id == row["listing_id"]).first()
                if not existing:
                    req = AnalyzeListingRequest(
                        listing_id=row["listing_id"],
                        merchant_id=row["merchant_id"],
                        title=row["title"],
                        description=row["description"],
                        category=row["category"],
                        price=float(row["price"]),
                        market_price=float(row["market_price"]) if row.get("market_price") else None,
                        seller_rating=float(row["seller_rating"]) if row.get("seller_rating") else None,
                        seller_account_age_days=int(row["account_age_days"]) if row.get("account_age_days") else None,
                        seller_complaints_count=int(row["complaints_count"]) if row.get("complaints_count") else None
                    )
                    service.analyze_listing(req, persist=True)
                    seeded += 1
            print(f"Evaluated and seeded {seeded} sample listings.")

    db.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
