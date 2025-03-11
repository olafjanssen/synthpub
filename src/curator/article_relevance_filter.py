"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from .llm_utils import get_llm
from utils.logging import debug
from api.db.prompt_db import get_prompt

class RelevanceResponse(BaseModel):
    """Model for the relevance filter response."""
    is_relevant: bool = Field(description="Whether the new content is relevant to the topic or article")
    explanation: str = Field(description="Explanation of why the content is or is not relevant")

def filter_relevance(topic_title: str, topic_description: str, article: str, new_context: str) -> tuple[bool, str]:
    """
    Determine if new context is relevant to the existing article.
    
    Args:
        topic_title: Title of the topic to write about
        topic_description: Description and context for the topic to write about
        article: Current article text
        new_context: New text to evaluate
        
    Returns:
        bool: True if the new context is relevant
        str: Explanation of why the content is or is not relevant
    """
    # Get the prompt template from the database
    prompt_data = get_prompt('article-relevance-filter')
    if not prompt_data:
        raise ValueError("Article relevance filter prompt not found in the database")
    
    # Create a Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=RelevanceResponse)
    
    # Create the prompt template with format instructions as partial variables
    prompt = PromptTemplate(
        template=prompt_data.template + "\n\n{format_instructions}",
        input_variables=["topic_title", "topic_description", "article", "new_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    debug("FILTER", "Prompt Template", prompt.template)
    
    # Format the prompt with our variables
    formatted_prompt = prompt.format(
        topic_title=topic_title,
        topic_description=topic_description,
        article=article,
        new_context=new_context
    )
    
    debug("FILTER", "Formatted Prompt", formatted_prompt)
    
    # Get the LLM and invoke it
    llm = get_llm('article_refinement')
    response_text = llm.invoke(formatted_prompt).content
    
    debug("FILTER", "Raw Response", response_text)
    
    try:
        # Parse the response into the Pydantic model
        parsed_response = parser.parse(response_text)
        debug("FILTER", "Parsed Response", f"is_relevant: {parsed_response.is_relevant}, explanation: {parsed_response.explanation}")
        return (parsed_response.is_relevant, parsed_response.explanation)
    except Exception as e:
        # Fallback to the original parsing method if the structured parsing fails
        debug("FILTER", "Parsing Error", str(e))
        is_relevant = "YES" in response_text.strip().upper()
        return is_relevant, response_text.strip()
