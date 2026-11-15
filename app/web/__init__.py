"""Web routing package."""
from .routes_pages import router as pages_router
from .routes_calculators import router as calculators_router
from .routes_newsletter import router as newsletter_router
from .routes_seo import router as seo_router

__all__ = [
    "pages_router",
    "calculators_router",
    "newsletter_router",
    "seo_router",
]
