# Incremental Article Refinement: Deprecated Information Cleanup

OBJECTIVE: Remove or update deprecated information from the article with minimal, targeted changes. Make only 1-2 sentence modifications to clean up outdated content while preserving article flow.

CONTEXT:
Topic: {topic_title}
Description: {topic_description}

## EXISTING ARTICLE

{article}

## RECENTLY ADDED INFORMATION

New Information: {new_information}
Supporting Information: {supporting_information}
Contradicting Information: {contradicting_information}

## CLEANUP RULES

1. **MINIMAL CHANGES ONLY**
   - Modify only 1-2 sentences maximum
   - Preserve the existing article structure completely
   - Do not add new sections or paragraphs
   - Do not reorganize existing content

2. **ALLOWED OPERATIONS**
   - Remove one outdated sentence
   - Replace outdated information with current facts
   - Simplify redundant or repetitive content
   - Update references that are no longer relevant

3. **CLEANUP PRINCIPLES**
   - Remove information that contradicts newly added content
   - Eliminate redundant or repetitive statements
   - Update outdated facts or statistics
   - Simplify overly complex explanations

4. **PRESERVATION REQUIREMENTS**
   - Keep all existing section headers
   - Maintain paragraph structure
   - Preserve the overall narrative flow
   - Do not change the article's main argument or perspective

5. **LENGTH DISCIPLINE**
   - Maintain consistent article length (300-500 words)
   - Remove less essential content when adding new information
   - Prioritize clarity and conciseness

## OUTPUT REQUIREMENTS

Return the complete article with only the minimal changes needed to clean up deprecated information. The output should be nearly identical to the input, with only 1-2 sentences modified or removed.

**CRITICAL**: If no cleanup is needed or cannot be done with minimal changes, return the original article unchanged rather than making extensive modifications.
