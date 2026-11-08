"""
TrustLens AI Risk Intelligence API - Main Application Entrypoint
"""
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database.connection import init_db, SessionLocal
from app.database.models import User
from app.security.authentication import hash_password
from app.security.headers import SecurityHeadersMiddleware
from app.api.routes import (
    health_router,
    auth_router,
    analyze_router,
    listings_router,
    merchants_router,
    reports_router,
)

settings = get_settings()

# Setup Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("trustlens")
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
logging.getLogger("asyncio").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event: initializes database and root admin account."""
    logger.info("Initializing TrustLens Database schema...")
    init_db()

    # Seed Admin User if missing
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Seeding default administrator account...")
            admin_user = User(
                username="admin",
                email="admin@trustlens.internal",
                hashed_password=hash_password("AdminSecurePass123!"),
                role="admin",
                api_key=settings.ADMIN_API_KEY,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
    except Exception as e:
        logger.error(f"Error seeding admin user: {e}")
    finally:
        db.close()

    logger.info("TrustLens Risk Intelligence API ready for scoring requests.")
    yield
    logger.info("Shutting down TrustLens API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade AI Risk Intelligence API detecting counterfeit listings, "
        "price anomalies, duplicate catalog imagery, and merchant fraud patterns in "
        "e-commerce marketplaces and fintech platforms."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Timing, OWASP Security Headers & Structured Logging Middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

        # OWASP Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "frame-ancestors 'none';"
        )
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - {process_time:.2f}ms"
        )
        return response
    except Exception as exc:
        process_time = (time.time() - start_time) * 1000
        logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "detail": str(exc) if settings.DEBUG else "An unexpected error occurred processing your request.",
                "path": request.url.path
            }
        )


# Centralized Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for err in exc.errors():
        error_details.append({
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "type": err.get("type")
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": error_details,
            "path": request.url.path
        }
    )


# Standard HTTP Exception Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


# Register Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(analyze_router, prefix=settings.API_V1_PREFIX)
app.include_router(listings_router, prefix=settings.API_V1_PREFIX)
app.include_router(merchants_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)


@app.get("/", summary="Root Welcome & Documentation Link")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1_prefix": settings.API_V1_PREFIX
    }
