"""
Configuration loader for Curator package.
"""
import yaml
from pathlib import Path

def load_config():
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

config = load_config() 