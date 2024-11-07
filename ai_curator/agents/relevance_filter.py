from typing import Dict, List, Optional
import numpy as np
from .base_agent import BaseAgent
from ..llm.agent_llm import AgentLLM

class RelevanceFilter(BaseAgent):
    """Agent for filtering content based on relevance to topics."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.llm = AgentLLM(
            model_name=config.get('model_name', 'smollm:135m'),
            config=config.get('llm_config')
        )
    
    async def process(self, data: Dict) -> Dict:
        """
        Process incoming content and determine its relevance.
        
        Args:
            data: Dict containing 'content' and 'topic' keys
        Returns:
            Dict with relevance score and classification
        """
        if not self.validate_input(data):
            return {'status': 'error', 'message': 'Invalid input data'}
        
        try:
            # Use LLM for relevance analysis
            relevance_result = await self.llm.analyze_relevance(
                data['content'],
                data['topic']
            )
            
            return self.format_output({
                'relevance_score': relevance_result['relevance_score'],
                'is_relevant': relevance_result['relevance_score'] > 0.7,
                'reasoning': relevance_result['reasoning'],
                'topics': relevance_result['key_topics_identified']
            })
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
