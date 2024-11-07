from typing import Dict, List, Optional
import json
import logging
from .ollama_client import OllamaClient
from .prompt_manager import PromptManager

class AgentLLM:
    """
    LLM integration for AI Curator agents.
    Handles all LLM operations including generation, embeddings, and specific agent tasks.
    """
    
    def __init__(
        self,
        model_name: str = "smollm:135m",
        prompts_path: Optional[str] = None,
        config: Optional[Dict] = None
    ):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.llm = OllamaClient(
            model_name=model_name,
            base_url=self.config.get('base_url', 'http://localhost:11434'),
            config=self.config
        )
        self.prompt_manager = PromptManager(prompts_path)
        self.model_name = model_name

    async def analyze_relevance(self, content: str, topic: str) -> Dict:
        """
        Analyze content relevance using LLM.
        
        Args:
            content: The content to analyze
            topic: The topic to check relevance against
            
        Returns:
            Dict containing relevance analysis results
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                'relevance',
                content=content,
                topic=topic
            )
            response = await self.llm.generate(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Relevance analysis failed: {str(e)}")
            raise

    async def extract_substance(self, content: str) -> Dict:
        """
        Extract key information and insights from content.
        
        Args:
            content: The content to analyze
            
        Returns:
            Dict containing extracted information
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                'extract_substance',
                content=content
            )
            response = await self.llm.generate(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Substance extraction failed: {str(e)}")
            raise

    async def synthesize_content(
        self,
        content: str,
        topic: str,
        existing_article: Optional[Dict] = None
    ) -> Dict:
        """
        Synthesize new content or update existing article.
        
        Args:
            content: New content to synthesize
            topic: The topic of the article
            existing_article: Optional existing article to update
            
        Returns:
            Dict containing the synthesized article
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                'synthesize_article',
                content=content,
                topic=topic,
                existing_article=json.dumps(existing_article) if existing_article else "None"
            )
            response = await self.llm.generate(prompt)
            
            # Ensure the response is properly structured
            return {
                'content': response,
                'metadata': {
                    'topic': topic,
                    'is_update': existing_article is not None,
                    'source_length': len(content)
                }
            }
        except Exception as e:
            self.logger.error(f"Content synthesis failed: {str(e)}")
            raise

    async def get_embeddings(self, text: str) -> List[float]:
        """
        Get vector embeddings for text.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List of embedding values
        """
        try:
            return await self.llm.embed(text)
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {str(e)}")
            raise

    async def enhance_content(self, content: str) -> Dict:
        """
        Enhance content with additional elements like summaries and keywords.
        
        Args:
            content: Content to enhance
            
        Returns:
            Dict containing enhanced content elements
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                'enhance_content',
                content=content
            )
            response = await self.llm.generate(prompt)
            return json.loads(response)
        except Exception as e:
            self.logger.error(f"Content enhancement failed: {str(e)}")
            raise

    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.llm.is_available()

    async def validate_response(self, response: str, expected_format: str) -> bool:
        """
        Validate LLM response format.
        
        Args:
            response: The LLM response to validate
            expected_format: Expected format description
            
        Returns:
            bool indicating if response is valid
        """
        try:
            prompt = self.prompt_manager.get_prompt(
                'validate_response',
                response=response,
                expected_format=expected_format
            )
            validation_result = await self.llm.generate(prompt)
            return json.loads(validation_result)['is_valid']
        except Exception:
            return False

    async def generate_initial_content(self, topic: str) -> str:
        """Generate initial content for a given topic using the Ollama LLM."""
        try:
            # Define the prompt for the LLM
            prompt = f"Write an introductory article about the topic: {topic}. Include key points and insights."

            # Call the Ollama API to generate content
            response = await self.llm.generate(
                model=self.model_name,
                prompt=prompt,
                max_tokens=500,  # Adjust the token limit as needed
                temperature=0.7  # Adjust the creativity level as needed
            )
            print(f"Generated content: {response}")
            # Extract the generated content from the response
            initial_content = response.strip()
            return initial_content

        except Exception as e:
            print(f"Error generating content with Ollama: {e}")
            raise