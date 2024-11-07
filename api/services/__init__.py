from typing import TypeVar, Type, Optional
from ..utils.db import db

T = TypeVar('T')

class BaseService:
    @staticmethod
    def get_by_id(model: Type[T], id: int) -> Optional[T]:
        """
        Generic method to retrieve an entity by ID.
        """
        return model.query.get(id)

    @staticmethod
    def create(model: Type[T], **kwargs) -> T:
        """
        Generic method to create an entity.
        """
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    @staticmethod
    def delete(instance: T) -> bool:
        """
        Generic method to delete an entity.
        """
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
