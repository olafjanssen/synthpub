"""
FastAPI application for the Curator API.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from curator.topic_updater import start_update_processor
from utils.logging import debug, error

from .routes.article_routes import router as article_router
from .routes.health import router as health_router
from .routes.log_routes import router as log_router
from .routes.project_routes import router as project_router
from .routes.settings import router as settings_router
from .routes.topic_routes import router as topic_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Load environment variables from settings.yaml
    if os.path.exists("settings.yaml"):
        with open("settings.yaml", "r") as f:
            settings = yaml.safe_load(f)
            env_vars = settings.get("env_vars", {})
            debug("CONFIG", "Environment variables", f"Found {len(env_vars)} variables")
            for key, value in env_vars.items():
                os.environ[key] = value

    debug("SYSTEM", "Server starting", "SynthPub API")

    # Start background processes
    start_update_processor()

    # Initialize the news scheduler
    try:
        from news.news_scheduler import start_scheduler_thread, stop_scheduler_thread

        start_scheduler_thread()
        debug("SYSTEM", "News scheduler started")
    except Exception as e:
        error("SYSTEM", "Failed to start news scheduler", str(e))

    # Run log router's lifespan if it exists
    if hasattr(log_router, "lifespan"):
        async with log_router.lifespan(app):
            yield
    else:
        yield

    # Cleanup on shutdown
    try:
        from news.news_scheduler import stop_scheduler_thread

        stop_scheduler_thread()
        debug("SYSTEM", "News scheduler stopped")
    except Exception as e:
        error("SYSTEM", "Error stopping news scheduler", str(e))


app = FastAPI(
    title="SynthPub API",
    description="API for creating, managing, and publishing SynthPub content",
    version="1.0.0",
    openapi_tags=[
        {"name": "health", "description": "Health check endpoints"},
        {
            "name": "topics",
            "description": "Operations with topics and content generation",
        },
        {"name": "articles", "description": "Article management endpoints"},
        {"name": "projects", "description": "Project management endpoints"},
        {"name": "settings", "description": "Application settings endpoints"},
        {"name": "logs", "description": "Log management and streaming endpoints"},
    ],
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with prefix
api_router = APIRouter(prefix="/api")

# Include the various routes in the API router
api_router.include_router(topic_router, tags=["topics"])
api_router.include_router(article_router, tags=["articles"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(project_router, tags=["projects"])
api_router.include_router(settings_router, tags=["settings"])
api_router.include_router(log_router, tags=["logs"], prefix="/logs")

# Include the API router in the main app
app.include_router(api_router)

# Mount the frontend static files
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    debug("SYSTEM", "Mounting frontend", str(frontend_dir))
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    debug("SYSTEM", "Frontend directory not found", str(frontend_dir))
