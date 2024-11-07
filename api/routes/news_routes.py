from flask import Blueprint, jsonify, request
from ..services.article_service import trigger_content_update
from ..models.topic import Topic

bp = Blueprint('news', __name__, url_prefix='/api/news')

@bp.route('/update/<int:topic_id>', methods=['POST'])
def trigger_update(topic_id):
    """Trigger content update for a specific topic."""
    topic = Topic.query.get_or_404(topic_id)
    
    try:
        # Async task to update content
        task_id = trigger_content_update(topic)
        return jsonify({
            'message': f'Update triggered for topic: {topic.name}',
            'task_id': task_id
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to trigger update: {str(e)}'
        }), 500

@bp.route('/status/<string:task_id>', methods=['GET'])
def get_update_status(task_id):
    """Get the status of a content update task."""
    # This would typically check a task queue or background job status
    # For now, return a mock response
    return jsonify({
        'task_id': task_id,
        'status': 'pending',
        'message': 'Update in progress'
    })

@bp.route('/schedule', methods=['POST'])
def schedule_update():
    """Schedule a periodic content update for topics."""
    data = request.get_json()
    topic_ids = data.get('topic_ids', [])
    schedule = data.get('schedule', '0 */12 * * *')  # Default: every 12 hours
    
    try:
        # Here you would typically create a scheduled task
        # For now, return a mock response
        return jsonify({
            'message': 'Update schedule created',
            'topics': topic_ids,
            'schedule': schedule
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to schedule update: {str(e)}'
        }), 500

@bp.route('/schedule/<int:topic_id>', methods=['DELETE'])
def remove_schedule(topic_id):
    """Remove scheduled updates for a topic."""
    topic = Topic.query.get_or_404(topic_id)
    
    try:
        # Here you would typically remove the scheduled task
        return jsonify({
            'message': f'Update schedule removed for topic: {topic.name}'
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to remove schedule: {str(e)}'
        }), 500
