from typing import Dict, Optional
from .base_agent import BaseAgent
from ..llm.agent_llm import AgentLLM

class ArticleSynthesizer(BaseAgent):
    """Agent for synthesizing new articles and updating existing ones."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.llm = AgentLLM(
            model_name=config.get('model_name', 'smollm:135m'),
            config=config.get('llm_config')
        )
    
    async def process(self, data: Dict) -> Dict:
        """Process data to synthesize or update an article."""
        try:
            # Example implementation: Use LLM to synthesize content
            synthesized_content = await self.llm.synthesize_content(
                data['content'],
                data['topic'],
                data.get('existing_article')
            )
            return {'content': synthesized_content}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def generate_initial_content(self, topic: str) -> Dict:
        """Generate initial content for a given topic.
        
        Args:
            topic: The topic to generate content for
            
        Returns:
            Dict containing generated content and metadata
            
        Raises:
            ValueError: If topic is empty or invalid
            RuntimeError: If content generation fails
        """
        if not topic or not isinstance(topic, str):
            raise ValueError("Topic must be a non-empty string")
            
        try:
            content = await self.llm.generate_initial_content(topic)
            print(f"Generated content: {content}")
            return {
                'content': content,
                'status': 'success',
                'metadata': {
                    'topic': topic,
                    'length': len(content)
                }
            }
        except Exception as e:
            raise RuntimeError(f"Failed to generate initial content: {str(e)}")