from fastapi import APIRouter, HTTPException
from ..db.article_db import get_article
from ..models.article import Article
from utils.logging import info, error, debug

router = APIRouter()

@router.get("/articles/{article_id}", response_model=Article)
async def get_article_route(article_id: str):
    """Get a specific article by ID."""
    try:
        article = get_article(article_id)
        if not article:
            error("ARTICLE", "Not found", f"ID: {article_id}")
            raise HTTPException(status_code=404, detail="Article not found")
        debug("ARTICLE", "Retrieved", f"ID: {article_id}")
        return article
    except Exception as e:
        if not isinstance(e, HTTPException):
            error("ARTICLE", "Retrieval error", str(e))
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        raise e 