/** @global {Object} bootstrap */
/** @global {Object} bootstrap.Modal */

const API_URL = '/api';

document.addEventListener("DOMContentLoaded", function() {
    loadProjects();
});

function loadProjects() {
    fetch(`${API_URL}/projects/`)
        .then(response => response.json())
        .then(projects => {
            renderProjects(projects);
        })
        .catch(error => console.error("Error loading projects:", error));
}
function renderProjects(projects) {
    const projectsList = document.getElementById('projects-list');
    const emptyCard = document.getElementById('projects-list').querySelector('.empty-card');

    // Clear existing projects but keep the new project card
    projectsList.textContent = '';
    
    // Add all project cards
    projects.forEach(project => {
        const projectCard = createProjectCard(project);
        projectsList.appendChild(projectCard);
    });

    // Add empty cards until we have at least 30 total
    const totalCards = projects.length;
    const emptyCardsNeeded = Math.max(0, 30 - totalCards);
    
    for (let i = 0; i < emptyCardsNeeded; i++) {
        projectsList.appendChild(emptyCard.cloneNode(true));
    }
}

function createProject() {
    const title = document.getElementById("projectTitle").value;
    const description = document.getElementById("projectDescription").value;
    const thumbnailUrl = document.getElementById("projectThumbnailUrl").value.trim();

    fetch(`${API_URL}/projects/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            title, 
            description,
            thumbnail_url: thumbnailUrl // Send empty string if field is empty
        })
    })
    .then(response => response.json())
    .then(project => {
        loadProjects();
        document.getElementById("createProjectForm").reset();
        const modal = bootstrap.Modal.getInstance(document.getElementById("createProjectModal"));
        modal.hide();
    })
    .catch(error => console.error("Error creating project:", error));
}

var cardIndex = 0;

function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'card';

    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';

    // Create a header buttons container
    const cardHeaderButtons = document.createElement('div');
    cardHeaderButtons.className = 'card-header-buttons';
    
    // Add edit button
    const editButton = document.createElement('button');
    editButton.className = 'btn btn-link btn-sm p-0 edit-project';
    editButton.setAttribute('data-bs-toggle', 'modal');
    editButton.setAttribute('data-bs-target', '#editProjectModal');
    editButton.title = 'Edit Project';
    
    // Create icon element
    const icon = document.createElement('i');
    icon.className = 'bi bi-pencil';
    editButton.appendChild(icon);
    
    editButton.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        editProject(project.id);
    };
    
    // Add the edit button to the header buttons
    cardHeaderButtons.appendChild(editButton);
    
    const cardImg = document.createElement('img');
    cardImg.className = 'card-img-top';
    
    // Use Pexels thumbnail if available, otherwise use default image
    if (project.thumbnail_url) {
        cardImg.src = project.thumbnail_url;
    } else {
        cardImg.src = `/img/bg/bg-${(cardIndex++ % 5) + 1}.png`;
    }
    
    cardImg.alt = project.title;

    // Add buttons to header
    cardHeader.appendChild(cardImg);
    cardHeader.appendChild(cardHeaderButtons);
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    
    const cardTitle = document.createElement('h5');
    cardTitle.className = 'card-title';
    cardTitle.textContent = project.title;
    
    const cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer';

    const cardText = document.createElement('p');
    cardText.className = 'card-text';
    cardText.textContent = project.description;
    
    const viewTopicsLink = document.createElement('a');
    viewTopicsLink.href = `project.html?project_id=${project.id}`;
    viewTopicsLink.className = 'stretched-link';
    
    card.appendChild(cardHeader);
    
    cardBody.appendChild(cardTitle);
    card.appendChild(cardBody);

    cardFooter.appendChild(cardText);
    cardFooter.appendChild(viewTopicsLink);
    card.appendChild(cardFooter);
    
    return card;
}

function editProject(projectId) {
    fetch(`${API_URL}/projects/${projectId}`)
        .then(response => response.json())
        .then(project => {
            // Populate the edit form
            document.getElementById('editProjectId').value = projectId;
            document.getElementById('editProjectTitle').value = project.title;
            document.getElementById('editProjectDescription').value = project.description;
            document.getElementById('editProjectThumbnailUrl').value = project.thumbnail_url || '';
        })
        .catch(error => {
            console.error('Error fetching project details:', error);
            showError('Failed to load project details. Please try again later.');
        });
}

async function updateProject() {
    const projectId = document.getElementById('editProjectId').value;
    const title = document.getElementById('editProjectTitle').value;
    const description = document.getElementById('editProjectDescription').value;
    const thumbnailUrl = document.getElementById('editProjectThumbnailUrl').value.trim();

    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                title, 
                description,
                thumbnail_url: thumbnailUrl // Send empty string if field is empty
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close modal and refresh projects list
        const modal = bootstrap.Modal.getInstance(document.getElementById('editProjectModal'));
        modal.hide();
        await loadProjects();
    } catch (error) {
        console.error('Error updating project:', error);
        showError('Failed to update project. Please try again later.');
    }
}

async function deleteProject() {
    const projectId = document.getElementById('editProjectId').value;
    
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/projects/${projectId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Close modal and refresh projects list
        const modal = bootstrap.Modal.getInstance(document.getElementById('editProjectModal'));
        modal.hide();
        await loadProjects();
    } catch (error) {
        console.error('Error deleting project:', error);
        showError('Failed to delete project. Please try again later.');
    }
}

function showError(message) {
    alert(message); // Simple error display for now
}

function viewTopics(projectId) {
    // Implement the logic to view topics for the given projectId
    console.log(`Viewing topics for project ID: ${projectId}`);
    // You can redirect to a topics page or open a modal with topics
} 