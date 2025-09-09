"""
Demo script showing how the new template system works.

This script demonstrates the structured article generation pipeline
using markdown templates with strict section guidelines.
"""

import json
from pathlib import Path

# Add the src directory to the path so we can import our modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from curator.template_parser import parse_template, create_json_schema, create_llm_prompt
from curator.article_renderer import process_llm_response


def demo_template_parsing():
    """Demonstrate template parsing functionality."""
    print("=== Template Parsing Demo ===\n")
    
    # Load a sample template
    template_path = Path(__file__).parent.parent.parent / "resources" / "prompts" / "project-update-template.md"
    
    if not template_path.exists():
        print(f"Template file not found: {template_path}")
        return
    
    template_content = template_path.read_text(encoding="utf-8")
    print("Original Template:")
    print("-" * 50)
    print(template_content)
    print("-" * 50)
    print()
    
    # Parse the template
    template_structure = parse_template(template_content)
    
    print("Parsed Structure:")
    print(f"Title placeholder: {template_structure.title_placeholder}")
    print(f"Number of sections: {len(template_structure.sections)}")
    print()
    
    for section in template_structure.sections:
        print(f"Section: {section.heading}")
        print(f"  ID: {section.id}")
        print(f"  Level: {section.level}")
        print(f"  Guidance: {section.guidance[:100]}...")
        print()
    
    # Create JSON schema
    schema = create_json_schema(template_structure)
    print("Generated JSON Schema:")
    print(json.dumps(schema, indent=2))
    print()
    
    # Create LLM prompt
    prompt = create_llm_prompt(
        template_structure,
        "AI Research Project Update",
        "Monthly progress report on our AI research initiative"
    )
    
    print("Generated LLM Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


def demo_article_rendering():
    """Demonstrate article rendering with mock LLM response."""
    print("=== Article Rendering Demo ===\n")
    
    # Load template
    template_path = Path(__file__).parent.parent.parent / "resources" / "prompts" / "project-update-template.md"
    template_content = template_path.read_text(encoding="utf-8")
    template_structure = parse_template(template_content)
    
    # Mock LLM response
    mock_response = {
        "title": "AI Research Project - March 2024 Update",
        "executive-summary": "The AI research project has made significant progress this month, with key milestones achieved in model training and data collection. The team is on track to deliver the first prototype by the end of Q2.",
        "project-status": "The project is currently in Phase 2 of development, with 75% completion. We have successfully completed the data preprocessing pipeline and are now focusing on model optimization.",
        "key-achievements": "• Completed data preprocessing pipeline\n• Achieved 95% accuracy on validation set\n• Deployed staging environment\n• Onboarded two new team members",
        "technical-updates": "Implemented advanced neural network architecture with attention mechanisms. Optimized training process reduced training time by 40%. Added comprehensive logging and monitoring system.",
        "challenges-and-risks": "Current challenges include limited GPU resources and potential data quality issues in the new dataset. Risk mitigation strategies are in place.",
        "next-steps": "• Complete model fine-tuning\n• Conduct user acceptance testing\n• Prepare production deployment\n• Document API specifications",
        "team-updates": "Added two new data scientists to the team. Reorganized project structure for better collaboration."
    }
    
    # Convert to JSON string (as LLM would return)
    llm_response = json.dumps(mock_response, indent=2)
    
    print("Mock LLM Response:")
    print("-" * 50)
    print(llm_response)
    print("-" * 50)
    print()
    
    # Process and render article
    try:
        rendered_article = process_llm_response(llm_response, template_structure)
        
        print("Rendered Article:")
        print("-" * 50)
        print(rendered_article)
        print("-" * 50)
        print()
        
    except Exception as e:
        print(f"Error rendering article: {e}")


def demo_template_validation():
    """Demonstrate template validation with invalid responses."""
    print("=== Template Validation Demo ===\n")
    
    # Load template
    template_path = Path(__file__).parent.parent.parent / "resources" / "prompts" / "project-update-template.md"
    template_content = template_path.read_text(encoding="utf-8")
    template_structure = parse_template(template_content)
    
    # Test with invalid response (missing required fields)
    invalid_response = {
        "title": "Test Article",
        "executive-summary": "This is a test."
        # Missing other required fields
    }
    
    llm_response = json.dumps(invalid_response)
    
    print("Invalid LLM Response (missing fields):")
    print("-" * 50)
    print(llm_response)
    print("-" * 50)
    print()
    
    try:
        rendered_article = process_llm_response(llm_response, template_structure)
        print("Unexpectedly succeeded!")
    except Exception as e:
        print(f"Validation correctly caught error: {e}")
        print()


if __name__ == "__main__":
    print("Template System Demo")
    print("=" * 60)
    print()
    
    demo_template_parsing()
    demo_article_rendering()
    demo_template_validation()
    
    print("Demo completed!")
