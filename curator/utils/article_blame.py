"""Generate blame information for article versions."""
from typing import List, Tuple, Dict
from diff_match_patch import diff_match_patch
from api.models.article import Article
import re

class BlameEntry:
    """Represents a chunk of text with its origin version."""
    def __init__(self, text: str, version: int, article_id: str):
        self.text = text
        self.version = version
        self.article_id = article_id

def tokenize_to_words(text: str) -> List[str]:
    """Split text into words, preserving markdown formatting."""
    # Preserve markdown headers, lists, and code blocks
    markdown_patterns = [
        r'#{1,6}\s+[^\n]+',  # Headers
        r'`[^`]+`',          # Inline code
        r'```[\s\S]+?```',   # Code blocks
        r'\*\*[^*]+\*\*',    # Bold
        r'\*[^*]+\*',        # Italic
        r'\[[^\]]+\]',       # Link text
        r'\([^)]+\)',        # Link URL
    ]
    
    # Replace markdown patterns with placeholders
    placeholders = {}
    for i, pattern in enumerate(markdown_patterns):
        for match in re.finditer(pattern, text):
            placeholder = f"MARKDOWN_{i}_{len(placeholders)}"
            placeholders[placeholder] = match.group(0)
            text = text.replace(match.group(0), placeholder)
    
    # Split into words
    words = re.findall(r'\S+|\s+', text)
    
    # Restore markdown
    for i, word in enumerate(words):
        if word in placeholders:
            words[i] = placeholders[word]
    
    return words

def generate_blame(articles: List[Article]) -> List[BlameEntry]:
    """
    Generate blame information for a series of article versions.
    
    Args:
        articles: List of articles in chronological order (oldest first)
        
    Returns:
        List of BlameEntry objects showing origin of each text chunk
    """
    if not articles:
        return []
    
    # Sort articles by version
    articles = sorted(articles, key=lambda x: x.version)
    dmp = diff_match_patch()
    
    # Start with the first version
    current_words = tokenize_to_words(articles[0].content)
    blame_map: Dict[int, str] = {i: articles[0].id for i in range(len(current_words))}
    
    # Process each subsequent version
    for prev_article, curr_article in zip(articles, articles[1:]):
        new_words = tokenize_to_words(curr_article.content)
        
        # Compare words
        diffs = dmp.diff_main(' '.join(current_words), ' '.join(new_words))
        dmp.diff_cleanupSemantic(diffs)
        
        # Update blame map
        pos_old = 0
        pos_new = 0
        new_blame_map: Dict[int, str] = {}
        
        for op, text in diffs:
            words = tokenize_to_words(text)
            word_count = len(words)
            
            if op == 0:  # Equal
                for i in range(word_count):
                    if pos_old + i in blame_map:  # Check if index exists
                        new_blame_map[pos_new + i] = blame_map[pos_old + i]
                    else:
                        # If index doesn't exist, use current article as fallback
                        new_blame_map[pos_new + i] = curr_article.id
                pos_old += word_count
                pos_new += word_count
            elif op == -1:  # Deletion
                pos_old += word_count
            else:  # Insertion
                for i in range(word_count):
                    new_blame_map[pos_new + i] = curr_article.id
                pos_new += word_count
        
        current_words = new_words
        blame_map = new_blame_map
    
    # Convert final blame map to BlameEntry objects
    blame_entries: List[BlameEntry] = []
    current_article_id = None
    current_text = []
    
    for i, word in enumerate(current_words):
        if i not in blame_map:
            article_id = articles[-1].id  # Use the latest article as fallback
        else:
            article_id = blame_map[i]
            
        if article_id != current_article_id:
            if current_text:
                article = next(a for a in articles if a.id == current_article_id)
                blame_entries.append(BlameEntry(
                    text=''.join(current_text),
                    version=article.version,
                    article_id=current_article_id
                ))
                current_text = []
            current_article_id = article_id
        current_text.append(word)
    
    # Add final chunk
    if current_text:
        article = next(a for a in articles if a.id == current_article_id)
        blame_entries.append(BlameEntry(
            text=''.join(current_text),
            version=article.version,
            article_id=current_article_id
        ))
    
    return blame_entries

def format_blame_html(blame_entries: List[BlameEntry], articles: List[Article]) -> str:
    """Format blame information as HTML with tooltips."""
    html_parts = []
    for entry in blame_entries:
        article = next(a for a in articles if a.id == entry.article_id)
        date = article.updated_at or article.created_at
        tooltip = f"Version {entry.version} ({date.strftime('%Y-%m-%d %H:%M')})"
        
        html_parts.append(
            f'<span class="blame-chunk" data-version="{entry.version}" '
            f'title="{tooltip}">{entry.text}</span>'
        )
    
    return '\n'.join([
        '<div class="blame-container">',
        ''.join(html_parts),
        '</div>'
    ])

def get_blame_css() -> str:
    """Get CSS styles for blame view."""
    return """
    .blame-container {
        font-family: monospace;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    
    .blame-chunk {
        display: inline;
        padding: 1px 0;
        transition: background-color 0.2s;
    }
    
    .blame-chunk:hover {
        background-color: #f0f0f0;
        border-radius: 3px;
    }
    
    [data-version="1"] { border-bottom: 2px solid #FFB6C1; }
    [data-version="2"] { border-bottom: 2px solid #98FB98; }
    [data-version="3"] { border-bottom: 2px solid #87CEEB; }
    [data-version="4"] { border-bottom: 2px solid #DDA0DD; }
    [data-version="5"] { border-bottom: 2px solid #F0E68C; }
    """ 