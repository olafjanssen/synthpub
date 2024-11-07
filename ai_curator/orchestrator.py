from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
from .agents.relevance_filter import RelevanceFilter
from .agents.substance_extractor import SubstanceExtractor
from .agents.article_synthesizer import ArticleSynthesizer

class AICuratorOrchestrator:
    """Orchestrates the AI curation process across all agents."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize agents
        self.relevance_filter = RelevanceFilter(self.config.get('relevance_filter'))
        self.substance_extractor = SubstanceExtractor(self.config.get('substance_extractor'))
        self.article_synthesizer = ArticleSynthesizer(self.config.get('article_synthesizer'))
        
        # Processing queue
        self._queue = asyncio.Queue()
        
        # Processing history
        self._history: List[Dict] = []

    async def process_content(self, content: Dict) -> Dict:
        """
        Process new content through the curation pipeline.
        
        Args:
            content: Dict containing:
                - raw_content: str
                - topic: str
                - metadata: Dict
                - existing_article: Optional[Dict]
        """
        try:
            self.logger.info(f"Starting content processing for topic: {content.get('topic')}")
            
            # Add to processing queue
            await self._queue.put(content)
            
            # Step 1: Check relevance
            relevance_result = await self.relevance_filter.process({
                'content': content['raw_content'],
                'topic': content['topic']
            })
            
            if not relevance_result.get('data', {}).get('is_relevant', False):
                self.logger.info("Content deemed not relevant enough")
                return self._create_response('filtered', relevance_result)
            
            # Step 2: Extract substance
            extraction_result = await self.substance_extractor.process({
                'content': content['raw_content'],
                'topic': content['topic'],
                'metadata': content.get('metadata', {})
            })
            
            if extraction_result.get('status') != 'success':
                self.logger.error("Substance extraction failed")
                return self._create_response('failed', extraction_result)
            
            # Step 3: Synthesize article
            synthesis_result = await self.article_synthesizer.process({
                'extracted_content': extraction_result['data'],
                'existing_article': content.get('existing_article'),
                'topic': content['topic'],
                'metadata': content.get('metadata', {})
            })
            
            # Record processing history
            self._record_history(content, synthesis_result)
            
            return self._create_response('success', synthesis_result)
            
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            return self._create_response('error', {'message': str(e)})

    async def batch_process(self, contents: List[Dict]) -> List[Dict]:
        """Process multiple content items concurrently."""
        tasks = [self.process_content(content) for content in contents]
        return await asyncio.gather(*tasks)

    async def update_existing_article(self, article_id: int, new_content: Dict) -> Dict:
        """Update an existing article with new information."""
        try:
            # Process new content
            result = await self.process_content({
                **new_content,
                'existing_article': {'id': article_id}
            })
            
            if result['status'] == 'success':
                self.logger.info(f"Article {article_id} updated successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Update failed for article {article_id}: {str(e)}")
            return self._create_response('error', {'message': str(e)})

    def get_processing_history(self, limit: Optional[int] = None) -> List[Dict]:
        """Get processing history, optionally limited to recent entries."""
        history = self._history
        if limit:
            history = history[-limit:]
        return history

    def _create_response(self, status: str, data: Dict) -> Dict:
        """Create a standardized response format."""
        return {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }

    def _record_history(self, input_content: Dict, result: Dict) -> None:
        """Record processing history."""
        self._history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'topic': input_content.get('topic'),
            'status': result.get('status'),
            'metadata': {
                'input_length': len(input_content.get('raw_content', '')),
                'processing_result': result.get('status'),
                'confidence': result.get('data', {}).get('synthesis_metadata', {}).get('quality', 0)
            }
        }) 