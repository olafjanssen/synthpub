"""
FastAPI application for the Curator API.
"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import yaml
from .routes.topic_routes import router as topic_router
from .routes.article_routes import router as article_router
from .routes.health import router as health_router
from .routes.project_routes import router as project_router
from .routes.settings import router as settings_router
from .routes.log_routes import router as log_router
from contextlib import asynccontextmanager
from curator.topic_updater import start_update_processor
from pathlib import Path
from utils.logging import info, user_info

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Load environment variables from settings.yaml
    if os.path.exists("settings.yaml"):
        with open("settings.yaml", 'r') as f:
            settings = yaml.safe_load(f)
            env_vars = settings.get("env_vars", {})
            print(env_vars)
            for key, value in env_vars.items():
                os.environ[key] = value

    info("Starting SynthPub API server")
    user_info("SynthPub system initialized and ready")
    start_update_processor()
    yield
    info("Shutting down SynthPub API server")
    # Add any cleanup code here if needed

app = FastAPI(title="SynthPub API", lifespan=lifespan)

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
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
