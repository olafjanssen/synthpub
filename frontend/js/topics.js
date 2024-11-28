const API_URL = 'http://localhost:8000';

async function fetchTopics() {
    try {
        const response = await fetch(`${API_URL}/topics/`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const topics = await response.json();
        displayTopics(topics);
    } catch (error) {
        console.error('Error fetching topics:', error);
        showError('Failed to load topics. Please try again later.');
    }
}

function displayTopics(topics) {
    const topicsList = document.getElementById('topics-list');
    const template = document.getElementById('topic-template');
    
    // Clear existing topics
    topicsList.innerHTML = '';
    
    if (topics.length === 0) {
        topicsList.innerHTML = '<div class="col-12"><p class="text-center text-muted">No topics found</p></div>';
        return;
    }
    
    topics.forEach(topic => {
        const topicElement = template.content.cloneNode(true);
        
        // Fill in the template
        topicElement.querySelector('.topic-name').textContent = topic.name;
        topicElement.querySelector('.description').textContent = topic.description;
        
        // Set up view article button
        const viewButton = topicElement.querySelector('.view-article');
        viewButton.dataset.topicId = topic.id;
        viewButton.addEventListener('click', () => window.location.href = `article.html?id=${topic.article}`);
        
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
    });
}

async function updateArticle(topicId) {
    try {
        // Find and update the button state
        const button = document.querySelector(`[data-topic-id="${topicId}"]`);
        const originalText = button.textContent;
        button.disabled = true;
        button.textContent = 'Updating...';
        
        // Call the update endpoint
        const response = await fetch(`${API_URL}/topics/${topicId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Refresh the topics list
        await fetchTopics();
        
    } catch (error) {
        console.error('Error updating article:', error);
        showError('Failed to update article. Please try again later.');
    }
}

function showError(message) {
    // Simple error display - you might want to make this more sophisticated
    alert(message);
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
    const feedInputs = document.querySelectorAll('.feed-url');
    
    // Collect non-empty feed URLs
    const feed_urls = Array.from(feedInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');
    
    const topicData = {
        name,
        description,
        feed_urls
    };
    
    try {
        const response = await fetch(`${API_URL}/topics/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(topicData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
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
        await fetchTopics();
        
    } catch (error) {
        console.error('Error creating topic:', error);
        showError('Failed to create topic. Please try again later.');
    }
}

function viewArticle(topicId, articleId) {
    window.location.href = `article.html?id=${articleId}`;
}

async function removeTopic(topicId) {
    try {
        const response = await fetch(`${API_URL}/topics/${topicId}/`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Refresh the topics list
        await fetchTopics();
    } catch (error) {
        console.error('Error removing topic:', error);
        showError('Failed to remove topic. Please try again later.');
    }
}

function editTopic(topicId) {
    const topicElement = document.querySelector(`[data-topic-id="${topicId}"]`).closest('.card');
    const topicName = topicElement.querySelector('.card-title').textContent;
    const topicDescription = topicElement.querySelector('.description').textContent;
    const feedUrls = Array.from(topicElement.querySelectorAll('.feed-list li')).map(li => li.textContent);

    // Populate the edit form
    document.getElementById('editTopicId').value = topicId;
    document.getElementById('editTopicName').value = topicName;
    document.getElementById('editTopicDescription').value = topicDescription;

    // Clear existing feed URLs
    const editFeedUrlsContainer = document.getElementById('editFeedUrlsContainer');
    editFeedUrlsContainer.innerHTML = '';
    feedUrls.forEach(url => {
        const inputGroup = document.createElement('div');
        inputGroup.className = 'input-group mb-2';
        inputGroup.innerHTML = `
            <input type="url" class="form-control feed-url" value="${url}">
            <button type="button" class="btn btn-outline-danger remove-feed" onclick="removeFeedInput(this)">×</button>
        `;
        editFeedUrlsContainer.appendChild(inputGroup);
    });
}

async function updateTopic() {
    const topicId = document.getElementById('editTopicId').value;
    const name = document.getElementById('editTopicName').value;
    const description = document.getElementById('editTopicDescription').value;
    const feedInputs = document.querySelectorAll('#editFeedUrlsContainer .feed-url');

    // Collect non-empty feed URLs
    const feed_urls = Array.from(feedInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');

    const topicData = {
        name,
        description,
        feed_urls
    };

    try {
        const response = await fetch(`${API_URL}/topics/${topicId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(topicData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close modal and refresh topics list
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTopicModal'));
        modal.hide();
        await fetchTopics();
    } catch (error) {
        console.error('Error updating topic:', error);
        showError('Failed to update topic. Please try again later.');
    }
}

// Update the event listeners for the buttons
document.addEventListener('DOMContentLoaded', () => {
    fetchTopics();
    document.getElementById('topics-list').addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-article')) {
            const topicId = event.target.closest('.card-footer').querySelector('.view-article').dataset.topicId;
            removeTopic(topicId);
        } else if (event.target.classList.contains('edit-article')) {
            const topicId = event.target.closest('.card-footer').querySelector('.view-article').dataset.topicId;
            editTopic(topicId);
        }
    });
});

// Initial load
document.addEventListener('DOMContentLoaded', fetchTopics); 