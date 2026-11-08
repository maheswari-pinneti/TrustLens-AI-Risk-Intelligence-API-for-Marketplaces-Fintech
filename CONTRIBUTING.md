# Contributing to TrustLens – AI Risk Intelligence Platform

Thank you for your interest in contributing to **TrustLens**! This document outlines our branch architecture, pull request (PR) process, and code quality standards.

---

## 🌿 Git Branching Strategy

We follow a modular feature-branch workflow structured around platform domains:

| Branch | Description |
| :--- | :--- |
| **`main`** | Production-ready stable branch. Direct commits to `main` are restricted in production; all code enters via Pull Request. |
| **`backend`** | Core FastAPI services, risk engine, fraud detectors, and security layers. |
| **`frontend`** | React 19 + TypeScript + Vite compliance investigation dashboard. |
| **`database`** | SQLAlchemy 2.0 ORM models, repository patterns, and seed pipelines. |
| **`docker`** | Dockerfiles, NGINX configurations, and multi-container orchestration. |
| **`ci/cd`** | GitHub Actions workflows and continuous integration configurations. |
| **`docs`** | Architectural specifications, risk engine formulas, and API documentation. |

---

## 🔄 Pull Request Workflow

### 1. Create a Topic Branch
Branch off `main` or the relevant domain branch using conventional naming:
```bash
git checkout main
git pull origin main
git checkout -b feature/webhook-dispatcher
# Or: fix/image-hash-tolerance, docs/api-guide
```

### 2. Implement Changes & Add Automated Tests
Every new feature or bugfix must be accompanied by automated tests:
```bash
# Run unit and integration tests
python -m pytest tests/ -v
```

### 3. Commit with Conventional Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:
```bash
git add .
git commit -m "feat(webhooks): HMAC-SHA256 event notification dispatcher"
```

### 4. Push and Open a Pull Request
Push your branch to GitHub:
```bash
git push -u origin feature/webhook-dispatcher
```

Then navigate to the repository on GitHub to open your Pull Request:
👉 **[Open New Pull Request](https://github.com/maheswari-pinneti/TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech/compare)**

---

## ✅ Pull Request Review Standards

All Pull Requests must satisfy the following checklist before merge:

1. **Automated CI Validation**: All GitHub Actions workflows in `.github/workflows/ci.yml` must pass cleanly.
2. **100% Test Pass Rate**: No failing or skipped tests.
3. **Security Standards**:
   - Inputs sanitized via `sanitize_text()`.
   - Endpoints guarded with RBAC (`require_admin`, `require_investigator`, etc.).
   - No credentials or `.env` files staged.
4. **Code Quality**:
   - Python code formatted and linted.
   - Frontend TypeScript compiles cleanly (`npm run build` with 0 errors).
