from typing import Dict, Optional
import json
import os

class CuratorConfig:
    """Configuration manager for the AI Curator."""
    
    DEFAULT_CONFIG = {
        'llm': {
            'model_name': 'mistral',
            'base_url': 'http://localhost:11434',
            'timeout': 30.0
        },
        'relevance_filter': {
            'min_score': 0.7,
            'max_topics': 3
        },
        'substance_extractor': {
            'min_quality': 0.6,
            'max_key_points': 5
        },
        'article_synthesizer': {
            'max_length': 2000,
            'min_readability': 0.7
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
                self.config.update(custom_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def get_agent_config(self, agent_name: str) -> Dict:
        """Get configuration for specific agent."""
        return self.config.get(agent_name, {})
    
    def update_config(self, updates: Dict) -> None:
        """Update configuration values."""
        self.config.update(updates) 