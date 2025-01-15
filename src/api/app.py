"""
FastAPI application for the Curator API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .routes.topic_routes import router as topic_router
from .routes.article_routes import router as article_router
from .routes.health import router as health_router
from .routes.project_routes import router as project_router
from .routes.settings import router as settings_router
from contextlib import asynccontextmanager
from curator.topic_updater import start_update_processor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    start_update_processor()
    yield
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

# Include the various routes
app.include_router(topic_router, tags=["topics"])
app.include_router(article_router, tags=["articles"])
app.include_router(health_router, tags=["health"])
app.include_router(project_router, tags=["projects"])
app.include_router(settings_router, tags=["settings"])
