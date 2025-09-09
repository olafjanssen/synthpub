# Knowledge Synthesis: Essential Insight Distillation with Template Structure

OBJECTIVE: Create a focused, insightful synthesis of an existing article taking into account new information coming in that emphasizes key principles / recent news and discards peripheral or outdated information, while strictly adhering to the provided template structure.

**CRITICAL: You must follow the template structure exactly. Return ONLY a JSON object with the required keys. Do not add extra sections or modify the template structure. Fill each section with refined content that follows the template's guidance.**

CONTEXT:
Topic: {topic_title}
Description: {topic_description}

## EXISTING ARTICLE

---------------------------------------------------

{article}

---------------------------------------------------

## VERIFIED INFORMATION

NEW INFORMATION:

{new_information}

SUPPORTING INFORMATION:

{enforcing_information}

CONTRADICTING INFORMATION:

{contradicting_information}

## TEMPLATE STRUCTURE

You must generate content for the following sections based on the template:

{template_guidance}

## INTEGRATION PRINCIPLES

1. RUTHLESS PRIORITIZATION
   - Focus exclusively on insights that meaningfully advance understanding
   - Discard peripheral details even if factually accurate
   - Maintain strict adherence to topic scope - remove tangential information
   - **CRITICAL**: When adding new information, remove less essential existing content to stay within length limits

2. SUBSTANCE OVER COMPLETENESS
   - Elevate key principles and core insights above comprehensive coverage
   - Include only the most impactful examples, not exhaustive listings
   - Value clarity and depth on critical points over breadth of coverage
   - **CRITICAL**: Each template section should contain only the most relevant information

3. COGNITIVE ACCESSIBILITY
   - Structure content to emphasize relationships between key concepts
   - Use clear, direct language that prioritizes understanding over jargon
   - Create meaningful transitions that reveal conceptual connections
   - **CRITICAL**: Follow the template's guidance for each section's purpose and tone

4. LENGTH DISCIPLINE
   - Maintain a consistent length of 300-500 words maximum for the entire article
   - When adding new information, **remove less essential existing content**
   - Avoid the temptation to include something merely because it exists
   - **CRITICAL**: Distribute content appropriately across template sections

5. TEMPLATE ADHERENCE
   - Follow the template structure exactly as provided
   - Respect the guidance and instructions for each section
   - Do not add sections not specified in the template
   - Do not modify the template's organizational structure

## DELIVERY REQUIREMENTS

Produce a refined article that:

1. Feels more insightful, not longer
2. Prioritizes key principles over peripheral details
3. Contains only the most relevant information to the topic
4. Reads as a unified perspective with a clear point of view
5. Is engaging and accessible, not dry or academic
6. Does not exceed 500 words under any circumstances
7. **CRITICAL**: Follows the template structure exactly
8. **CRITICAL**: Returns only JSON with the required template section keys

## JSON OUTPUT FORMAT

Return ONLY a JSON object with the following structure:
- "title": [refined article title]
- [section_id_1]: [refined content for first template section]
- [section_id_2]: [refined content for second template section]
- ... [one key for each template section]

Do not include explanations, code fences, or any text outside the JSON object.

Remember: The hallmark of understanding is the ability to separate signal from noise. Your task is to intensify the signal while eliminating the noise, all while respecting the template structure.
