"""
Content converter using a prompt from the prompt database.
"""

from langchain.prompts import PromptTemplate

from api.db.prompt_db import get_prompt
from api.models.topic import Topic
from services.llm_service import get_llm
from utils.logging import debug, error, info, warning

from .converter_interface import Converter


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
    def convert_representation(content_type: str, topic: Topic) -> bool:
        try:
            info("PROMPT", "Starting conversion", f"Topic: {topic.name}")
            content = topic.representations[-1].content

            # Get the prompt template to use
            template_text = Prompt._get_prompt_template(content_type)

            debug("PROMPT", "Getting LLM", "Using article_refinement model")
            llm = get_llm("article_refinement")

            prompt = PromptTemplate.from_template(template_text)

            debug("PROMPT", "Invoking LLM", f"Content length: {len(content)}")
            converted_content = llm.invoke(
                prompt.format(content=content)
            ).content.strip()
            debug(
                "PROMPT",
                "LLM response received",
                f"Output length: {len(converted_content)}",
            )

            topic.add_representation(content_type, converted_content)
            info("PROMPT", "Conversion complete", f"Topic: {topic.name}")

            return True

        except Exception as e:
            error(
                "PROMPT", "Conversion failed", f"Topic: {topic.name}, Error: {str(e)}"
            )
            return False
