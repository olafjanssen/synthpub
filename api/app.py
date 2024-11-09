"""
FastAPI application for the Curator API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.topic_routes import router as topic_router
from .routes.article_routes import router as article_router

app = FastAPI(title="SynthPub API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the topic routes
app.include_router(topic_router, tags=["topics"])

# Include the article routes
app.include_router(article_router, tags=["articles"])