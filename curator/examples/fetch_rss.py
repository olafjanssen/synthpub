"""
Example script demonstrating RSS feed fetching.
"""
from curator.feeds.rss_connector import fetch_rss_links
from curator.feeds.web_connector import fetch_webpage
from curator.article_generator import generate_article
from curator.article_refiner import refine_article

def main():
    rss_url = "https://feeds.rijksoverheid.nl/nieuws.rss"
    
    try:
        # Fetch RSS entries
        print("Fetching RSS feed...")
        entries = fetch_rss_links(rss_url)
        
        print(f"\nFound {len(entries)} entries")
        print("======================")
        
        # Process the first entry as an example
        if entries:
            entry = entries[0]
            print(f"\nProcessing: {entry['title']}")
            print(f"URL: {entry['link']}")
            print(f"Published: {entry['published']}")
            
            # Fetch the webpage content
            webpage_data = fetch_webpage(entry['link'])
            
            # Generate initial article
            initial_article = generate_article(entry['title'])
            
            print("\nInitial Generated Article:")
            print("=========================")
            print(initial_article)
            
            # Refine with webpage content
            refined_article = refine_article(
                article=initial_article,
                new_context=webpage_data['content']
            )
            
            print("\nRefined Article:")
            print("===============")
            print(refined_article)
            
    except Exception as e:
        print(f"Error processing RSS feed: {e}")

if __name__ == "__main__":
    main() 