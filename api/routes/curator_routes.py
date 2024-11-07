from flask import Blueprint, jsonify, request
from ..services.curator_service import CuratorService
import asyncio

bp = Blueprint('curator', __name__, url_prefix='/api/curator')
curator_service = CuratorService()

@bp.route('/process', methods=['POST'])
def process_content():
    """Process new content through the AI Curator."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['content', 'topic', 'topic_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400
    
    # Process content asynchronously
    result = asyncio.run(curator_service.process_new_content(data))
    return jsonify(result)

@bp.route('/update/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """Update existing article with new content."""
    data = request.get_json()
    
    # Validate input
    if 'content' not in data or 'topic' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400
    
    # Update article asynchronously
    result = asyncio.run(curator_service.update_article(article_id, data))
    return jsonify(result)

@bp.route('/status', methods=['GET'])
def get_status():
    """Get curator processing status and history."""
    history = curator_service.orchestrator.get_processing_history(limit=10)
    return jsonify({
        'status': 'active',
        'recent_history': history
    }) 