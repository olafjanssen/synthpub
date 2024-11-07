from typing import Dict, List, Optional
from ..models.topic import Topic
from ..utils.db import db

class TopicService:
    @staticmethod
    def get_all_topics() -> List[Topic]:
        """
        Retrieve all topics.
        """
        return Topic.query.order_by(Topic.name).all()

    @staticmethod
    def get_topic_by_id(topic_id: int) -> Optional[Topic]:
        """
        Retrieve a specific topic by ID.
        """
        return Topic.query.get(topic_id)

    @staticmethod
    def get_topic_by_name(name: str) -> Optional[Topic]:
        """
        Retrieve a specific topic by name.
        """
        return Topic.query.filter_by(name=name).first()

    @staticmethod
    def create_topic(data: Dict) -> Topic:
        """
        Create a new topic.
        """
        topic = Topic(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(topic)
        db.session.commit()
        return topic

    @staticmethod
    def update_topic(topic_id: int, data: Dict) -> Optional[Topic]:
        """
        Update an existing topic.
        """
        topic = Topic.query.get(topic_id)
        if not topic:
            return None

        if 'name' in data:
            existing = Topic.query.filter_by(name=data['name']).first()
            if existing and existing.id != topic_id:
                raise ValueError('Topic name already exists')
            topic.name = data['name']

        if 'description' in data:
            topic.description = data['description']

        db.session.commit()
        return topic

    @staticmethod
    def delete_topic(topic_id: int) -> bool:
        """
        Delete a topic
