const API_URL = 'http://localhost:8000';

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
    const newProjectCard = projectsList.querySelector('.new-project-card');
    
    // Clear existing projects but keep the new project card
    projectsList.innerHTML = '';
    
    // Add all project cards
    projects.forEach(project => {
        const projectCard = createProjectCard(project);
        projectsList.appendChild(projectCard);
    });
    
    // Add the new project card at the end
    projectsList.appendChild(newProjectCard);
}

function createProject() {
    const title = document.getElementById("projectTitle").value;
    const description = document.getElementById("projectDescription").value;

    fetch(`${API_URL}/projects/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ title, description })
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

function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    
    const cardTitle = document.createElement('h5');
    cardTitle.className = 'card-title';
    cardTitle.textContent = project.title;
    
    const cardText = document.createElement('p');
    cardText.className = 'card-text';
    cardText.textContent = project.description;
    
    const viewTopicsLink = document.createElement('a');
    viewTopicsLink.href = `project.html?project_id=${project.id}`;
    viewTopicsLink.className = 'btn btn-primary';
    viewTopicsLink.textContent = 'View Topics';
    
    cardBody.appendChild(cardTitle);
    cardBody.appendChild(cardText);
    cardBody.appendChild(viewTopicsLink);
    card.appendChild(cardBody);
    
    return card;
}

function viewTopics(projectId) {
    // Implement the logic to view topics for the given projectId
    console.log(`Viewing topics for project ID: ${projectId}`);
    // You can redirect to a topics page or open a modal with topics
} 