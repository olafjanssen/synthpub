"""
Arxiv connector for fetching research papers and their PDF contents.
"""
import arxiv
import requests
import PyPDF2
import io
from typing import List, Dict
from urllib.parse import urlparse, unquote
from .feed_connector import FeedConnector
from utils.logging import info, error
def extract_pdf_text(pdf_url: str) -> str:
    """Download and extract text from PDF."""
    try:
        # Download PDF
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # Create PDF reader object
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages with encoding error handling
        text_parts = []
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                # Clean and encode text to remove surrogate pairs
                cleaned_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                text_parts.append(cleaned_text)
            except Exception as e:
                error("ARXIV", "Page extracting failed", str(e))
                continue
            
        return "\n".join(text_parts)
    except Exception as e:
        error("ARXIV", "PDF extracting failed", str(e))
        return ""

def parse_arxiv_query(url: str) -> str:
    """Extract search query from custom arxiv:// URL."""
    parsed = urlparse(url)
    # Get everything after arxiv:// and decode URL encoding
    return unquote(parsed.netloc + parsed.path)

class ArxivConnector(FeedConnector):
    # Cache arXiv search results
    cache_expiration = 24 * 3600  # 24 hours
    
    @staticmethod
    def can_handle(url: str) -> bool:
        """Check if URL uses arxiv:// scheme."""
        parsed = urlparse(url)
        return parsed.scheme == 'arxiv'
    
    @staticmethod
    def fetch_content(url: str) -> List[Dict[str, str]]:
        """
        Fetch papers from Arxiv based on search query.
        
        Args:
            url: Custom URL in format arxiv://search-query-terms
            
        Returns:
            List of dicts containing paper details and PDF content
        """
        try:
            # Extract search query from URL
            query = parse_arxiv_query(url)
            
            info("ARXIV", "Query", query)

            # Search Arxiv
            search = arxiv.Search(
                query=query,
                max_results=30,  # Limit results to avoid overload
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            info("ARXIV", "Search", search)
            
            results = []
            for paper in search.results():
                info("ARXIV", "Paper", paper)
                # Create a basic result entry with minimal info, mark for further processing
                entry = {
                    'url': paper.pdf_url,  # Use the PDF URL for direct access in the next step
                    'title': paper.title,
                    'content': f"""Title: {paper.title}
Authors: {', '.join(author.name for author in paper.authors)}
Published: {paper.published}
Summary: {paper.summary}""",
                    'needs_further_processing': True  # Mark for further processing to fetch PDF content
                }
                results.append(entry)
            
            return results
            
        except Exception as e:
            error("ARXIV", "Fetching papers failed", str(e))
            return []

ArxivConnector.connect_signals()