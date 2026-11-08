# 05 - Database Design

TrustLens utilizes **SQLAlchemy 2.0 ORM** with native support for SQLite in development and PostgreSQL in enterprise deployments.

---

## Entity Relationship Schema

```
+--------------------+           +------------------------+           +--------------------------+
|       users        |           |       merchants        |           |         listings         |
+--------------------+           +------------------------+           +--------------------------+
| id (PK)            |           | id (PK)                |           | id (PK)                  |
| uuid (Unique)      |           | merchant_id (Unique,IX)|<----+     | listing_id (Unique, IX)  |
| username (Unique)  |           | name                   |     |     | merchant_id (FK, IX)-----+
| email (Unique)     |           | email                  |     +---->| title (IX)               |
| hashed_password    |           | rating                 |           | description              |
| role               |           | total_listings         |           | category (IX)            |
| api_key (Unique,IX)|           | flagged_listings       |           | price, market_price      |
| is_active          |           | account_age_days       |           | risk_score (IX)          |
| created_at         |           | complaints_count       |           | risk_level (IX)          |
+---------+----------+           | is_verified            |           | ml_fraud_probability     |
          |                      | risk_score             |           | flags (JSON)             |
          |                      | risk_level             |           | score_breakdown (JSON)   |
          |                      | created_at             |           | evidence (JSON)          |
          |                      +-----------+------------+           | status (IX)              |
          |                                  |                        | review_notes             |
          |                                  |                        | reviewed_by_id (FK)------+
          |                                  |                        | reviewed_at              |
          |                                  |                        +-------------+------------+
          |                                  |                                      |
          |                                  v                                      v
          |                      +------------------------+           +--------------------------+
          |                      |      risk_alerts       |           |    image_fingerprints    |
          |                      +------------------------+           +--------------------------+
          |                      | id (PK)                |           | id (PK)                  |
          |                      | alert_id (Unique)      |           | listing_id (FK, IX)      |
          |                      | severity (IX)          |           | image_hash (IX)          |
          |                      | message                |           | perceptual_hash (IX)     |
          |                      | listing_id (FK)        |           | duplicate_of_id          |
          |                      | merchant_id (FK)       |           | similarity_score         |
          |                      | is_resolved (IX)       |           | created_at               |
          |                      +------------------------+           +--------------------------+
          |
          v
+--------------------+
|     audit_logs     |
+--------------------+
| id (PK)            |
| user_id            |
| action (IX)        |
| resource_type      |
| resource_id        |
| details (JSON)     |
| ip_address         |
| created_at (IX)    |
+--------------------+
```

---

## Key Indexes and Optimizations
- **B-Tree Indexes**: Placed on `listing_id`, `merchant_id`, `risk_score`, `risk_level`, `status`, and `created_at` for sub-millisecond triage filtering.
- **Perceptual Hash Lookup**: `image_hash` and `perceptual_hash` indexed to accelerate reverse image catalog queries.
- **Audit Immutability**: `audit_logs` record every disposition decision, score update, and authentication event with timestamps.
