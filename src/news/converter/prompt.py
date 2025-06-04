"""
Content converter using a prompt from the prompt database.
"""

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from api.db.prompt_db import get_prompt
from api.models.article import Article
from services.llm_service import get_llm
from utils.logging import debug, error, info, warning

from .converter_interface import Converter

class ConverterOutput(BaseModel):
    """Structured output from the LLM conversion process."""
    output: str = Field(
        description="The converted content following the instructions of the prompt.",
        min_length=1,
        max_length=10000  # Reasonable limit to prevent endless outputs
    )

class Prompt(Converter):

    @staticmethod
    def can_handle(content_type: str) -> bool:
        # Check if type starts with 'prompt/' followed by a prompt ID
        return content_type.startswith("prompt")

    @staticmethod
    def _get_prompt_template(content_type: str) -> str:
        """Extract and retrieve the prompt template to use for conversion."""
        # Parse type to extract prompt_id
        # Format is either 'prompt' (using default) or 'prompt/prompt_id'
        prompt_id = None
        if "/" in content_type:
            _, prompt_id = content_type.split("/", 1)

        # Get prompt from database or use default
        template_text = None
        if prompt_id:
            prompt_obj = get_prompt(prompt_id)
            if prompt_obj:
                info(
                    "PROMPT",
                    "Using prompt from database",
                    f"Prompt: {prompt_obj.name}",
                )
                template_text = prompt_obj.template
            else:
                warning(
                    "PROMPT",
                    "Prompt not found",
                    f"Prompt ID: {prompt_id}, using default",
                )

        # Use default prompt if no prompt_id or prompt not found
        if not template_text:
            info(
                "PROMPT",
                "Using default prompt",
                "No prompt ID specified or prompt not found",
            )
            template_text = """
Write a well-crafted response about the following content:

{content}

Use a clear, concise style appropriate for the content.
"""
        return template_text

    @staticmethod
    def convert_representation(content_type: str, article: Article) -> bool:
        try:
            info("PROMPT", "Starting conversion", f"Article: {article.title}")

            # Use the most recent representation's content, or fall back to article content
            if article.representations:
                content = article.representations[-1].content
                info(
                    "PROMPT",
                    "Using previous representation",
                    f"Type: {article.representations[-1].type}",
                )
            else:
                content = article.content
                info(
                    "PROMPT",
                    "No previous representations",
                    "Using original article content",
                )

            # Get the prompt template to use
            template_text = Prompt._get_prompt_template(content_type)

            debug("PROMPT", "Getting LLM", "Using article_refinement model")
            llm = get_llm("article_refinement")

            # Set up the output parser
            parser = PydanticOutputParser(pydantic_object=ConverterOutput)
            
            # Create the prompt with output format instructions
            prompt = PromptTemplate.from_template(
                template_text + "\n\n{format_instructions}",
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )

            debug("PROMPT", "Invoking LLM", f"Content length: {len(content)}")
            raw_output = llm.invoke(
                prompt.format(content=content)
            ).content.strip()
            
            # Parse the output using Pydantic
            try:
                parsed_output = parser.parse(raw_output)
                converted_content = parsed_output.output
                debug(
                    "PROMPT",
                    "LLM response parsed successfully",
                    f"Output length: {len(converted_content)}",
                )
            except Exception as parse_error:
                error(
                    "PROMPT",
                    "Failed to parse LLM output",
                    f"Error: {str(parse_error)}, using raw output",
                )
                converted_content = raw_output

            article.add_representation(
                content_type, converted_content, {"extension": "txt"}
            )
            info("PROMPT", "Conversion complete", f"Article: {article.title}")

            return True

        except Exception as e:
            error(
                "PROMPT",
                "Conversion failed",
                f"Article: {article.title}, Error: {str(e)}",
            )
            return False
