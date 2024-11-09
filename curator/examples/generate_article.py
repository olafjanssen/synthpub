"""
Example script demonstrating article generation and refinement.
"""
from curator.article_generator import generate_article
from curator.article_refiner import refine_article

def main():
    # Generate initial article
    topic = "The impact of artificial intelligence on modern journalism"
    article = generate_article(topic)
    print("Original Article:\n", article)
    
    # Refine with new context
    new_context = """
    Recent studies show that 73% of news organizations are now using AI 
    for content analysis and 45% for automated news writing. However, 
    concerns about AI hallucinations have led to stricter human oversight.
    """
    refined_article = refine_article(article, new_context)
    print("\nRefined Article:\n", refined_article)

if __name__ == "__main__":
    main()