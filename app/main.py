"""FastAPI Application Factory for Multi-Country Finance Calculator Platform."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import init_db
from app.countries.registry import country_registry
from app.web.routes_pages import router as pages_router
from app.web.routes_calculators import router as calculators_router
from app.web.routes_newsletter import router as newsletter_router
from app.web.routes_seo import router as seo_router

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("omnifinance")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing database...")
    init_db()

    logger.info(f"Loading Country Packs from {settings.COUNTRIES_DIR}...")
    country_registry.discover_and_load(settings.COUNTRIES_DIR)
    logger.info(f"Loaded countries: {country_registry.get_codes()}")

    yield

    logger.info("Application shutting down...")

def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Multi-Country Finance Calculator Platform with Groq LLM Tax Intelligence",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static assets
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

    # Include routers
    app.include_router(seo_router)
    app.include_router(pages_router)
    app.include_router(calculators_router)
    app.include_router(newsletter_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
