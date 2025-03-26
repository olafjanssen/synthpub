/*global marked, DOMPurify */

const API_URL = '/api';

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
    
    // Display representations
    displayRepresentations(article.representations);
    
    // Render markdown content
    const contentElement = document.getElementById('article-text');
    const htmlContent = marked.parse(article.content);
    // Sanitize the HTML content before rendering
    contentElement.innerHTML = DOMPurify.sanitize(htmlContent, {
        USE_PROFILES: { html: true },
        FORBID_TAGS: ['script', 'style', 'iframe', 'frame', 'object', 'embed'],
        FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
    });
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

async function init() {
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

    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`);
        const project = await response.json();
        
        // Update the project title
        const projectTitle = document.getElementById('project-title');
        projectTitle.textContent = '';
        
        const projectText = document.createTextNode('Project');
        projectTitle.appendChild(projectText);
        
        const lineBreak = document.createElement('br');
        projectTitle.appendChild(lineBreak);
        
        const titleText = document.createTextNode(project.title);
        projectTitle.appendChild(titleText);
    } catch (error) {
        console.error('Error fetching project:', error);
    }
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
    contentDiv.textContent = '';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.setAttribute('role', 'alert');
    alertDiv.textContent = message;
    
    contentDiv.appendChild(alertDiv);
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
    
    // Clear the existing list
    sourcesList.textContent = '';
    
    // Create and append list items for each source
    relevantSources.forEach(source => {
        const li = document.createElement('li');
        
        const a = document.createElement('a');
        a.href = source.url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = source.title || source.url;
        
        li.appendChild(a);
        
        if (source.accessed_at) {
            const span = document.createElement('span');
            span.className = 'text-muted';
            span.textContent = ` (accessed ${new Date(source.accessed_at).toLocaleDateString()})`;
            li.appendChild(span);
        }
        
        sourcesList.appendChild(li);
    });
}

function displayRepresentations(representations) {
    const representationsSection = document.getElementById('article-representations');
    const accordionContainer = document.getElementById('representationsAccordion');
    
    // Hide the section if there are no representations
    if (!representations || representations.length === 0) {
        representationsSection.style.display = 'none';
        return;
    }
    
    // Show the section
    representationsSection.style.display = 'block';
    
    // Clear the existing content
    accordionContainer.innerHTML = '';
    
    // Create accordion items for each representation
    representations.forEach((rep, index) => {
        const accordionItem = document.createElement('div');
        accordionItem.className = 'accordion-item';
        
        // Create unique IDs for this representation
        const headingId = `heading${index}`;
        const collapseId = `collapse${index}`;
        
        // Determine file extension from metadata or type
        const extension = rep.metadata?.extension || getExtensionFromType(rep.type);
        
        // Create the accordion header
        const header = document.createElement('h2');
        header.className = 'accordion-header';
        header.id = headingId;
        
        const button = document.createElement('button');
        button.className = 'accordion-button collapsed';
        button.type = 'button';
        button.setAttribute('data-bs-toggle', 'collapse');
        button.setAttribute('data-bs-target', `#${collapseId}`);
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', collapseId);
        
        // Format the type for display
        const displayType = formatRepresentationType(rep.type);
        const createdAt = formatDate(rep.created_at);
        button.innerHTML = `<strong>${displayType}</strong> <small class="ms-2 text-muted">(${createdAt})</small>`;
        
        header.appendChild(button);
        accordionItem.appendChild(header);
        
        // Create the collapsible body
        const collapseDiv = document.createElement('div');
        collapseDiv.id = collapseId;
        collapseDiv.className = 'accordion-collapse collapse';
        collapseDiv.setAttribute('aria-labelledby', headingId);
        collapseDiv.setAttribute('data-bs-parent', '#representationsAccordion');
        
        const bodyDiv = document.createElement('div');
        bodyDiv.className = 'accordion-body';
        
        // Handle different representation types
        if (rep.type.includes('audio') || extension === 'mp3') {
            // Audio representation
            const audio = document.createElement('audio');
            audio.className = 'audio-player';
            audio.controls = true;
            
            // Convert hex string to bytes
            const bytes = new Uint8Array(rep.content.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
            const blob = new Blob([bytes], {type: 'audio/mpeg'});
            const blobUrl = URL.createObjectURL(blob);
            audio.src = blobUrl;
            
            bodyDiv.appendChild(audio);
        } else if (rep.type.includes('html')) {
            // HTML representation - sanitize before rendering
            bodyDiv.innerHTML = DOMPurify.sanitize(rep.content, {
                USE_PROFILES: { html: true },
                FORBID_TAGS: ['script', 'style', 'iframe', 'frame', 'object', 'embed'],
                FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
            });
        } else if (rep.type.includes('markdown') || extension === 'md') {
            // Markdown representation
            bodyDiv.innerHTML = DOMPurify.sanitize(marked.parse(rep.content), {
                USE_PROFILES: { html: true },
                FORBID_TAGS: ['script', 'style', 'iframe', 'frame', 'object', 'embed'],
                FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
            });
        } else {
            // Plain text or other representation types
            const pre = document.createElement('pre');
            pre.style.whiteSpace = 'pre-wrap';
            pre.style.wordWrap = 'break-word';
            pre.textContent = rep.content;
            bodyDiv.appendChild(pre);
        }
        
        collapseDiv.appendChild(bodyDiv);
        accordionItem.appendChild(collapseDiv);
        
        // Add to the accordion container
        accordionContainer.appendChild(accordionItem);
    });
}

function formatRepresentationType(type) {
    // Capitalize and clean up the representation type for display
    return type
        .split('/')
        .pop()
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function getExtensionFromType(type) {
    // Map mime types to file extensions
    const typeToExt = {
        'text/html': 'html',
        'text/markdown': 'md',
        'text/plain': 'txt',
        'audio/mpeg': 'mp3',
        'audio/mp3': 'mp3',
        'application/xml': 'xml',
        'text/xml': 'xml'
    };
    
    // Check if the type is in our mapping
    for (const [mimeType, ext] of Object.entries(typeToExt)) {
        if (type.includes(mimeType)) {
            return ext;
        }
    }
    
    // Return a default based on the type
    if (type.includes('audio')) return 'mp3';
    if (type.includes('html')) return 'html';
    if (type.includes('markdown')) return 'md';
    if (type.includes('xml')) return 'xml';
    
    return 'txt';
}

// Load article when page loads
document.addEventListener('DOMContentLoaded', init); 