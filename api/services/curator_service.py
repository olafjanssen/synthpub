from typing import Dict, List, Optional
from ..utils.db import db_session
from ai_curator.orchestrator import AICuratorOrchestrator
from ai_curator.config.curator_config import CuratorConfig
from ai_curator.agents.article_synthesizer import ArticleSynthesizer
from ..models.article import Article

class CuratorService:
    def __init__(self):
        config = CuratorConfig()
        self.orchestrator = AICuratorOrchestrator(config.config)
        self.article_synthesizer = ArticleSynthesizer(config.config)
    
    async def create_initial_article(self, topic: str) -> Dict:
        """Create an initial article using the ArticleSynthesizer."""
        try:
            result = await self.article_synthesizer.generate_initial_content(topic)
            if 'content' not in result:
                raise ValueError("Content generation failed")
            return result
        except Exception as e:
            print(f"Error in create_initial_article: {e}")
            return {'status': 'error', 'message': str(e)}

    async def process_article(self, content_data: Dict, article_id: Optional[int] = None) -> Dict:
        """Process article content - handles both new and existing articles."""
        try:
            with db_session() as session:
                existing_article = None
                if article_id:
                    existing_article = session.query(Article).get(article_id)
                    if not existing_article:
                        return {'status': 'error', 'message': 'Article not found'}

                # Prepare orchestrator input
                orchestrator_data = {
                    'raw_content': content_data['content'],
                    'topic': content_data['topic'],
                    'metadata': content_data.get('metadata', {})
                }

                if existing_article:
                    orchestrator_data['existing_article'] = existing_article.to_dict()
                    result = await self.orchestrator.update_existing_article(article_id, orchestrator_data)
                else:
                    result = await self.orchestrator.process_content(orchestrator_data)

                if result['status'] == 'success':
                    article_data = result['data']['article']
                    if existing_article:
                        # Update existing
                        existing_article.title = article_data['title']
                        existing_article.content = article_data['content']
                        existing_article.version += 1
                    else:
                        # Create new
                        article = Article(
                            title=article_data['title'],
                            content=article_data['content'],
                            topic_id=content_data['topic_id'],
                            version=1
                        )
                        session.add(article)

                return result

        except Exception as e:
            return {'status': 'error', 'message': str(e)}