from flask import Flask
from flask_cors import CORS
from .config import Config
from .utils.db import init_db, db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    init_db(app)

    # Register blueprints
    from .routes import (
        article_routes, 
        topic_routes, 
        news_routes,
        curator_routes
    )
    
    app.register_blueprint(article_routes)
    app.register_blueprint(topic_routes)
    app.register_blueprint(news_routes)
    app.register_blueprint(curator_routes)

    return app
