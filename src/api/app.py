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

app = FastAPI(title="SynthPub API")

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
