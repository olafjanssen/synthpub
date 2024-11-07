from typing import Dict, Optional
import json
import os

class PromptManager:
    """Manages prompts for different LLM tasks."""
    
    def __init__(self, prompts_path: Optional[str] = None):
        self.prompts = self._load_default_prompts()
        if prompts_path:
            self._load_custom_prompts(prompts_path)
    
    def _load_default_prompts(self) -> Dict:
        """Load default prompts."""
        return {
            'relevance': """
                Analyze the following content and determine its relevance to the topic '{topic}'.
                Content: {content}
                
                Provide a JSON response with:
                - relevance_score (0-1)
                - reasoning
                - key_topics_identified
            """,
            
            'extract_substance': """
                Extract the key information from the following content:
                {content}
                
                Provide a JSON response with:
                - key_points (list)
                - main_concepts (list)
                - supporting_evidence
                - knowledge_gaps
            """,
            
            'synthesize_article': """
                Create or update an article based on the following information:
                Content: {content}
                Topic: {topic}
                Existing Article: {existing_article}
                
                Provide a well-structured article that:
                - Maintains a coherent narrative
                - Integrates new information
                - Maintains academic tone
                - Includes proper citations
            """
        }
    
    def _load_custom_prompts(self, path: str) -> None:
        """Load custom prompts from file."""
        try:
            with open(path, 'r') as f:
                custom_prompts = json.load(f)
                self.prompts.update(custom_prompts)
        except Exception as e:
            print(f"Error loading custom prompts: {e}")
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get formatted prompt."""
        prompt_template = self.prompts.get(prompt_name)
        if not prompt_template:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        return prompt_template.format(**kwargs) 