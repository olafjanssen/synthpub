const API_URL = 'http://localhost:8000';

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
    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`);
        const project = await response.json();
        
        // Update the project title
        document.getElementById('project-title').textContent = `Topics for ${project.title}`;
        
        const topicsList = document.getElementById('topics-list');
        topicsList.innerHTML = '';
        
        const template = document.getElementById('topic-template');
        
        for (const topicId of project.topic_ids) {
            const topicResponse = await fetch(`${API_URL}/topics/${topicId}`);
            const topic = await topicResponse.json();
            
            const topicElement = template.content.cloneNode(true);
            
            // Fill in the template
            topicElement.querySelector('.topic-name').textContent = topic.name;
            topicElement.querySelector('.description').textContent = topic.description;
            
            // Set up view article button
            const viewButton = topicElement.querySelector('.view-article');
            viewButton.dataset.topicId = topic.id;
            viewButton.addEventListener('click', () => {
                const urlParams = new URLSearchParams(window.location.search);
                const projectId = urlParams.get("project_id");
                window.location.href = `article.html?id=${topic.article}&project_id=${projectId}`;
            });
            
            // Add feed URLs
            const feedList = topicElement.querySelector('.feed-list');
            topic.feed_urls.forEach(url => {
                const li = document.createElement('li');
                li.textContent = url;
                feedList.appendChild(li);
            });
            
            // Add data attributes and event listeners for other buttons
            const updateButton = topicElement.querySelector('.update-article');
            const editButton = topicElement.querySelector('.edit-article');
            
            updateButton.dataset.topicId = topic.id;
            editButton.dataset.topicId = topic.id;
            
            updateButton.addEventListener('click', () => updateArticle(topic.id));
            editButton.addEventListener('click', () => editTopic(topic.id));
            
            topicsList.appendChild(topicElement);
        }
        
        // Add the new topic card at the end with the same layout as other cards
        const newTopicCard = template.content.cloneNode(true);

            // Fill in the template
            newTopicCard.querySelector('.card-header').innerHTML = "&nbsp;";
            newTopicCard.querySelector('.card-body').innerHTML = `
            <i class="bi bi-plus-circle"></i>
                <p class="card-text">Create New Topic</p>
        `;
        
        const viewButton = newTopicCard.querySelector('.view-article');
        viewButton.style.visibility = "hidden";

        var card = newTopicCard.querySelector('.card');
        card.classList.add('new-project-card');
        card.dataset.bsToggle = 'modal';
        card.dataset.bsTarget = '#createTopicModal';
        topicsList.appendChild(newTopicCard);
        
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
    const name = document.getElementById('topicName').value;
    const description = document.getElementById('topicDescription').value;
    const feedUrls = Array.from(document.querySelectorAll('.feed-url')).map(input => input.value);
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");

    try {
        const response = await fetch(`${API_URL}/topics/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, feed_urls: feedUrls })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const topic = await response.json();
        
        // Add topic to project
        await fetch(`${API_URL}/projects/${projectId}/topics/${topic.id}`, {
            method: 'POST'
        });
        
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
        })
        .catch(error => {
            console.error('Error fetching topic:', error);
            showError('Failed to load topic details. Please try again later.');
        });
}

async function updateTopic() {
    const topicId = document.getElementById('editTopicId').value;
    const name = document.getElementById('editTopicName').value;
    const description = document.getElementById('editTopicDescription').value;
    const feedInputs = document.querySelectorAll('#editFeedUrlsContainer .feed-url');
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");

    const feed_urls = Array.from(feedInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');

    try {
        const response = await fetch(`${API_URL}/topics/${topicId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, feed_urls })
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