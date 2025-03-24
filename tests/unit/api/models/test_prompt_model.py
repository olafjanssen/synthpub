"""
Unit tests for the Prompt model.
"""

from src.api.models.prompt import Prompt


def test_prompt_creation():
    """Test creating a Prompt instance."""
    prompt = Prompt(
        id="prompt-123",
        name="Article Generator",
        template="Generate an article about {topic} with the following information: {info}",
    )

    assert prompt.id == "prompt-123"
    assert prompt.name == "Article Generator"
    assert (
        prompt.template
        == "Generate an article about {topic} with the following information: {info}"
    )


def test_prompt_with_complex_template():
    """Test Prompt with a more complex template structure."""
    template = """
    You are an expert writer on {topic}.
    Write an article with the following requirements:
    - Include the latest information: {new_info}
    - Consider this existing information: {existing_info}
    - Address these contradicting points: {contradicting_info}
    - Use a {tone} tone
    - Format the article as {format}
    """

    prompt = Prompt(
        id="prompt-456", name="Advanced Article Generator", template=template
    )

    assert prompt.id == "prompt-456"
    assert prompt.name == "Advanced Article Generator"
    assert prompt.template == template
    assert "{topic}" in prompt.template
    assert "{new_info}" in prompt.template
    assert "{format}" in prompt.template


def test_prompt_from_fixture(sample_prompt_data):
    """Test creating a Prompt from fixture data."""
    prompt = Prompt(**sample_prompt_data)

    assert prompt.id == sample_prompt_data["id"]
    assert prompt.name == sample_prompt_data["name"]
    assert prompt.template == sample_prompt_data["template"]
    assert "{topic}" in prompt.template
    assert "{placeholder}" in prompt.template
