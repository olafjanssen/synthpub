from flask import Blueprint, jsonify, request
from ..models.article import Article
from ..services.curator_service import CuratorService
from ..utils.db import db, db_session
import asyncio

bp = Blueprint('articles', __name__, url_prefix='/api/articles')
curator_service = CuratorService()

@bp.route('/', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify([article.to_dict() for article in articles])

@bp.route('/<int:id>', methods=['GET'])
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_dict())

@bp.route('/', methods=['POST'])
def create_article():
    data = request.get_json()
    article = Article(
        title=data['title'],
        content=data['content'],
        topic_id=data['topic_id']
    )
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_dict()), 201

@bp.route('/synthesize', methods=['POST'])
def synthesize_article():
    """Create a new article using AI Curator."""
    data = request.get_json()
    
    # Validate input
    required_fields = ['content', 'topic', 'topic_id']
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields'
        }), 400
    
    # Process with AI Curator
    result = asyncio.run(curator_service.process_new_content(data))
    return jsonify(result)

@bp.route('/update-by-topic/<int:topic_id>', methods=['POST'])
def update_article_by_topic(topic_id):
    """Update article related to a specific topic."""
    try:
        with db_session() as session:
            article = session.query(Article).filter_by(topic_id=topic_id).first()
            if not article:
                return jsonify({'status': 'error', 'message': 'Article not found'}), 404

            # Call the curator service to update the article
            result = asyncio.run(curator_service.update_article(article.id, {
                'content': article.content,
                'topic': article.topic.name
            }))

            return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
