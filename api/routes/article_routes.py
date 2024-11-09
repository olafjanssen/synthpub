from fastapi import APIRouter, HTTPException
from ..db.article_db import get_article
from ..models.article import Article

router = APIRouter()

@router.get("/articles/{article_id}", response_model=Article)
async def get_article_route(article_id: str):
    """Get a specific article by ID."""
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article 