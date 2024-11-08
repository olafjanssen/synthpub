from flask import Blueprint, jsonify, request
from ..services.curator_service import CuratorService
import asyncio

bp = Blueprint('curator', __name__, url_prefix='/api/curator')
curator_service = CuratorService()

@bp.route('/update-article/<int:article_id>', methods=['POST'])
def update_article(article_id):
    """Update an article using the curator service."""
    try:
        data = request.get_json()
        result = asyncio.run(curator_service.process_article(data, article_id))
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500