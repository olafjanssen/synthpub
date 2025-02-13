from fastapi import APIRouter, Depends
from ..db.knowledge_graph import knowledge_graph

router = APIRouter()

@router.post("/knowledge/document/")
async def add_document(doc_id: str, title: str, topic_id: str):
    """API endpoint to add a document to the knowledge graph."""
    knowledge_graph.create_document(doc_id, title, topic_id)
    return {"message": "Document added to knowledge graph"}

@router.get("/knowledge/documents/{topic_id}")
async def get_documents(topic_id: str):
    """API endpoint to fetch documents by topic."""
    docs = knowledge_graph.get_documents_by_topic(topic_id)
    return {"documents": docs}
