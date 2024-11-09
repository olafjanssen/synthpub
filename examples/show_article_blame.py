"""Example script to show article blame information."""
from pathlib import Path
import sys

# Add project root to Python path (consider making this a proper package instead)
project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))  # Insert at beginning of path to ensure it's found first

from curator.utils.article_blame import generate_blame, format_blame_html, get_blame_css
from api.db.article_db import get_article
from api.db.topic_db import load_topics
import webbrowser
import tempfile

def show_article_blame(topic_id: str):
    """Show blame view for all versions of a topic's articles."""
    # Get topic first
    topics = load_topics()
    topic = topics.get(topic_id)
    if not topic:
        print(f"Topic {topic_id} not found")
        return
    
    # Get all article versions for the topic's article
    articles = []
    current_article = get_article(topic.article)
    
    while current_article:
        articles.insert(0, current_article)  # Insert at start to maintain order
        current_article = get_article(current_article.previous_version) if current_article.previous_version else None
    if not articles:
        print(f"No articles found for topic {topic_id}")
        return
        
    # Generate blame information
    blame_entries = generate_blame(articles)
    
    # Create HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Article Blame View</title>
        <style>
            {get_blame_css()}
        </style>
    </head>
    <body>
        <h1>Article History: {articles[-1].title}</h1>
        {format_blame_html(blame_entries, articles)}
    </body>
    </html>
    """
    
    # Save and open in browser
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html_content)
        print(f"Opening blame view in browser: {f.name}")
        webbrowser.open('file://' + f.name)

if __name__ == "__main__":
    # Example usage with error handling
    import argparse
    
    parser = argparse.ArgumentParser(description='Show article blame view')
    parser.add_argument('topic_id', help='ID of the topic to analyze')
    
    args = parser.parse_args()
    
    try:
        show_article_blame(args.topic_id)
    except Exception as e:
        print(f"Error: {str(e)}")
        # Add these lines for better debugging:
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()