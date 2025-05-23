/*global bootstrap */

const API_URL = '/api';

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    if (projectId) {
        loadTopics(projectId);
    }
    
    // Connect create topic button
    const createTopicBtn = document.getElementById('createTopicBtn');
    if (createTopicBtn) {
        createTopicBtn.addEventListener('click', function() {
            const form = document.getElementById('createTopicForm');
            if (form.checkValidity()) {
                createTopic();
            } else {
                form.reportValidity();
            }
        });
    }

    // Connect update topic button
    const updateTopicBtn = document.getElementById('updateTopicBtn');
    if (updateTopicBtn) {
        updateTopicBtn.addEventListener('click', function() {
            const form = document.getElementById('editTopicForm');
            if (form.checkValidity()) {
                updateTopic();
            } else {
                form.reportValidity();
            }
        });
    }

    // Connect feed URL buttons
    const addFeedBtn = document.getElementById('addFeedBtn');
    if (addFeedBtn) {
        addFeedBtn.addEventListener('click', addFeedInput);
    }

    // Connect publish URL buttons
    const addPublishBtn = document.getElementById('addPublishBtn');
    if (addPublishBtn) {
        addPublishBtn.addEventListener('click', addPublishInput);
    }

    // Connect remove feed buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-feed')) {
            removeFeedInput(event.target);
        }
    });

    // Connect remove publish buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-publish')) {
            removePublishInput(event.target);
        }
    });

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

// Split loadTopics into smaller functions to reduce complexity
async function loadTopics(projectId) {
    try {
        const project = await fetchProject(projectId);
        updateProjectTitle(project.title);
        await renderTopicsList(project.topic_ids);
    } catch (error) {
        console.error('Error loading topics:', error);
        showError('Failed to load topics. Please try again later.');
    }
}

async function fetchProject(projectId) {
    const response = await fetch(`${API_URL}/projects/${projectId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function updateProjectTitle(title) {
    const projectTitle = document.getElementById('project-title');
    projectTitle.textContent = '';
    projectTitle.appendChild(document.createTextNode('Project'));
    projectTitle.appendChild(document.createElement('br'));
    projectTitle.appendChild(document.createTextNode(title));
}

async function renderTopicsList(topicIds) {
    const topicsList = document.getElementById('topics-list');
    const template = document.getElementById('topic-template');
    const emptyTemplate = document.getElementById('empty-topic-template');
    
    topicsList.textContent = '';
    let cardIndex = 2;

    for (const topicId of topicIds) {
        const topic = await fetchTopic(topicId);
        const topicElement = createTopicElement(topic, template, cardIndex++);
        topicsList.appendChild(topicElement);
    }

    // Add empty cards
    const emptyCardsNeeded = Math.max(0, 30 - topicIds.length);
    for (let i = 0; i < emptyCardsNeeded; i++) {
        topicsList.appendChild(emptyTemplate.content.cloneNode(true));
    }
}

async function fetchTopic(topicId) {
    const response = await fetch(`${API_URL}/topics/${topicId}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function createTopicElement(topic, template, cardIndex) {
    const topicElement = template.content.cloneNode(true);
    
    // Fill in the template
    topicElement.querySelector('.topic-name').textContent = topic.name;
    topicElement.querySelector('.description').textContent = topic.description;
    
    // Set up image
    const topicImg = topicElement.querySelector('.topic-img');
    topicImg.src = topic.thumbnail_url || `/img/bg/bg-${(cardIndex % 5) + 1}.png`;
    
    // Set up buttons
    setupTopicButtons(topicElement, topic);
    
    return topicElement;
}

function setupTopicButtons(topicElement, topic) {
    const viewButton = topicElement.querySelector('.view-article');
    const updateButton = topicElement.querySelector('.update-article');
    const editButton = topicElement.querySelector('.edit-article');
    const publishButton = topicElement.querySelector('.publish-article');
    
    // Set data attributes
    [viewButton, updateButton, editButton, publishButton].forEach(btn => {
        btn.dataset.topicId = topic.id;
    });
    
    // Set up view button
    viewButton.addEventListener('click', () => {
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get("project_id");
        if (topic.article) {
            const safeUrl = `article.html?id=${encodeURIComponent(topic.article)}&project_id=${encodeURIComponent(projectId)}`;
            window.location.href = safeUrl;
        } else {
            alert('Article is being generated. Please try again in a moment.');
        }
    });
    
    // Set up other buttons
    updateButton.addEventListener('click', () => updateArticle(topic.id));
    editButton.addEventListener('click', () => editTopic(topic.id));
    publishButton.addEventListener('click', () => publishArticle(topic.id));
    
    // Disable buttons if needed
    if (!topic.article) {
        updateButton.disabled = true;
        updateButton.title = 'Article is still being generated';
        publishButton.disabled = true;
        publishButton.title = 'Article is still being generated';
    }
    
    if (!topic.publish_urls || topic.publish_urls.length === 0) {
        publishButton.disabled = true;
        publishButton.title = 'No publish URLs configured';
    }
}

function addFeedInput() {
    const container = document.getElementById('feedUrlsContainer');
    const newInput = document.createElement('div');
    newInput.className = 'input-group mb-2';
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'url';
    input.className = 'form-control feed-url';
    input.placeholder = 'https://example.com/feed';
    
    // Create button element
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-danger remove-feed';
    button.textContent = '×';
    button.onclick = function() { removeFeedInput(this); };
    
    // Append elements to the container
    newInput.appendChild(input);
    newInput.appendChild(button);
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
        const response = await fetch(`${API_URL}/projects/${projectId}/topics`, {
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
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('createTopicModal'));
        modal.hide();
        document.getElementById('createTopicForm').reset();
        
        // Clear and reset feed URL container
        const feedUrlsContainer = document.getElementById('feedUrlsContainer');
        feedUrlsContainer.textContent = '';
        
        // Add a default feed URL input group
        const inputGroup = document.createElement('div');
        inputGroup.className = 'input-group mb-2';
        
        const input = document.createElement('input');
        input.type = 'url';
        input.className = 'form-control feed-url';
        input.placeholder = 'https://example.com/feed';
        
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-outline-danger remove-feed';
        button.textContent = '×';
        button.onclick = function() { removeFeedInput(this); };
        
        inputGroup.appendChild(input);
        inputGroup.appendChild(button);
        feedUrlsContainer.appendChild(inputGroup);
        
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
            editFeedUrlsContainer.textContent = '';
            topic.feed_urls.forEach(url => {
                const inputGroup = document.createElement('div');
                inputGroup.className = 'input-group mb-2';
                
                // Create input element for the feed URL
                const input = document.createElement('input');
                input.type = 'url';
                input.className = 'form-control feed-url';
                input.value = url;
                
                // Create remove button
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-danger remove-feed';
                button.textContent = '×';
                button.onclick = function() { removeFeedInput(this); };
                
                // Append elements to input group
                inputGroup.appendChild(input);
                inputGroup.appendChild(button);
                
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
            editPublishUrlsContainer.textContent = '';
            (topic.publish_urls || []).forEach(url => {
                const inputGroup = document.createElement('div');
                inputGroup.className = 'input-group mb-2';
                
                // Create input element for the publish URL
                const input = document.createElement('input');
                input.type = 'url';
                input.className = 'form-control edit-publish-url';
                input.value = url;
                
                // Create remove button
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'btn btn-outline-danger remove-publish';
                button.textContent = '×';
                button.onclick = function() { removePublishInput(this); };
                
                // Append elements to input group
                inputGroup.appendChild(input);
                inputGroup.appendChild(button);
                
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
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'url';
    input.className = 'form-control feed-url';
    input.placeholder = 'https://example.com/feed';
    
    // Create button element
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-danger remove-feed';
    button.textContent = '×';
    button.onclick = function() { removeFeedInput(this); };
    
    // Append elements to the container
    inputGroup.appendChild(input);
    inputGroup.appendChild(button);
    
    container.insertBefore(inputGroup, container.lastChild);
}

function addEditPublishInput() {
    const container = document.getElementById('editPublishUrlsContainer');
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group mb-2';
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'url';
    input.className = 'form-control edit-publish-url';
    input.placeholder = 'https://example.com/publish';
    
    // Create button element
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-danger remove-publish';
    button.textContent = '×';
    button.onclick = function() { removePublishInput(this); };
    
    // Append elements to the container
    inputGroup.appendChild(input);
    inputGroup.appendChild(button);
    
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
    
    // Create input element
    const input = document.createElement('input');
    input.type = 'url';
    input.className = 'form-control publish-url';
    input.placeholder = 'https://example.com/publish';
    
    // Create button element
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-danger remove-publish';
    button.textContent = '×';
    button.onclick = function() { removePublishInput(this); };
    
    // Append elements to the container
    div.appendChild(input);
    div.appendChild(button);
    
    container.appendChild(div);
}

function removePublishInput(button) {
    button.closest('.input-group').remove();
}

async function publishArticle(topicId) {
    try {
        const button = document.querySelector(`[data-topic-id="${topicId}"].publish-article`);
        const originalIcon = button.innerHTML;
        button.disabled = true;
        
        // Safely clear and add icon
        button.textContent = '';
        const icon = document.createElement('i');
        icon.className = 'bi bi-cloud-upload';
        button.appendChild(icon);
        
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
            button.innerHTML = originalIcon;
        }, 2000);
        
    } catch (error) {
        console.error('Error publishing article:', error);
        showError('Failed to publish article. Please try again later.');
        const button = document.querySelector(`[data-topic-id="${topicId}"].publish-article`);
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-cloud-upload"></i>';
    }
} 