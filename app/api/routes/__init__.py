from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.listings import router as listings_router
from app.api.routes.merchants import router as merchants_router
from app.api.routes.reports import router as reports_router

__all__ = [
    "health_router",
    "auth_router",
    "analyze_router",
    "listings_router",
    "merchants_router",
    "reports_router",
]
