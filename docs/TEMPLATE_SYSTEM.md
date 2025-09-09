# Structured Article Template System

This document describes the new structured article template system that allows non-technical editors to define article structures and expectations in Markdown templates.

## Overview

The template system provides a pipeline for generating articles that strictly adhere to predefined structures:

1. **Template Definition**: Editors create Markdown templates with headings and guidance
2. **Structure Parsing**: The system extracts headings and generates stable section IDs
3. **LLM Prompting**: Structured prompts guide the LLM to generate only section content
4. **Validation**: JSON responses are validated against generated schemas
5. **Rendering**: Final articles combine template structure with LLM content

## Key Features

- **Strict Structure Enforcement**: Articles must follow the exact template structure
- **Non-Technical Editor Friendly**: Templates are simple Markdown files
- **Automatic Validation**: JSON schema validation ensures compliance
- **Retry Logic**: Invalid responses trigger structured retries
- **Backward Compatibility**: Falls back to legacy prompt system if needed

## Template Format

Templates are Markdown files with the following structure:

```markdown
# {title}

## Section Heading

Guidance text for this section. This can include:
- Bullet points
- Specific instructions
- Format requirements
- Content constraints

## Another Section

More guidance text...

### Subsection

Guidance for subsections...
```

### Template Rules

1. **Title Placeholder**: Use `{title}` for dynamic article titles
2. **Headings**: Use `#`, `##`, `###`, etc. for section hierarchy
3. **Guidance**: Any text following a heading until the next heading
4. **Section IDs**: Auto-generated from headings (slugified, unique)

## Example Templates

### Project Update Template

```markdown
# {title}

## Executive Summary

Provide a concise overview of the project's current status, key achievements, and immediate next steps. Keep this section to 2-3 sentences maximum.

## Project Status

Describe the current phase of the project, including:
- Overall progress percentage
- Current milestones achieved
- Any delays or challenges encountered

## Key Achievements

List the most significant accomplishments since the last update:
- Specific deliverables completed
- Major milestones reached
- Important decisions made
```

### News Analysis Template

```markdown
# {title}

## Breaking News Summary

Provide a clear, factual summary of the main news event. Include the who, what, when, where, and why in 2-3 concise paragraphs.

## Context and Background

Explain the broader context that led to this news:
- Historical background
- Previous related events
- Key stakeholders involved
- Relevant policies or regulations
```

## Usage

### Basic Article Generation

```python
from curator.template_service import template_service

# Generate article using template
article_content = template_service.generate_article_with_template(
    template_id="project-update-template",
    topic_title="AI Research Project Update",
    topic_description="Monthly progress report on our AI research initiative"
)
```

### Article Refinement

```python
# Refine existing article with new information
refined_content = template_service.refine_article_with_template(
    template_id="project-update-template",
    topic_title="AI Research Project Update",
    topic_description="Monthly progress report on our AI research initiative",
    existing_article=current_article_content,
    new_context=new_feed_content,
    new_information="New developments...",
    enforcing_information="Supporting evidence...",
    contradicting_information="Conflicting information..."
)
```

### Custom Template Loading

```python
from curator.template_parser import parse_template

# Load and parse a custom template
template_content = Path("my-template.md").read_text()
template_structure = parse_template(template_content)

# Generate JSON schema
from curator.template_parser import create_json_schema
schema = create_json_schema(template_structure)
```

## Integration with Curator Workflow

The template system integrates seamlessly with the existing curator workflow:

### Article Generator

The `article_generator.py` step now:
1. Attempts to use template-based generation first
2. Falls back to legacy prompt system if template fails
3. Maintains backward compatibility

### Article Refiner

The `article_refiner.py` step now:
1. Uses templates for structured refinement
2. Preserves template structure during updates
3. Falls back to legacy system if needed

## Template Management

### Adding New Templates

1. Create a new `.md` file in `resources/prompts/`
2. Follow the template format with headings and guidance
3. The system will automatically detect and load the template
4. Use the filename (without extension) as the template ID

### Template Validation

Templates are automatically validated when loaded:
- Headings must be properly formatted
- Section IDs must be unique
- Guidance text is preserved

## Error Handling

### LLM Response Validation

The system validates LLM responses against generated schemas:
- All required sections must be present
- Values must be strings
- No extra fields allowed

### Retry Logic

Invalid responses trigger structured retries:
1. Validation errors are sent back to the LLM
2. Enhanced prompts guide correction
3. Maximum retry attempts prevent infinite loops

### Fallback Behavior

If template-based generation fails:
1. System logs the error
2. Falls back to legacy prompt system
3. Continues normal workflow

## Configuration

### LLM Configuration

Templates use the same LLM configurations as the legacy system:
- `article_generation`: For new article creation
- `article_refinement`: For article updates

### Template Caching

Templates are cached in memory for performance:
- First load parses and caches the template
- Subsequent uses load from cache
- Cache is cleared on application restart

## Best Practices

### Template Design

1. **Clear Headings**: Use descriptive, specific headings
2. **Detailed Guidance**: Provide comprehensive instructions for each section
3. **Consistent Structure**: Maintain logical flow and hierarchy
4. **Reusable Patterns**: Design templates for multiple use cases

### Content Guidelines

1. **Section-Specific**: Guidance should be specific to each section
2. **Format Requirements**: Specify any formatting needs
3. **Length Constraints**: Include word count or length guidelines
4. **Quality Standards**: Define content quality expectations

### Testing

1. **Template Validation**: Test templates with sample content
2. **LLM Response Testing**: Verify generated content meets requirements
3. **Integration Testing**: Test with real curator workflow
4. **Error Scenarios**: Test fallback and error handling

## Troubleshooting

### Common Issues

1. **Template Not Found**: Check template ID and file location
2. **Validation Errors**: Verify LLM response format
3. **Rendering Issues**: Check template structure and guidance
4. **Performance Issues**: Monitor template caching and LLM calls

### Debug Information

Enable debug logging to see:
- Template parsing details
- LLM prompt generation
- Validation results
- Retry attempts

## Future Enhancements

### Planned Features

1. **Template Versioning**: Track template changes over time
2. **Dynamic Sections**: Conditional sections based on content
3. **Template Inheritance**: Base templates with specializations
4. **Visual Editor**: GUI for template creation and editing

### Integration Opportunities

1. **Content Management**: Integration with CMS systems
2. **Workflow Automation**: Advanced workflow triggers
3. **Quality Metrics**: Content quality scoring
4. **A/B Testing**: Template performance comparison
