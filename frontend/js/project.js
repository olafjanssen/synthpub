/** @global {Object} bootstrap */
/** @global {Object} bootstrap.Modal */

const API_URL = '/api';

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    if (projectId) {
        loadTopics(projectId);
    }
    
    // Handle edit button clicks in topic list
    document.getElementById('topics-list').addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-article')) {
            const topicId = event.target.closest('.card').querySelector('.view-article').dataset.topicId;
            editTopic(topicId);
        }
    });

    // Handle remove button click in edit modal
    document.querySelector('.remove-article').addEventListener('click', () => {
        const topicId = document.getElementById('editTopicId').value;
        removeTopic(topicId);
    });
});

async function loadTopics(projectId) {
    var cardIndex = 2;

    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`);
        const project = await response.json();
        
        // Update the project title
        document.getElementById('project-title').innerHTML = `Project<br>${project.title}`;
        
        const topicsList = document.getElementById('topics-list');
        topicsList.innerHTML = '';
        
        const template = document.getElementById('topic-template');
        const emptyTemplate = document.getElementById('empty-topic-template');
        
        for (const topicId of project.topic_ids) {
            const topicResponse = await fetch(`${API_URL}/topics/${topicId}`);
            const topic = await topicResponse.json();
            
            const topicElement = template.content.cloneNode(true);
            
            // Fill in the template
            topicElement.querySelector('.topic-name').textContent = topic.name;
            topicElement.querySelector('.description').textContent = topic.description;
            
            // Check if article is still being generated
            if (!topic.article) {
                // Disable the update button while generating
                topicElement.querySelector('.update-article').disabled = true;
                topicElement.querySelector('.update-article').title = 'Article is still being generated';
                
                // Disable the publish button while generating
                topicElement.querySelector('.publish-article').disabled = true;
                topicElement.querySelector('.publish-article').title = 'Article is still being generated';
            }
            
            // Use Pexels thumbnail if available, otherwise use default image
            const topicImg = topicElement.querySelector('.topic-img');
            if (topic.thumbnail_url) {
                topicImg.src = topic.thumbnail_url;
            } else {
                topicImg.src = `/img/bg/bg-${(cardIndex++ % 5) + 1}.png`;
            }

            // Set up view article button
            const viewButton = topicElement.querySelector('.view-article');
            viewButton.dataset.topicId = topic.id;
            viewButton.addEventListener('click', () => {
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get("project_id");
                if (topic.article) {
                    window.location.href = `article.html?id=${topic.article}&project_id=${projectId}`;
                } else {
                    // If the article isn't generated yet, show a message to the user
                    alert('Article is being generated. Please try again in a moment.');
                }
            });
                        
            // Add data attributes and event listeners for other buttons
            const updateButton = topicElement.querySelector('.update-article');
            const editButton = topicElement.querySelector('.edit-article');
            const publishButton = topicElement.querySelector('.publish-article');
            
            updateButton.dataset.topicId = topic.id;
            editButton.dataset.topicId = topic.id;
            publishButton.dataset.topicId = topic.id;
            
            updateButton.addEventListener('click', () => updateArticle(topic.id));
            editButton.addEventListener('click', () => editTopic(topic.id));
            publishButton.addEventListener('click', () => publishArticle(topic.id));
            
            // Only enable publish button if there are publish URLs
            if (!topic.publish_urls || topic.publish_urls.length === 0) {
                publishButton.disabled = true;
                publishButton.title = 'No publish URLs configured';
            }
            
            topicsList.appendChild(topicElement);
        }

        // Add empty cards until we have at least 30 total
        const totalCards = project.topic_ids.length;
        const emptyCardsNeeded = Math.max(0, 30 - totalCards);
        
        for (let i = 0; i < emptyCardsNeeded; i++) {
            topicsList.appendChild(emptyTemplate.content.cloneNode(true));
        }

                
    } catch (error) {
        console.error('Error loading topics:', error);
        showError('Failed to load topics. Please try again later.');
    }
}

function addFeedInput() {
    const container = document.getElementById('feedUrlsContainer');
    const newInput = document.createElement('div');
    newInput.className = 'input-group mb-2';
    newInput.innerHTML = `
        <input type="url" class="form-control feed-url" placeholder="https://example.com/feed">
        <button type="button" class="btn btn-outline-danger remove-feed" onclick="removeFeedInput(this)">×</button>
    `;
    container.appendChild(newInput);
}

function removeFeedInput(button) {
    button.closest('.input-group').remove();
}

async function createTopic() {
    // Get the project ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    
    if (!projectId) {
        showError('Project ID not found in URL');
        return;
    }

    const name = document.getElementById('topicName').value;
    const description = document.getElementById('topicDescription').value;
    const thumbnailUrl = document.getElementById('thumbnailUrl').value.trim();
    const feedUrls = Array.from(document.querySelectorAll('.feed-url'))
        .map(input => input.value)
        .filter(url => url.trim() !== '');
    const publishUrls = Array.from(document.querySelectorAll('.publish-url'))
        .map(input => input.value)
        .filter(url => url.trim() !== '');

    try {
        const response = await fetch(`${API_URL}/topics/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name, 
                description, 
                feed_urls: feedUrls, 
                publish_urls: publishUrls,
                thumbnail_url: thumbnailUrl // Send empty string if field is empty
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const topic = await response.json();
        
        // Add topic to project
        const projectResponse = await fetch(`${API_URL}/projects/${projectId}/topics/${topic.id}`, {
            method: 'POST'
        });

        if (!projectResponse.ok) {
            throw new Error(`Failed to add topic to project: ${projectResponse.status}`);
        }
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('createTopicModal'));
        modal.hide();
        document.getElementById('createTopicForm').reset();
        document.getElementById('feedUrlsContainer').innerHTML = `
            <div class="input-group mb-2">
                <input type="url" class="form-control feed-url" placeholder="https://example.com/feed">
                <button type="button" class="btn btn-outline-danger remove-feed" onclick="removeFeedInput(this)">×</button>
            </div>
        `;
        
        // Refresh topics list
        await loadTopics(projectId);
        
    } catch (error) {
        console.error('Error creating topic:', error);
        showError('Failed to create topic. Please try again later.');
    }
}

async function updateArticle(topicId) {
    try {
        const button = document.querySelector(`[data-topic-id="${topicId}"]`);
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = 'Updating...';
        
        const response = await fetch(`${API_URL}/topics/${topicId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get("project_id");
        await loadTopics(projectId);
        
    } catch (error) {
        console.error('Error updating article:', error);
        showError('Failed to update article. Please try again later.');
    }
}

function editTopic(topicId) {
    fetch(`${API_URL}/topics/${topicId}`)
        .then(response => response.json())
        .then(topic => {
            // Populate the edit form
            document.getElementById('editTopicId').value = topicId;
            document.getElementById('editTopicName').value = topic.name;
            document.getElementById('editTopicDescription').value = topic.description;
            document.getElementById('editThumbnailUrl').value = topic.thumbnail_url || '';

            // Clear existing feed URLs
            const editFeedUrlsContainer = document.getElementById('editFeedUrlsContainer');
            editFeedUrlsContainer.innerHTML = '';
            topic.feed_urls.forEach(url => {
                const inputGroup = document.createElement('div');
                inputGroup.className = 'input-group mb-2';
                inputGroup.innerHTML = `
                    <input type="url" class="form-control feed-url" value="${url}">
                    <button type="button" class="btn btn-outline-danger remove-feed" onclick="removeFeedInput(this)">×</button>
                `;
                editFeedUrlsContainer.appendChild(inputGroup);
            });

            // Add "Add Feed URL" button
            const addFeedButton = document.createElement('button');
            addFeedButton.type = 'button';
            addFeedButton.className = 'btn btn-outline-secondary btn-sm';
            addFeedButton.onclick = () => addEditFeedInput();
            addFeedButton.textContent = 'Add Feed URL';
            editFeedUrlsContainer.appendChild(addFeedButton);

            // Clear existing publish URLs
            const editPublishUrlsContainer = document.getElementById('editPublishUrlsContainer');
            editPublishUrlsContainer.innerHTML = '';
            (topic.publish_urls || []).forEach(url => {
                const inputGroup = document.createElement('div');
                inputGroup.className = 'input-group mb-2';
                inputGroup.innerHTML = `
                    <input type="url" class="form-control edit-publish-url" value="${url}">
                    <button type="button" class="btn btn-outline-danger remove-publish" onclick="removePublishInput(this)">×</button>
                `;
                editPublishUrlsContainer.appendChild(inputGroup);
            });

            // Add "Add Publish URL" button
            const addPublishButton = document.createElement('button');
            addPublishButton.type = 'button';
            addPublishButton.className = 'btn btn-outline-secondary btn-sm';
            addPublishButton.onclick = () => addEditPublishInput();
            addPublishButton.textContent = 'Add Publish URL';
            editPublishUrlsContainer.appendChild(addPublishButton);
        })
        .catch(error => {
            console.error('Error fetching topic:', error);
            showError('Failed to load topic details. Please try again later.');
        });
}

function addEditFeedInput() {
    const container = document.getElementById('editFeedUrlsContainer');
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group mb-2';
    inputGroup.innerHTML = `
        <input type="url" class="form-control feed-url" placeholder="https://example.com/feed">
        <button type="button" class="btn btn-outline-danger remove-feed" onclick="removeFeedInput(this)">×</button>
    `;
    container.insertBefore(inputGroup, container.lastChild);
}

function addEditPublishInput() {
    const container = document.getElementById('editPublishUrlsContainer');
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group mb-2';
    inputGroup.innerHTML = `
        <input type="url" class="form-control edit-publish-url" placeholder="https://example.com/publish">
        <button type="button" class="btn btn-outline-danger remove-publish" onclick="removePublishInput(this)">×</button>
    `;
    container.insertBefore(inputGroup, container.lastChild);
}

async function updateTopic() {
    const topicId = document.getElementById('editTopicId').value;
    const name = document.getElementById('editTopicName').value;
    const description = document.getElementById('editTopicDescription').value;
    const thumbnailUrl = document.getElementById('editThumbnailUrl').value.trim();
    const feedInputs = document.querySelectorAll('#editFeedUrlsContainer .feed-url');
    const publishInputs = document.querySelectorAll('#editPublishUrlsContainer .edit-publish-url');
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");

    const feed_urls = Array.from(feedInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');

    const publish_urls = Array.from(publishInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');

    try {
        const response = await fetch(`${API_URL}/topics/${topicId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name, 
                description, 
                feed_urls, 
                publish_urls,
                thumbnail_url: thumbnailUrl // Send empty string if field is empty
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close modal and refresh topics list
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTopicModal'));
        modal.hide();
        await loadTopics(projectId);
    } catch (error) {
        console.error('Error updating topic:', error);
        showError('Failed to update topic. Please try again later.');
    }
}

async function removeTopic(topicId) {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    
    try {
        const response = await fetch(`${API_URL}/topics/${topicId}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close modal and refresh topics list
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTopicModal'));
        modal.hide();
        await loadTopics(projectId);
    } catch (error) {
        console.error('Error removing topic:', error);
        showError('Failed to remove topic. Please try again later.');
    }
}

function showError(message) {
    alert(message);
}

function addPublishInput() {
    const container = document.getElementById('publishUrlsContainer');
    const div = document.createElement('div');
    div.className = 'input-group mb-2';
    div.innerHTML = `
        <input type="url" class="form-control publish-url" placeholder="https://example.com/publish">
        <button type="button" class="btn btn-outline-danger remove-publish" onclick="removePublishInput(this)">×</button>
    `;
    container.appendChild(div);
}

function removePublishInput(button) {
    button.closest('.input-group').remove();
}

async function publishArticle(topicId) {
    try {
        const button = document.querySelector(`[data-topic-id="${topicId}"].publish-article`);
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-cloud-upload"></i>';
        
        const response = await fetch(`${API_URL}/topics/${topicId}/publish`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Reset button after short delay
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = originalText;
        }, 2000);
        
    } catch (error) {
        console.error('Error publishing article:', error);
        showError('Failed to publish article. Please try again later.');
        const button = document.querySelector(`[data-topic-id="${topicId}"].publish-article`);
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-cloud-upload"></i>';
    }
} 