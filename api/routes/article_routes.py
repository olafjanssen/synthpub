from flask import Blueprint, jsonify, request
from ..models.article import Article
from ..services.curator_service import CuratorService
from ..utils.db import db, db_session
import asyncio
from datetime import datetime

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

@bp.route('/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """Delete an article by ID."""
    try:
        with db_session() as session:
            article = session.query(Article).get(article_id)
            if not article:
                return jsonify({'status': 'error', 'message': 'Article not found'}), 404

            session.delete(article)
            session.commit()
            return jsonify({'status': 'success', 'message': 'Article deleted'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/create-initial', methods=['POST'])
def create_initial_article():
    """Create an initial article using the curator service."""
    try:
        data = request.get_json()
        topic_name = data.get('topic')
        if not topic_name:
            return jsonify({'status': 'error', 'message': 'Topic name is required'}), 400

        # Generate initial content using the curator service
        result = asyncio.run(curator_service.create_initial_article(topic_name))
        
        # Ensure a title is provided
        title = f"Introduction to {topic_name}"

        # Assuming you have a function to save the article
        article = save_article_to_db(title, result['content'], topic_name)
        
        return jsonify({'status': 'success', 'article': article.to_dict()}), 201
    except Exception as e:
        print(f"Error creating initial article: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def save_article_to_db(title: str, content: str, topic_name: str):
    """Save an article to the database."""
    from ..models import Article, Topic

    # Find the topic by name
    topic = Topic.query.filter_by(name=topic_name).first()
    if not topic:
        raise ValueError("Topic not found")

    # Create a new article
    article = Article(
        title=title,
        content=content,
        topic_id=topic.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1
    )

    # Add and commit the article to the database
    db.session.add(article)
    db.session.commit()

    return article
