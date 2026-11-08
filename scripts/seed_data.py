"""
Data Generation Script: Creates realistic sample datasets for training & demonstration
"""
import random
import csv
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    "Footwear & Apparel", "Luxury Goods", "Smartphones",
    "Electronics", "Watches & Jewelry", "Perfume & Cosmetics"
]

GENUINE_PRODUCTS = [
    ("Apple iPhone 15 Pro Max 256GB Natural Titanium", "Brand new in factory sealed retail box with official Apple warranty.", 1199.0, 1199.0, "Smartphones"),
    ("Nike Air Jordan 1 Retro High OG Chicago", "Authentic sneaker purchase from official Nike SNKRS drop. Includes original invoice and box.", 180.0, 210.0, "Footwear & Apparel"),
    ("Sony WH-1000XM5 Wireless Noise Canceling Headphones", "Like new condition, used twice for travel. Full accessories and charging cable included.", 320.0, 399.0, "Electronics"),
    ("Rolex Submariner Date 41mm Oystersteel", "Complete set with box, green chronometer tag, and 2023 international guarantee card.", 13500.0, 14200.0, "Watches & Jewelry"),
    ("Chanel Classic Flap Bag Medium Black Lambskin", "Pre-owned in pristine condition, authenticated by Entrupy. Gold hardware.", 8500.0, 9200.0, "Luxury Goods"),
    ("Dior Sauvage Eau de Parfum 100ml", "Original Dior fragrance bought at Sephora. Unopened packaging.", 130.0, 145.0, "Perfume & Cosmetics"),
    ("Dell XPS 15 Laptop 32GB RAM 1TB SSD", "Workstation laptop in excellent working order with original 130W charger.", 1450.0, 1600.0, "Electronics"),
    ("Adidas Yeezy Boost 350 V2 Zebra", "Deadstock pair directly from Adidas store. Verified tags intact.", 230.0, 240.0, "Footwear & Apparel"),
    ("Samsung Galaxy S24 Ultra 512GB Titanium Black", "Unlocked carrier-free phone in mint condition. Includes screen protector.", 1100.0, 1299.0, "Smartphones"),
    ("Omega Speedmaster Professional Moonwatch", "Manual winding chronograph watch with full box set and Omega warranty.", 6400.0, 7000.0, "Watches & Jewelry")
]

FRAUD_PRODUCTS = [
    ("Nike Shoes Cheap Replica First Copy Jordan", "Brand new cheap replica nike shoes 1:1 ua quality whatsapp me for orders fast delivery", 55.0, 210.0, "Footwear & Apparel"),
    ("iPhone 15 Pro Max iCloud Bypassed Clean IMEI", "Works perfectly bypassed icloud locked phone cash only or telegram me wire transfer only", 199.0, 1199.0, "Smartphones"),
    ("Rolex Submariner Master Copy Superclone", "AAA grade superclone mirror quality looks authentic clone watch no receipt must go today", 250.0, 14000.0, "Watches & Jewelry"),
    ("Chanel Bag 1:1 Mirror Quality Handbag", "Unauthorized authentic overrun from oem factory defective batch clearance contact outside app", 180.0, 8500.0, "Luxury Goods"),
    ("Sony WH-1000XM5 Headphones Factory Reject", "Knockoff first copy bluetooth headphones fake packaging zelle only wire transfer only", 40.0, 399.0, "Electronics"),
    ("Dior Sauvage Perfume AA Quality Replica", "Fake perfume wholesale batch customs seized won in lottery pay offline friends and family paypal", 20.0, 145.0, "Perfume & Cosmetics"),
    ("Apple MacBook Pro M3 Stolen Goods Urgent", "Fell off truck urgent sale must go today gift card payment or crypto only blacklisted", 300.0, 2200.0, "Electronics"),
    ("Gucci Marmont Belt AAA Grade Replica", "First copy 1:1 replica belt unauthorized authentic dm on instagram no refund", 35.0, 490.0, "Luxury Goods"),
    ("Samsung S24 Ultra First Copy Clone Phone", "Brand new clone phone non genuine android oem overrun telegram me fast shipping", 120.0, 1299.0, "Smartphones"),
    ("Cartier Love Bracelet Superclone Gold", "Counterfeit 1:1 replica master copy bracelet mirror quality wire transfer only cash only", 90.0, 7350.0, "Watches & Jewelry")
]


def generate_merchants_and_listings(num_merchants=50, num_listings=600):
    merchants_file = DATA_DIR / "sample_merchants.csv"
    listings_file = DATA_DIR / "sample_listings.csv"

    merchants = []
    for i in range(1, num_merchants + 1):
        is_fraudster = random.random() < 0.28
        m_id = f"merch_{i:03d}"
        if is_fraudster:
            name = f"{random.choice(['QuickDeals', 'FlashDiscounts', 'SuperBargain', 'WholesaleOverstock', 'DirectImport'])} {random.randint(10, 999)}"
            rating = round(random.uniform(1.0, 2.8), 1)
            age = random.randint(1, 20)
            complaints = random.randint(3, 18)
            verified = False
            risk_score = round(random.uniform(62.0, 95.0), 1)
            risk_level = "High"
        else:
            name = f"{random.choice(['ApexRetail', 'SummitGoods', 'HorizonCommerce', 'TrustMart', 'NordicStore', 'EchoBoutique'])} {random.randint(10, 99)}"
            rating = round(random.uniform(3.9, 5.0), 1)
            age = random.randint(60, 1200)
            complaints = random.randint(0, 2)
            verified = random.random() < 0.85
            risk_score = round(random.uniform(5.0, 24.0), 1)
            risk_level = "Low"

        merchants.append({
            "merchant_id": m_id,
            "name": name,
            "email": f"{m_id}@marketplace-demo.com",
            "rating": rating,
            "total_listings": 0,
            "flagged_listings": 0,
            "account_age_days": age,
            "complaints_count": complaints,
            "is_verified": 1 if verified else 0,
            "risk_score": risk_score,
            "risk_level": risk_level
        })

    # Generate Listings
    listings = []
    for i in range(1, num_listings + 1):
        merchant = random.choice(merchants)
        is_fraud_merchant = merchant["risk_level"] == "High"
        is_fraud_listing = random.random() < (0.78 if is_fraud_merchant else 0.08)

        if is_fraud_listing:
            prod = random.choice(FRAUD_PRODUCTS)
            title = f"{prod[0]} #{random.randint(100, 999)}"
            desc = f"{prod[1]}. Contact quickly for limited inventory! Best prices guaranteed."
            price = round(prod[2] * random.uniform(0.7, 1.2), 2)
            market_price = prod[3]
            category = prod[4]
            is_fraud = 1
            merchant["flagged_listings"] += 1
        else:
            prod = random.choice(GENUINE_PRODUCTS)
            title = f"{prod[0]} - Authentic Edition"
            desc = f"{prod[1]} Fast domestic shipping with tracking number provided upon dispatch."
            price = round(prod[2] * random.uniform(0.9, 1.1), 2)
            market_price = prod[3]
            category = prod[4]
            is_fraud = 0

        merchant["total_listings"] += 1
        listings.append({
            "listing_id": f"lst_{i:04d}",
            "merchant_id": merchant["merchant_id"],
            "title": title,
            "description": desc,
            "category": category,
            "price": price,
            "market_price": market_price,
            "seller_rating": merchant["rating"],
            "account_age_days": merchant["account_age_days"],
            "complaints_count": merchant["complaints_count"],
            "is_fraud": is_fraud
        })

    # Write Merchants CSV
    with open(merchants_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(merchants[0].keys()))
        writer.writeheader()
        writer.writerows(merchants)

    # Write Listings CSV
    with open(listings_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(listings[0].keys()))
        writer.writeheader()
        writer.writerows(listings)

    print(f"Generated {len(merchants)} merchants -> {merchants_file}")
    print(f"Generated {len(listings)} listings -> {listings_file}")


if __name__ == "__main__":
    generate_merchants_and_listings()
