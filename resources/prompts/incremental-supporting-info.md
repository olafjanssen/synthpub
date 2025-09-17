# Incremental Article Refinement: Supporting Information Integration

OBJECTIVE: Add supporting information to strengthen existing claims in the article with minimal, targeted changes. Make only 1-2 sentence modifications to preserve article flow.

CONTEXT:
Topic: {topic_title}
Description: {topic_description}

## EXISTING ARTICLE

{article}

## SUPPORTING INFORMATION TO ADD

{supporting_information}

## SOURCE CONTEXT

{new_context}

## REFINEMENT RULES

1. **MINIMAL CHANGES ONLY**
   - Modify only 1-2 sentences maximum
   - Preserve the existing article structure completely
   - Do not add new sections or paragraphs
   - Do not reorganize existing content

2. **ALLOWED OPERATIONS**
   - Add one sentence that supports an existing claim
   - Enhance an existing sentence with supporting details
   - Add a brief example or evidence to existing content
   - Strengthen an existing argument with additional context

3. **SUPPORTING PRINCIPLES**
   - Choose supporting information that directly reinforces existing points
   - Add credibility to current claims
   - Provide additional context for existing statements
   - Strengthen the article's overall argument

4. **PRESERVATION REQUIREMENTS**
   - Keep all existing section headers
   - Maintain paragraph structure
   - Preserve the overall narrative flow
   - Do not change the article's main argument or perspective

## OUTPUT REQUIREMENTS

Return the complete article with only the minimal changes needed to add supporting information. The output should be nearly identical to the input, with only 1-2 sentences modified or added.

**CRITICAL**: If the supporting information cannot be integrated with minimal changes, return the original article unchanged rather than making extensive modifications.
