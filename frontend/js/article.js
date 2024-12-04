const API_URL = 'http://localhost:8000';

// Configure marked options
marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Convert line breaks to <br>
    headerIds: true, // Add IDs to headers
    mangle: false, // Don't escape HTML
    sanitize: false // Allow HTML in markdown
});

async function fetchArticle(articleId) {
    try {
        const response = await fetch(`${API_URL}/articles/${articleId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const article = await response.json();
        
        // Display article first
        displayArticle(article);
        setupVersionNavigation(article);
        
        // Then fetch and display sources
        await fetchAndDisplaySources(article.topic_id);
    } catch (error) {
        console.error('Error fetching article:', error);
        showError('Failed to load article. Please try again later.');
    }
}

async function fetchAndDisplaySources(topic_id) {
    try {
        // Get all topics
        const response = await fetch(`${API_URL}/topics/${topic_id}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const topic = await response.json();
        if (topic) {
            displaySources(topic.processed_feeds);
        }
    } catch (error) {
        console.error('Error fetching sources:', error);
    }
}

function displayArticle(article) {
    // Set title
    document.title = `SynthPub - ${article.title}`;
    document.getElementById('article-title').textContent = article.title;
    
    // Set metadata
    document.getElementById('article-version').textContent = article.version;
    document.getElementById('current-version').textContent = article.version;
    document.getElementById('article-created').textContent = formatDate(article.created_at);
    document.getElementById('article-updated').textContent = article.updated_at ? formatDate(article.updated_at) : 'Never';
    
    // Display feed source info if available
    const sourceFeedInfo = document.getElementById('source-feed-info');
    if (article.source_feed) {
        const feedUrl = document.getElementById('feed-url');
        feedUrl.href = article.source_feed.url;
        feedUrl.textContent = article.source_feed.url;
        
        document.getElementById('feed-accessed').textContent = 
            formatDate(article.source_feed.accessed_at);
            
        sourceFeedInfo.style.display = 'block';
    } else {
        sourceFeedInfo.style.display = 'none';
    }
    
    // Render markdown content
    const contentElement = document.getElementById('article-text');
    contentElement.innerHTML = marked.parse(article.content);
}

function setupVersionNavigation(article) {
    const prevButton = document.getElementById('prev-version');
    const nextButton = document.getElementById('next-version');
    
    // Enable/disable previous version button
    if (article.previous_version) {
        prevButton.disabled = false;
        prevButton.onclick = () => navigateToVersion(article.previous_version);
    } else {
        prevButton.disabled = true;
    }
    
    // Enable/disable next version button
    if (article.next_version) {
        nextButton.disabled = false;
        nextButton.onclick = () => navigateToVersion(article.next_version);
    } else {
        nextButton.disabled = true;
    }
}

function navigateToVersion(articleId) {
    // Update URL without reloading page
    const url = new URL(window.location);
    url.searchParams.set('id', articleId);
    window.history.pushState({}, '', url);
    
    // Fetch and display the article
    fetchArticle(articleId);
}

function init() {
    // Get both article ID and project ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const articleId = urlParams.get('id');
    const projectId = urlParams.get('project_id');

    // Set up back button navigation
    const backButton = document.getElementById('back-button');
    backButton.href = projectId ? `project.html?project_id=${projectId}` : 'index.html';

    if (!articleId) {
        showError('No article ID provided');
        return;
    }
    
    fetchArticle(articleId);
}

// Handle browser back/forward buttons
window.onpopstate = () => {
    init();
};

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

function displaySources(sources) {
    const sourcesList = document.getElementById('article-sources');
    if (!sources || sources.length === 0) {
        sourcesList.parentElement.style.display = 'none';
        return;
    }

    const relevantSources = sources.filter(source => source.is_relevant);
    
    if (relevantSources.length === 0) {
        sourcesList.parentElement.style.display = 'none';
        return;
    }
    
    sourcesList.innerHTML = relevantSources.map(source => `
        <li>
            <a href="${source.url}" target="_blank" rel="noopener noreferrer">
                ${source.title || source.url}
            </a>
            ${source.accessed_at ? `<span class="text-muted"> (accessed ${new Date(source.accessed_at).toLocaleDateString()})</span>` : ''}
        </li>
    `).join('');
}

// Load article when page loads
document.addEventListener('DOMContentLoaded', init); 