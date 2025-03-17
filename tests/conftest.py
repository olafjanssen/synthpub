"""
Common test fixtures for SynthPub tests.
"""
import pytest
import yaml

@pytest.fixture
def sample_settings_data():
    """Return sample settings data for tests."""
    return {
        'env_vars': {
            'OPENAI_API_KEY': 'test_openai_key',
            'YOUTUBE_API_KEY': 'test_youtube_key',
            'PEXELS_API_KEY': 'test_pexels_key',
        },
        'llm': {
            'article_generation': {
                'provider': 'openai',
                'model_name': 'gpt-4',
                'max_tokens': 800,
            },
        },
        'db_path': '../test_db',
    }

@pytest.fixture
def temp_settings_file(tmp_path, sample_settings_data):
    """Create a temporary settings.yaml file for testing."""
    settings_file = tmp_path / "settings.yaml"
    
    with open(settings_file, 'w') as f:
        yaml.dump(sample_settings_data, f)
    
    return settings_file

@pytest.fixture
def mock_feed_data():
    """Return mock feed data for tests."""
    return {
        "feed": {
            "title": "Test Feed",
            "link": "https://example.com/feed",
            "description": "A test feed for unit tests",
        },
        "entries": [
            {
                "title": "Test Article 1",
                "link": "https://example.com/article1",
                "summary": "This is a test article for unit tests",
                "published": "Mon, 01 Jan 2023 12:00:00 GMT",
            },
            {
                "title": "Test Article 2",
                "link": "https://example.com/article2",
                "summary": "This is another test article for unit tests",
                "published": "Tue, 02 Jan 2023 12:00:00 GMT",
            },
        ],
    } 