"""
Template parser for markdown-based article templates.

This module parses markdown templates to extract headings and guidance,
generates stable section IDs, and creates JSON schemas for LLM responses.
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from pydantic import BaseModel, Field


class Section(BaseModel):
    """Represents a section in a markdown template."""
    
    id: str = Field(description="Auto-generated stable ID for the section")
    heading: str = Field(description="Original heading text")
    level: int = Field(description="Heading level (1-6)")
    guidance: str = Field(description="Guidance text following the heading")
    line_number: int = Field(description="Line number where heading starts")


class TemplateStructure(BaseModel):
    """Represents the parsed structure of a markdown template."""
    
    title_placeholder: Optional[str] = Field(default=None, description="Title placeholder if present")
    sections: List[Section] = Field(description="List of sections in order")
    raw_content: str = Field(description="Original template content")


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: Text to convert
        
    Returns:
        URL-friendly slug
    """
    # Convert to lowercase and replace spaces with hyphens
    text = text.lower().strip()
    # Remove special characters except hyphens and underscores
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces and multiple hyphens with single hyphen
    text = re.sub(r'[\s_-]+', '-', text)
    # Remove leading/trailing hyphens
    return text.strip('-')


def generate_section_id(heading: str, existing_ids: set) -> str:
    """
    Generate a unique section ID from a heading.
    
    Args:
        heading: The heading text
        existing_ids: Set of existing IDs to avoid duplicates
        
    Returns:
        Unique section ID
    """
    base_id = slugify(heading)
    if not base_id:
        base_id = "section"
    
    # Ensure uniqueness
    counter = 1
    section_id = base_id
    while section_id in existing_ids:
        section_id = f"{base_id}-{counter}"
        counter += 1
    
    return section_id


def parse_template(template_content: str) -> TemplateStructure:
    """
    Parse a markdown template to extract structure and guidance.
    
    Args:
        template_content: Raw markdown template content
        
    Returns:
        Parsed template structure
    """
    lines = template_content.split('\n')
    sections = []
    existing_ids = set()
    title_placeholder = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for title placeholder
        if line.startswith('{title}') and not title_placeholder:
            title_placeholder = line
        
        # Check for headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            
            # Collect guidance text (everything until next heading or end)
            guidance_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if we hit another heading
                if re.match(r'^#{1,6}\s+', next_line):
                    break
                # Include non-empty lines in guidance
                if next_line:
                    guidance_lines.append(next_line)
                j += 1
            
            guidance = '\n'.join(guidance_lines).strip()
            
            # Generate unique section ID
            section_id = generate_section_id(heading_text, existing_ids)
            existing_ids.add(section_id)
            
            sections.append(Section(
                id=section_id,
                heading=heading_text,
                level=level,
                guidance=guidance,
                line_number=i + 1
            ))
        
        i += 1
    
    return TemplateStructure(
        title_placeholder=title_placeholder,
        sections=sections,
        raw_content=template_content
    )


def create_json_schema(template_structure: TemplateStructure) -> Dict:
    """
    Create a JSON schema from template structure for LLM validation.
    
    Args:
        template_structure: Parsed template structure
        
    Returns:
        JSON schema dictionary
    """
    properties = {}
    required = []
    
    # Add title if placeholder exists
    if template_structure.title_placeholder:
        properties["title"] = {
            "type": "string",
            "description": "Article title"
        }
        required.append("title")
    
    # Add section properties
    for section in template_structure.sections:
        properties[section.id] = {
            "type": "string",
            "description": f"Content for section: {section.heading}"
        }
        required.append(section.id)
    
    schema = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False
    }
    
    return schema


def create_llm_prompt(
    template_structure: TemplateStructure,
    topic_title: str,
    topic_description: str,
    context: Optional[str] = None
) -> str:
    """
    Create LLM prompt with template guidance.
    
    Args:
        template_structure: Parsed template structure
        topic_title: Article topic title
        topic_description: Article topic description
        context: Additional context (for refinement)
        
    Returns:
        Formatted LLM prompt
    """
    prompt_parts = [
        "# Article Generation with Structured Template",
        "",
        f"**Topic:** {topic_title}",
        f"**Description:** {topic_description}",
        ""
    ]
    
    if context:
        prompt_parts.extend([
            "## Context",
            context,
            ""
        ])
    
    prompt_parts.extend([
        "## Template Structure",
        "",
        "You must generate content that follows this exact structure. ",
        "Return ONLY a JSON object with the specified keys. ",
        "No explanations, no code fences, no additional text.",
        ""
    ])
    
    # Add section guidance
    for section in template_structure.sections:
        prompt_parts.extend([
            f"### {section.heading}",
            section.guidance,
            ""
        ])
    
    # Add JSON format instructions
    prompt_parts.extend([
        "## Required JSON Format",
        "",
        "Return a JSON object with these exact keys:",
        ""
    ])
    
    if template_structure.title_placeholder:
        prompt_parts.append("- `title`: Article title")
    
    for section in template_structure.sections:
        prompt_parts.append(f"- `{section.id}`: Content for '{section.heading}' section")
    
    prompt_parts.extend([
        "",
        "**Important:**",
        "- Return ONLY the JSON object",
        "- No markdown formatting in the JSON values",
        "- No explanations or additional text",
        "- Ensure all required keys are present"
    ])
    
    return '\n'.join(prompt_parts)
