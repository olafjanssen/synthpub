# Incremental Article Refinement: New Information Integration

OBJECTIVE: Integrate new information into the existing article with minimal, targeted changes. Make only 1-2 sentence modifications to preserve article flow and structure.

CONTEXT:
Topic: {topic_title}
Description: {topic_description}

## EXISTING ARTICLE

{article}

## NEW INFORMATION TO INTEGRATE

{new_information}

## SOURCE CONTEXT

{new_context}

## REFINEMENT RULES

1. **MINIMAL CHANGES ONLY**
   - Modify only 1-2 sentences maximum
   - Preserve the existing article structure completely
   - Do not add new sections or paragraphs
   - Do not reorganize existing content

2. **ALLOWED OPERATIONS**
   - Replace a single sentence with updated information
   - Add one sentence to an existing paragraph
   - Modify a sentence to include new details
   - Update a specific fact or statistic

3. **INTEGRATION PRINCIPLES**
   - Choose the most relevant new information only
   - Integrate naturally into existing flow
   - Maintain the article's tone and style
   - Ensure new information fits contextually

4. **PRESERVATION REQUIREMENTS**
   - Keep all existing section headers
   - Maintain paragraph structure
   - Preserve the overall narrative flow
   - Do not change the article's main argument or perspective

## OUTPUT REQUIREMENTS

Return the complete article with only the minimal changes needed to integrate the new information. The output should be nearly identical to the input, with only 1-2 sentences modified or added.

**CRITICAL**: If the new information cannot be integrated with minimal changes, return the original article unchanged rather than making extensive modifications.
