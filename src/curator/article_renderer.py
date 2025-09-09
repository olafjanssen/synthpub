"""
Article renderer for combining templates with LLM output.

This module handles rendering final markdown articles by combining
template structure with LLM-generated content.
"""

import json
from typing import Dict, Optional

from pydantic import BaseModel, ValidationError

from .template_parser import TemplateStructure
from utils.logging import debug, error, info


class ArticleRenderError(Exception):
    """Exception raised when article rendering fails."""
    pass


class LLMResponse(BaseModel):
    """Model for LLM JSON response validation."""
    
    title: Optional[str] = None
    # Dynamic fields will be added based on template sections


def validate_llm_response(
    response_text: str, 
    template_structure: TemplateStructure
) -> Dict[str, str]:
    """
    Validate and parse LLM JSON response.
    
    Args:
        response_text: Raw LLM response text
        template_structure: Template structure for validation
        
    Returns:
        Parsed and validated response data
        
    Raises:
        ArticleRenderError: If validation fails
    """
    try:
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Remove code fences if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()
        
        # Parse JSON
        response_data = json.loads(cleaned_text)
        
        # Validate required fields
        required_fields = set()
        if template_structure.title_placeholder:
            required_fields.add("title")
        
        for section in template_structure.sections:
            required_fields.add(section.id)
        
        missing_fields = required_fields - set(response_data.keys())
        if missing_fields:
            raise ArticleRenderError(
                f"Missing required fields in LLM response: {missing_fields}"
            )
        
        # Validate field types
        for field in required_fields:
            if not isinstance(response_data[field], str):
                raise ArticleRenderError(
                    f"Field '{field}' must be a string, got {type(response_data[field])}"
                )
        
        return response_data
        
    except json.JSONDecodeError as e:
        raise ArticleRenderError(f"Invalid JSON in LLM response: {e}")
    except Exception as e:
        raise ArticleRenderError(f"Failed to validate LLM response: {e}")


def render_article(
    template_structure: TemplateStructure,
    llm_response: Dict[str, str]
) -> str:
    """
    Render final article by combining template with LLM content.
    
    Args:
        template_structure: Parsed template structure
        llm_response: Validated LLM response data
        
    Returns:
        Rendered markdown article
    """
    lines = template_structure.raw_content.split('\n')
    rendered_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle title placeholder
        if line.strip() == '{title}' and 'title' in llm_response:
            rendered_lines.append(llm_response['title'])
            i += 1
            continue
        elif line.strip() == '# {title}' and 'title' in llm_response:
            rendered_lines.append(f"# {llm_response['title']}")
            i += 1
            continue
        
        # Handle headings and their guidance
        heading_match = None
        for section in template_structure.sections:
            if line.strip().startswith('#' * section.level + ' ' + section.heading):
                heading_match = section
                break
        
        if heading_match:
            # Add the heading
            rendered_lines.append(line)
            
            # Skip guidance lines and add LLM content instead
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if we hit another heading
                if any(lines[j].strip().startswith('#' * level + ' ') 
                       for level in range(1, 7)):
                    break
                j += 1
            
            # Add the LLM-generated content for this section
            section_content = llm_response.get(heading_match.id, '')
            if section_content.strip():
                rendered_lines.append('')  # Empty line after heading
                rendered_lines.append(section_content.strip())
                rendered_lines.append('')  # Empty line after content
            
            i = j
            continue
        
        # Regular line - keep as is
        rendered_lines.append(line)
        i += 1
    
    return '\n'.join(rendered_lines)


def process_llm_response(
    response_text: str,
    template_structure: TemplateStructure
) -> str:
    """
    Process LLM response and render final article.
    
    Args:
        response_text: Raw LLM response text
        template_structure: Parsed template structure
        
    Returns:
        Rendered markdown article
        
    Raises:
        ArticleRenderError: If processing fails
    """
    try:
        # Validate the LLM response
        llm_response = validate_llm_response(response_text, template_structure)
        
        # Render the final article
        rendered_article = render_article(template_structure, llm_response)
        
        info("RENDERER", "Article rendered successfully", 
             f"Sections: {len(template_structure.sections)}")
        
        return rendered_article
        
    except Exception as e:
        error("RENDERER", "Failed to process LLM response", str(e))
        raise ArticleRenderError(f"Failed to process LLM response: {e}")


def create_retry_prompt(
    original_prompt: str,
    validation_errors: str,
    template_structure: TemplateStructure
) -> str:
    """
    Create a retry prompt with validation error feedback.
    
    Args:
        original_prompt: Original LLM prompt
        validation_errors: Validation error details
        template_structure: Template structure for reference
        
    Returns:
        Enhanced prompt for retry
    """
    retry_prompt = f"""# RETRY: Article Generation with Structured Template

## Previous Response Issues
{validation_errors}

## Original Instructions
{original_prompt}

## Required JSON Format (REPEAT)
Return a JSON object with these exact keys:

"""
    
    if template_structure.title_placeholder:
        retry_prompt += "- `title`: Article title\n"
    
    for section in template_structure.sections:
        retry_prompt += f"- `{section.id}`: Content for '{section.heading}' section\n"
    
    retry_prompt += """
## Critical Requirements
- Return ONLY the JSON object
- No markdown formatting in JSON values
- No explanations or additional text
- Ensure all required keys are present
- All values must be strings

## CRITICAL - NO HALLUCINATION
- If you do not have sufficient information for a section, leave it empty or write 'No information available'
- Do NOT make up facts, statistics, or details that are not provided
- Do NOT invent examples or case studies
- Do NOT speculate about future events or outcomes
- Only include information that is explicitly provided in the context
- It is better to have an empty section than to include fabricated content
"""
    
    return retry_prompt
