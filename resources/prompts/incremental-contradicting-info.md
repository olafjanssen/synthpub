# Incremental Article Refinement: Contradicting Information Handling

OBJECTIVE: Handle contradicting information in the existing article with minimal, targeted changes. Make only 1-2 sentence modifications to address contradictions while preserving article flow.

CONTEXT:
Topic: {topic_title}
Description: {topic_description}

## EXISTING ARTICLE

{article}

## CONTRADICTING INFORMATION TO HANDLE

{contradicting_information}

## SOURCE CONTEXT

{new_context}

## REFINEMENT RULES

1. **MINIMAL CHANGES ONLY**
   - Modify only 1-2 sentences maximum
   - Preserve the existing article structure completely
   - Do not add new sections or paragraphs
   - Do not reorganize existing content

2. **ALLOWED OPERATIONS**
   - Replace a contradicted sentence with corrected information
   - Add a qualifying statement to address contradictions
   - Modify a sentence to acknowledge alternative viewpoints
   - Update outdated information with current facts

3. **CONTRADICTION HANDLING PRINCIPLES**
   - Address the most significant contradictions only
   - Maintain the article's overall perspective and argument
   - Acknowledge contradictions when appropriate
   - Correct factual errors without changing the core message

4. **PRESERVATION REQUIREMENTS**
   - Keep all existing section headers
   - Maintain paragraph structure
   - Preserve the overall narrative flow
   - Do not change the article's main argument or perspective

## OUTPUT REQUIREMENTS

Return the complete article with only the minimal changes needed to handle contradicting information. The output should be nearly identical to the input, with only 1-2 sentences modified.

**CRITICAL**: If the contradicting information cannot be addressed with minimal changes, return the original article unchanged rather than making extensive modifications.
