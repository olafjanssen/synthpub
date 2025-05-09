/*global bootstrap */

const API_URL = '/api';

document.addEventListener("DOMContentLoaded", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    if (projectId) {
        loadTopics(projectId);
    }
    
    // Load available prompts for the dropdowns
    loadPrompts();
    
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
        addPublishBtn.addEventListener('click', addPublishingChain);
    }

    // Connect remove feed buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-feed')) {
            removeFeedInput(event.target);
        }
    });

    // Connect remove chain buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-chain')) {
            removePublishingChain(event.target);
        }
    });

    // Connect add chain item buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('add-chain-item')) {
            addChainItem(event.target);
        }
    });

    // Connect remove chain item buttons
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-chain-item')) {
            removeChainItem(event.target);
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
        publishButton.title = 'No publishing chains configured';
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

// Function to load prompts from API and populate dropdowns
async function loadPrompts() {
    try {
        const response = await fetch(`${API_URL}/prompts`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const prompts = await response.json();
        
        // Sort prompts alphabetically by name
        prompts.sort((a, b) => a.name.localeCompare(b.name));
        
        // Populate create form dropdown
        const createDropdown = document.getElementById('promptSelect');
        // Populate edit form dropdown
        const editDropdown = document.getElementById('editPromptSelect');
        
        // Clear any existing options except the default
        while (createDropdown.options.length > 1) {
            createDropdown.remove(1);
        }
        
        while (editDropdown.options.length > 1) {
            editDropdown.remove(1);
        }
        
        // Add options for each prompt
        prompts.forEach(prompt => {
            // Add to create form dropdown
            const createOption = document.createElement('option');
            createOption.value = prompt.id;
            createOption.textContent = prompt.name;
            createDropdown.appendChild(createOption);
            
            // Add to edit form dropdown
            const editOption = document.createElement('option');
            editOption.value = prompt.id;
            editOption.textContent = prompt.name;
            editDropdown.appendChild(editOption);
        });
    } catch (error) {
        console.error('Error loading prompts:', error);
        showError('Failed to load prompts. Default prompt will be used.');
    }
}

async function generateWorkflowVisualization(topicId) {
    try {
        // Request TXT format - backend will handle fallback to markdown if needed
        const response = await fetch(`${API_URL}/topics/${topicId}/workflow?format=txt`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // The visualization is automatically saved to the topic's directory
        // We don't need to do anything with the response
    } catch (error) {
        console.error('Error generating workflow visualization:', error);
        // Don't show error to user as this is a background task
    }
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
    const promptId = document.getElementById('promptSelect').value;
    const feedUrls = Array.from(document.querySelectorAll('.feed-url'))
        .map(input => input.value)
        .filter(url => url.trim() !== '');
    
    // Get publishing chains
    const publishUrls = Array.from(document.querySelectorAll('.chain-container'))
        .map(container => {
            const chainItems = Array.from(container.querySelectorAll('.chain-item'))
                .map(input => input.value.trim())
                .filter(item => item !== '');
            return chainItems.join(' | ');
        })
        .filter(chain => chain !== '');

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
                thumbnail_url: thumbnailUrl,
                prompt_id: promptId || null
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const topic = await response.json();
        
        // Generate workflow visualization
        await generateWorkflowVisualization(topic.id);
        
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
            
            // Set the custom prompt dropdown
            const promptDropdown = document.getElementById('editPromptSelect');
            if (topic.prompt_id) {
                // Find and select the matching option
                for (let i = 0; i < promptDropdown.options.length; i++) {
                    if (promptDropdown.options[i].value === topic.prompt_id) {
                        promptDropdown.selectedIndex = i;
                        break;
                    }
                }
            } else {
                // Select the default option
                promptDropdown.selectedIndex = 0;
            }

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
            
            // Add publishing chains
            (topic.publish_urls || []).forEach(url => {
                const chainContainer = document.createElement('div');
                chainContainer.className = 'chain-container mb-3';
                
                // Create chain header
                const header = document.createElement('div');
                header.className = 'd-flex justify-content-between align-items-center mb-2';
                
                const label = document.createElement('label');
                label.className = 'form-label mb-0';
                label.textContent = 'Chain Items';
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn btn-outline-danger btn-sm remove-chain';
                removeBtn.textContent = 'Remove Chain';
                
                header.appendChild(label);
                header.appendChild(removeBtn);
                
                // Create items container
                const itemsContainer = document.createElement('div');
                itemsContainer.className = 'chain-items-container';
                
                // Split the URL by pipe and create items
                const chainItems = url.split('|').map(item => item.trim());
                
                chainItems.forEach(item => {
                    const inputGroup = document.createElement('div');
                    inputGroup.className = 'input-group mb-2';
                    
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.className = 'form-control chain-item';
                    input.value = item;
                    
                    const itemRemoveBtn = document.createElement('button');
                    itemRemoveBtn.type = 'button';
                    itemRemoveBtn.className = 'btn btn-outline-danger remove-chain-item';
                    itemRemoveBtn.textContent = '×';
                    
                    inputGroup.appendChild(input);
                    inputGroup.appendChild(itemRemoveBtn);
                    itemsContainer.appendChild(inputGroup);
                });
                
                // Add button to add chain items
                const addItemBtn = document.createElement('button');
                addItemBtn.type = 'button';
                addItemBtn.className = 'btn btn-outline-secondary btn-sm add-chain-item';
                addItemBtn.textContent = 'Add Chain Item';
                
                // Assemble chain container
                chainContainer.appendChild(header);
                chainContainer.appendChild(itemsContainer);
                chainContainer.appendChild(addItemBtn);
                
                editPublishUrlsContainer.appendChild(chainContainer);
            });

            // Add "Add Publishing Chain" button
            const addChainButton = document.createElement('button');
            addChainButton.type = 'button';
            addChainButton.className = 'btn btn-outline-secondary btn-sm';
            addChainButton.textContent = 'Add Publishing Chain';
            addChainButton.onclick = () => addEditPublishingChain();
            editPublishUrlsContainer.appendChild(addChainButton);
            
            // Add the Restart button to the modal footer
            const modalFooter = document.querySelector('#editTopicModal .modal-footer');
            
            // Remove any existing restart button first (to avoid duplicates)
            const existingButton = modalFooter.querySelector('.restart-topic-btn');
            if (existingButton) {
                existingButton.remove();
            }
            
            // Add the restart button
            const restartButton = document.createElement('button');
            restartButton.type = 'button';
            restartButton.className = 'btn btn-warning restart-topic-btn';
            restartButton.textContent = 'Restart Topic';
            restartButton.onclick = () => restartTopic(topicId);
            
            // Insert it next to the remove button
            const removeButton = modalFooter.querySelector('.remove-article');
            removeButton.insertAdjacentElement('afterend', restartButton);
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

function addEditPublishingChain() {
    const container = document.getElementById('editPublishUrlsContainer');
    const chainContainer = createChainContainer();
    container.insertBefore(chainContainer, container.lastChild);
}

function addEditPublishInput() {
    // Replace with addEditPublishingChain functionality
    addEditPublishingChain();
}

async function updateTopic() {
    const topicId = document.getElementById('editTopicId').value;
    const name = document.getElementById('editTopicName').value;
    const description = document.getElementById('editTopicDescription').value;
    const thumbnailUrl = document.getElementById('editThumbnailUrl').value.trim();
    const promptId = document.getElementById('editPromptSelect').value;
    const feedInputs = document.querySelectorAll('#editFeedUrlsContainer .feed-url');
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");

    const feed_urls = Array.from(feedInputs)
        .map(input => input.value.trim())
        .filter(url => url !== '');

    // Get publishing chains
    const publish_urls = Array.from(document.querySelectorAll('#editPublishUrlsContainer .chain-container'))
        .map(container => {
            const chainItems = Array.from(container.querySelectorAll('.chain-item'))
                .map(input => input.value.trim())
                .filter(item => item !== '');
            return chainItems.join(' | ');
        })
        .filter(chain => chain !== '');

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
                thumbnail_url: thumbnailUrl,
                prompt_id: promptId || null
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Generate workflow visualization
        await generateWorkflowVisualization(topicId);

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

function addPublishingChain() {
    const container = document.getElementById('publishUrlsContainer');
    const chainContainer = createChainContainer();
    container.appendChild(chainContainer);
}

function createChainContainer() {
    const chainContainer = document.createElement('div');
    chainContainer.className = 'chain-container mb-3';
    
    // Create chain header with label and remove button
    const header = document.createElement('div');
    header.className = 'd-flex justify-content-between align-items-center mb-2';
    
    const label = document.createElement('label');
    label.className = 'form-label mb-0';
    label.textContent = 'Chain Items';
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-outline-danger btn-sm remove-chain';
    removeBtn.textContent = 'Remove Chain';
    
    header.appendChild(label);
    header.appendChild(removeBtn);
    
    // Create items container
    const itemsContainer = document.createElement('div');
    itemsContainer.className = 'chain-items-container';
    
    // Add initial chain item
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group mb-2';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control chain-item';
    input.placeholder = 'Chain item';
    
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-danger remove-chain-item';
    button.textContent = '×';
    
    inputGroup.appendChild(input);
    inputGroup.appendChild(button);
    itemsContainer.appendChild(inputGroup);
    
    // Add "Add Chain Item" button
    const addItemBtn = document.createElement('button');
    addItemBtn.type = 'button';
    addItemBtn.className = 'btn btn-outline-secondary btn-sm add-chain-item';
    addItemBtn.textContent = 'Add Chain Item';
    
    // Assemble chain container
    chainContainer.appendChild(header);
    chainContainer.appendChild(itemsContainer);
    chainContainer.appendChild(addItemBtn);
    
    return chainContainer;
}

function removePublishingChain(button) {
    button.closest('.chain-container').remove();
}

function addChainItem(button) {
    const container = button.previousElementSibling;
    
    const inputGroup = document.createElement('div');
    inputGroup.className = 'input-group mb-2';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'form-control chain-item';
    input.placeholder = 'Chain item';
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn btn-outline-danger remove-chain-item';
    removeBtn.textContent = '×';
    
    inputGroup.appendChild(input);
    inputGroup.appendChild(removeBtn);
    
    container.appendChild(inputGroup);
}

function removeChainItem(button) {
    const inputGroup = button.closest('.input-group');
    const container = inputGroup.closest('.chain-items-container');
    
    // Only remove if there's more than one item
    if (container.querySelectorAll('.input-group').length > 1) {
        inputGroup.remove();
    }
}

function addPublishInput() {
    // Replace with addPublishingChain functionality
    addPublishingChain();
}

function removePublishInput(button) {
    // This function is kept for backward compatibility
    // If it's a chain container button, use removePublishingChain
    if (button.classList.contains('remove-chain')) {
        removePublishingChain(button);
    } else {
        // Otherwise, it's an old-style remove button
        button.closest('.input-group').remove();
    }
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

// Add this function to handle topic restarting
async function restartTopic(topicId) {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get("project_id");
    
    try {
        // Show confirmation dialog
        if (!confirm("Are you sure you want to restart this topic? The current topic will be archived and a new one created with the same configuration.")) {
            return;
        }
        
        // Restart the topic
        const response = await fetch(`${API_URL}/topics/${topicId}/restart`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const newTopic = await response.json();
        
        // Generate workflow visualization for the new topic
        await generateWorkflowVisualization(newTopic.id);
        
        // Close modal if open
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTopicModal'));
        if (modal) {
            modal.hide();
        }
        
        // Refresh topics list
        await loadTopics(projectId);
        
        // Show success message
        alert(`Topic restarted successfully. The original topic has been archived.`);
        
    } catch (error) {
        console.error('Error restarting topic:', error);
        showError('Failed to restart topic. Please try again later.');
    }
} 