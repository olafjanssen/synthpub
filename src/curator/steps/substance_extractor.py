"""
Substance extractor step for the curator workflow.

Extract the substance of an article: new information, enforcing information, and contradicting information.
"""
from langchain.prompts import PromptTemplate
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

from api.models.topic import Topic
from api.models.article import Article
from api.models.feed_item import FeedItem
from services.llm_service import get_llm
from api.db.prompt_db import get_prompt
from utils.logging import info, error, debug
from api.db.topic_db import save_topic

class SubstanceResponse(BaseModel):
    """Model for the substance extractor response."""
    new_information: str = Field(description="New information from the article, leave empty if there is no new information")
    enforcing_information: str = Field(description="Enforcing information from the article, leave empty if there is no enforcing information")
    contradicting_information: str = Field(description="Contradicting information from the article, leave empty if there is no contradicting information")

def process(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract substance from new content compared to existing article.
    
    Args:
        state: Current workflow state with topic, article, and feed content
        
    Returns:
        Updated state with extracted substance
    """
    # Create a new state starting with the current state
    new_state = {**state}
    
    # Extract needed data from state
    topic = state.get("topic")
    article = state.get("existing_article") 
    feed_content = state.get("feed_content")
    feed_item = state.get("feed_item")
        
    try:
        # Extract substance from the new content
        extracted_substance = extract_substance(
            topic=topic,
            current_article=article,
            feed_content=feed_content,
            feed_item=feed_item
        )
        
        # Update state with extracted substance
        new_state["new_information"] = extracted_substance.new_information
        new_state["enforcing_information"] = extracted_substance.enforcing_information
        new_state["contradicting_information"] = extracted_substance.contradicting_information
        
        # Store the extracted substance in the feed item
        feed_item.new_information = extracted_substance.new_information
        feed_item.enforcing_information = extracted_substance.enforcing_information
        feed_item.contradicting_information = extracted_substance.contradicting_information
        
        # Save the updated topic with the modified feed item
        save_topic(topic)
        
        return new_state
        
    except Exception as e:
        error_message = str(e)
        error("CURATOR", "Failed to extract substance", error_message)
        new_state["has_error"] = True
        new_state["error_message"] = f"Failed to extract substance: {error_message}"
        new_state["error_step"] = "substance_extractor"
        return new_state

def extract_substance(
    topic: Topic,
    current_article: Article,
    feed_content: str,
    feed_item: FeedItem
) -> SubstanceResponse:
    """
    Extract substance from new content compared to existing article.
    
    Args:
        topic: The topic the article belongs to
        current_article: The current article to compare against
        feed_content: The new content to analyze
        feed_item: The feed item that provided the content
        
    Returns:
        The extracted substance
        
    Raises:
        Exception: If substance extraction fails
    """
    # Get the LLM
    llm = get_llm('article_refinement')
    
    # Get the prompt template from the database
    prompt_data = get_prompt('substance-extraction')
    if not prompt_data:
        raise ValueError("Substance extraction prompt not found in the database")
    
    # Set up the parser
    parser = PydanticOutputParser(pydantic_object=SubstanceResponse)
    
    # Create and format the prompt with parser instructions
    prompt = PromptTemplate(
        template=prompt_data.template + "\n\n{format_instructions}",
        input_variables=["topic_title", "topic_description", "article", "new_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Invoke the LLM to extract substance
    debug("EXTRACTOR", "Extracting substance", f"Topic: {topic.name}, Source: {feed_item.url}")
    extraction_result = llm.invoke(prompt.format(
        topic_title=topic.name,
        topic_description=topic.description,
        article=current_article.content,
        new_context=feed_content
    ))
    
    # Parse the result into a SubstanceResponse object using the parser
    substance = parser.parse(extraction_result.content)

    info("CURATOR", "Substance extracted", 
         f"Topic: {topic.name}, Source: {feed_item.url}")
    
    return substance