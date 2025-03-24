// Configure marked.js options
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: true,
    langPrefix: 'language-'
});

// Function to render markdown content
function renderContent() {
    try {
        const contentElement = document.getElementById('content');
        const noscriptContent = contentElement.querySelector('noscript');
        
        if (!noscriptContent) {
            throw new Error('Content not found');
        }
        
        // Get the markdown content from the noscript tag
        const markdown = noscriptContent.textContent.trim();
        
        // Replace the content with the rendered markdown
        contentElement.innerHTML = marked.parse(markdown);

        // Add target="_blank" to external links
        document.querySelectorAll('a[href^="http"]').forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        });
    } catch (error) {
        console.error('Error rendering content:', error);
        document.getElementById('content').innerHTML = '<p>Error rendering content. Please try again later.</p>';
    }
}

// Render content when the page loads
document.addEventListener('DOMContentLoaded', renderContent); 