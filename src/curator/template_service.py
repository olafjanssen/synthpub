"""
Template service for structured article generation and refinement.

This service integrates template parsing, LLM prompting, and article rendering
to provide a complete structured article generation pipeline.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from langchain.prompts import PromptTemplate

from api.db.prompt_db import get_prompt
from services.llm_service import get_llm
from utils.logging import debug, error, info
from utils.rate_limit_utils import retry_with_backoff

from .article_renderer import ArticleRenderError, process_llm_response
from .template_parser import TemplateStructure, parse_template


class TemplateService:
    """Service for handling structured article generation with templates."""
    
    def __init__(self):
        self._template_cache: Dict[str, TemplateStructure] = {}
    
    def load_template(self, template_id: str) -> TemplateStructure:
        """
        Load and parse a template from the database.
        
        Args:
            template_id: ID of the template to load
            
        Returns:
            Parsed template structure
            
        Raises:
            ValueError: If template not found
        """
        if template_id in self._template_cache:
            return self._template_cache[template_id]
        
        # Get template from database
        prompt_data = get_prompt(template_id)
        if not prompt_data:
            raise ValueError(f"Template '{template_id}' not found in database")
        
        # Parse the template
        template_structure = parse_template(prompt_data.template)
        
        # Cache the parsed template
        self._template_cache[template_id] = template_structure
        
        info("TEMPLATE_SERVICE", "Template loaded", f"ID: {template_id}")
        return template_structure
    
    def generate_article_with_template(
        self,
        template_id: str,
        topic_title: str,
        topic_description: str,
        llm_config: str = "article_generation",
        max_retries: int = 3
    ) -> str:
        """
        Generate an article using a structured template.
        
        Args:
            template_id: ID of the template to use
            topic_title: Article topic title
            topic_description: Article topic description
            llm_config: LLM configuration to use
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated markdown article
            
        Raises:
            ArticleRenderError: If generation fails after retries
        """
        # Load template
        template_structure = self.load_template(template_id)
        
        # Get LLM
        llm = get_llm(llm_config)
        
        # Create prompt
        prompt_text = self._create_generation_prompt(
            template_structure, topic_title, topic_description
        )
        
        # Generate with retries
        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                response = self._call_llm_with_retry(llm, prompt_text)
                
                # Process response and render article
                article = process_llm_response(response, template_structure)
                
                info("TEMPLATE_SERVICE", "Article generated successfully", 
                     f"Template: {template_id}, Attempt: {attempt + 1}")
                return article
                
            except ArticleRenderError as e:
                if attempt < max_retries:
                    # Create retry prompt with error feedback
                    retry_prompt = self._create_retry_prompt(
                        prompt_text, str(e), template_structure
                    )
                    prompt_text = retry_prompt
                    debug("TEMPLATE_SERVICE", "Retrying generation", 
                          f"Attempt: {attempt + 1}, Error: {str(e)}")
                else:
                    error("TEMPLATE_SERVICE", "Article generation failed", 
                          f"Template: {template_id}, Error: {str(e)}")
                    raise
    
    def refine_article_with_template(
        self,
        template_id: str,
        topic_title: str,
        topic_description: str,
        existing_article: str,
        new_context: str,
        new_information: str = "",
        enforcing_information: str = "",
        contradicting_information: str = "",
        llm_config: str = "article_refinement",
        max_retries: int = 3
    ) -> str:
        """
        Refine an existing article using a structured template.
        
        Args:
            template_id: ID of the template to use
            topic_title: Article topic title
            topic_description: Article topic description
            existing_article: Current article content
            new_context: New context from feed
            new_information: New information to integrate
            enforcing_information: Supporting information
            contradicting_information: Contradicting information
            llm_config: LLM configuration to use
            max_retries: Maximum number of retry attempts
            
        Returns:
            Refined markdown article
            
        Raises:
            ArticleRenderError: If refinement fails after retries
        """
        # Load template
        template_structure = self.load_template(template_id)
        
        # Get LLM
        llm = get_llm(llm_config)
        
        # Create refinement prompt
        prompt_text = self._create_refinement_prompt(
            template_structure, topic_title, topic_description,
            existing_article, new_context, new_information,
            enforcing_information, contradicting_information
        )
        
        # Refine with retries
        for attempt in range(max_retries + 1):
            try:
                # Call LLM
                response = self._call_llm_with_retry(llm, prompt_text)
                
                # Process response and render article
                article = process_llm_response(response, template_structure)
                
                info("TEMPLATE_SERVICE", "Article refined successfully", 
                     f"Template: {template_id}, Attempt: {attempt + 1}")
                return article
                
            except ArticleRenderError as e:
                if attempt < max_retries:
                    # Create retry prompt with error feedback
                    retry_prompt = self._create_retry_prompt(
                        prompt_text, str(e), template_structure
                    )
                    prompt_text = retry_prompt
                    debug("TEMPLATE_SERVICE", "Retrying refinement", 
                          f"Attempt: {attempt + 1}, Error: {str(e)}")
                else:
                    error("TEMPLATE_SERVICE", "Article refinement failed", 
                          f"Template: {template_id}, Error: {str(e)}")
                    raise
    
    def _create_generation_prompt(
        self,
        template_structure: TemplateStructure,
        topic_title: str,
        topic_description: str
    ) -> str:
        """Create prompt for article generation."""
        from .template_parser import create_llm_prompt
        return create_llm_prompt(template_structure, topic_title, topic_description)
    
    def _create_refinement_prompt(
        self,
        template_structure: TemplateStructure,
        topic_title: str,
        topic_description: str,
        existing_article: str,
        new_context: str,
        new_information: str,
        enforcing_information: str,
        contradicting_information: str
    ) -> str:
        """Create prompt for article refinement."""
        from .template_parser import create_llm_prompt
        
        context = f"""## Existing Article
{existing_article}

## New Context
{new_context}

## New Information
{new_information}

## Supporting Information
{enforcing_information}

## Contradicting Information
{contradicting_information}

## Instructions
Refine the existing article by integrating the new information while maintaining the template structure. Focus on improving the content within each section rather than changing the overall structure."""
        
        return create_llm_prompt(template_structure, topic_title, topic_description, context)
    
    def _create_retry_prompt(
        self,
        original_prompt: str,
        error_message: str,
        template_structure: TemplateStructure
    ) -> str:
        """Create retry prompt with error feedback."""
        from .article_renderer import create_retry_prompt
        return create_retry_prompt(original_prompt, error_message, template_structure)
    
    @retry_with_backoff(max_retries=3, base_delay=2.0, max_delay=120.0)
    def _call_llm_with_retry(self, llm, prompt_text: str) -> str:
        """Call LLM with retry logic."""
        return llm.invoke(prompt_text).content


# Global instance
template_service = TemplateService()
