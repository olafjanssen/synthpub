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
    projectsList.innerHTML = '';
    
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

var cardIndex = 0;

function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'card';

    const cardHeader = document.createElement('div');
    cardHeader.className = 'card-header';

    const cardImg = document.createElement('img');
    cardImg.className = 'card-img-top';
    cardImg.src = `/img/bg/bg-${(cardIndex++ % 5) + 1}.png`;
    cardImg.alt = 'Card image cap';
    
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
    
    cardHeader.appendChild(cardImg);
    card.appendChild(cardHeader);
    
    cardBody.appendChild(cardTitle);
    card.appendChild(cardBody);

    cardFooter.appendChild(cardText);
    cardFooter.appendChild(viewTopicsLink);
    card.appendChild(cardFooter);
    
    return card;
}

function viewTopics(projectId) {
    // Implement the logic to view topics for the given projectId
    console.log(`Viewing topics for project ID: ${projectId}`);
    // You can redirect to a topics page or open a modal with topics
} 