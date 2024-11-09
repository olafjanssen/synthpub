const API_URL = 'http://localhost:8000';

// Configure marked options
marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Convert line breaks to <br>
    headerIds: true, // Add IDs to headers
    mangle: false, // Don't escape HTML
    sanitize: false // Allow HTML in markdown
});

async function fetchArticle() {
    // Get article ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const articleId = urlParams.get('id');
    
    if (!articleId) {
        showError('No article ID provided');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/articles/${articleId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const article = await response.json();
        displayArticle(article);
    } catch (error) {
        console.error('Error fetching article:', error);
        showError('Failed to load article. Please try again later.');
    }
}

function displayArticle(article) {
    // Set title
    document.title = `SynthPub - ${article.title}`;
    document.getElementById('article-title').textContent = article.title;
    
    // Set metadata
    document.getElementById('article-version').textContent = article.version;
    document.getElementById('article-created').textContent = formatDate(article.created_at);
    document.getElementById('article-updated').textContent = article.updated_at ? formatDate(article.updated_at) : 'Never';
    
    // Render markdown content
    const contentElement = document.getElementById('article-text');
    contentElement.innerHTML = marked.parse(article.content);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

function showError(message) {
    const contentDiv = document.getElementById('article-content');
    contentDiv.innerHTML = `
        <div class="alert alert-danger" role="alert">
            ${message}
        </div>
    `;
}

// Load article when page loads
document.addEventListener('DOMContentLoaded', fetchArticle); 