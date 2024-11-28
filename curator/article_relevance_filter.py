"""
Article refiner module for updating existing articles with new context.
"""
from langchain.prompts import PromptTemplate
from .llm_utils import get_llm

def filter_relevance(topic: str, article: str, new_context: str) -> bool:
    """
    Determine if new context is relevant to the existing article.
    
    Args:
        article: Current article text
        new_context: New text to evaluate
        
    Returns:
        bool: True if the new context is relevant
    """
    prompt = PromptTemplate(
        template="""You are evaluating if new content is relevant to the following topic and existing article.

        Topic: {topic}
        
        Existing article:
        {article}

        New content to evaluate:
        {new_context}

        Answer starting with YES or NO: Is the new content relevant to the main topic and themes of the existing article? and then a short explanation.""",
        input_variables=["article", "new_context"]
    )
    
    llm = get_llm('article_refinement')
    response = llm.invoke(prompt.format(
        topic=topic,
        article=article,
        new_context=new_context
    )).content
    print(response)
    return response.strip().upper().startswith('YES')
