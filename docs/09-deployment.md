# 09 - Deployment & Production Configuration

## 1. Quick Start with Docker Compose

TrustLens ships with production-ready container configurations:

```bash
docker-compose up --build -d
```

This deploys:
1. **Backend Service** (`trustlens_backend`): Python 3.11 Uvicorn server running on port `8000`.
2. **Frontend Service** (`trustlens_frontend`): Production NGINX web server hosting the compiled Vite application on port `3000`.
3. **Persistent Volume** (`trustlens_data`): Stores the SQLite database and uploaded catalog fingerprints.

---

## 2. Local Bare-Metal Setup

### Backend:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed database
python scripts/seed_db.py

# 3. Start API
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 3. Production Environment Variables (.env)
```ini
ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api/v1
SECRET_KEY=<generate-strong-64-char-secret>
ADMIN_API_KEY=<generate-secure-api-key>
DATABASE_URL=postgresql://user:password@postgres-db:5432/trustlens
RATE_LIMIT_PER_MINUTE=240
```
