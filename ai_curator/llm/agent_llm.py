from typing import Dict, Optional, List
import json
from .ollama_client import OllamaClient
from .prompt_manager import PromptManager

class AgentLLM:
    """LLM integration for AI Curator agents."""
    
    def __init__(
        self,
        model_name: str = "mistral",
        prompts_path: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        self.llm = OllamaClient(model_name, config=config)
        self.prompt_manager = PromptManager(prompts_path)
    
    async def analyze_relevance(self, content: str, topic: str) -> Dict:
        """Analyze content relevance using LLM."""
        prompt = self.prompt_manager.get_prompt(
            'relevance',
            content=content,
            topic=topic
        )
        response = await self.llm.generate(prompt)
        return json.loads(response)
    
    async def extract_substance(self, content: str) -> Dict:
        """Extract substance from content using LLM."""
        prompt = self.prompt_manager.get_prompt(
            'extract_substance',
            content=content
        )
        response = await self.llm.generate(prompt)
        return json.loads(response)
    
    async def synthesize_content(
        self,
        content: str,
        topic: str,
        existing_article: Optional[Dict] = None
    ) -> str:
        """Synthesize content using LLM."""
        prompt = self.prompt_manager.get_prompt(
            'synthesize_article',
            content=content,
            topic=topic,
            existing_article=json.dumps(existing_article) if existing_article else "None"
        )
        return await self.llm.generate(prompt)
    
    async def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text."""
        return await self.llm.embed(text) 