from typing import Dict, List, Optional
from .base_agent import BaseAgent
from ..llm.agent_llm import AgentLLM

class SubstanceExtractor(BaseAgent):
    """Agent for extracting valuable substance from content."""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.llm = AgentLLM(
            model_name=config.get('model_name', 'smollm:135m'),
            config=config.get('llm_config')
        )
    
    async def process(self, data: Dict) -> Dict:
        """
        Extract key information and insights from content.
        
        Args:
            data: Dict containing:
                - content: str (raw content)
                - topic: str (associated topic)
                - metadata: Dict (optional additional context)
        Returns:
            Dict containing extracted information
        """
        if not self.validate_input(data):
            return {'status': 'error', 'message': 'Invalid input data'}
        
        try:
            # Use LLM to extract key points and concepts
            extraction_result = await self.llm.extract_substance(data['content'])
            
            return self.format_output({
                'key_points': extraction_result['key_points'],
                'main_concepts': extraction_result['main_concepts'],
                'supporting_evidence': extraction_result['supporting_evidence'],
                'knowledge_gaps': extraction_result['knowledge_gaps']
            })
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
