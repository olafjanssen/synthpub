from typing import Dict, List, Optional
from ..utils.db import db_session
from ai_curator.orchestrator import AICuratorOrchestrator
from ai_curator.config.curator_config import CuratorConfig

class CuratorService:
    def __init__(self):
        config = CuratorConfig()
        self.orchestrator = AICuratorOrchestrator(config.config)
    
    async def process_new_content(self, content_data: Dict) -> Dict:
        """Process new content through the AI Curator."""
        try:
            result = await self.orchestrator.process_content({
                'raw_content': content_data['content'],
                'topic': content_data['topic'],
                'metadata': content_data.get('metadata', {})
            })
            
            if result['status'] == 'success':
                # Save to database if processing was successful
                with db_session() as session:
                    # Create new article from processed content
                    article_data = result['data']['article']
                    from ..models.article import Article
                    
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

    async def update_article(self, article_id: int, new_content: Dict) -> Dict:
        """Update existing article with new content."""
        try:
            # Get existing article
            from ..models.article import Article
            with db_session() as session:
                article = session.query(Article).get(article_id)
                if not article:
                    return {'status': 'error', 'message': 'Article not found'}
                
                result = await self.orchestrator.update_existing_article(
                    article_id,
                    {
                        'raw_content': new_content['content'],
                        'topic': new_content['topic'],
                        'existing_article': article.to_dict()
                    }
                )
                
                if result['status'] == 'success':
                    # Update article in database
                    article_data = result['data']['article']
                    article.title = article_data['title']
                    article.content = article_data['content']
                    article.version += 1
                    
            return result
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)} 