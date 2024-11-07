from flask import Blueprint, jsonify, request
from ..models.topic import Topic
from ..utils.db import db

bp = Blueprint('topics', __name__, url_prefix='/api/topics')

@bp.route('/', methods=['GET'])
def get_topics():
    """Get all topics."""
    topics = Topic.query.all()
    return jsonify([topic.to_dict() for topic in topics])

@bp.route('/<int:id>', methods=['GET'])
def get_topic(id):
    """Get a specific topic by ID."""
    topic = Topic.query.get_or_404(id)
    return jsonify(topic.to_dict())

@bp.route('/', methods=['POST'])
def create_topic():
    """Create a new topic."""
    data = request.get_json()
    
    # Check if topic already exists
    existing_topic = Topic.query.filter_by(name=data['name']).first()
    if existing_topic:
        return jsonify({'error': 'Topic already exists'}), 409
    
    topic = Topic(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(topic)
    db.session.commit()
    return jsonify(topic.to_dict()), 201

@bp.route('/<int:id>', methods=['PUT'])
def update_topic(id):
    """Update an existing topic."""
    topic = Topic.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        # Check if new name conflicts with existing topic
        existing_topic = Topic.query.filter_by(name=data['name']).first()
        if existing_topic and existing_topic.id != id:
            return jsonify({'error': 'Topic name already exists'}), 409
        topic.name = data['name']
    
    if 'description' in data:
        topic.description = data['description']
    
    db.session.commit()
    return jsonify(topic.to_dict())

@bp.route('/<int:id>', methods=['DELETE'])
def delete_topic(id):
    """Delete a topic."""
    topic = Topic.query.get_or_404(id)
    db.session.delete(topic)
    db.session.commit()
    return '', 204
