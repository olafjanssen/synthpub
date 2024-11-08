"""
FastAPI application for the Curator API.
"""
from fastapi import FastAPI
from .routes.topic_routes import router as topic_router

app = FastAPI(title="SynthPub API")

# Include the topic routes
app.include_router(topic_router, tags=["topics"])