"""
FastAPI application entry point.
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import get_settings
from app.routes import carrier, loads
from app.routes import calls
from app.services.load_service import init_loads
from app.database import init_db, seed_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load data on startup, cleanup on shutdown."""
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Load the freight loads into memory
    init_loads("data/loads.json")

    # Initialize database and seed with sample data
    init_db()
    seed_db()

    yield

    logger.info("Shutting down.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "API backend for the HappyRobot Inbound Carrier Sales agent. "
            "Provides carrier verification via FMCSA and freight load search."
        ),
        lifespan=lifespan,
    )

    # CORS — allow HappyRobot platform to call us
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(carrier.router)
    app.include_router(loads.router)
    app.include_router(calls.router)

    # Serve static files (CSS, JS)
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    @app.get("/dashboard", tags=["Dashboard"], include_in_schema=False)
    async def dashboard():
        """Serve the analytics dashboard."""
        return FileResponse(str(static_dir / "dashboard.html"))

    return app


app = create_app()
