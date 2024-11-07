from .article_routes import bp as article_bp
from .topic_routes import bp as topic_bp
from .news_routes import bp as news_bp

# Export the blueprints
article_routes = article_bp
topic_routes = topic_bp
news_routes = news_bp
