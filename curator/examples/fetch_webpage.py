"""
Example script demonstrating web content fetching and article refinement.
"""
from curator.feeds.web_connector import fetch_webpage
from curator.article_generator import generate_article
from curator.article_refiner import refine_article

def main():
    # Fetch content from a webpage
    url = "https://dogfoodstudios.nl/page/students/"
    try:
        webpage_data = fetch_webpage(url)
        
        print("Fetched Content:")
        print("===============")
        print(f"Title: {webpage_data['title']}")
        print(f"URL: {webpage_data['url']}")
        print("\nContent Preview:")
        print(webpage_data['content'][:500] + "...\n")
        
        # Generate initial article based on the title
        topic = f"Summary of: {webpage_data['title']}"
        initial_article = generate_article(topic)
        
        print("\nInitial Generated Article:")
        print("=========================")
        print(initial_article)
        
        # Refine the article using the webpage content
        refined_article = refine_article(
            article=initial_article,
            new_context=webpage_data['content']
        )
        
        print("\nRefined Article:")
        print("===============")
        print(refined_article)
        
    except Exception as e:
        print(f"Error fetching webpage: {e}")

if __name__ == "__main__":
    main() 