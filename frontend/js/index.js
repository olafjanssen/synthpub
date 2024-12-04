const API_URL = 'http://localhost:8000';

document.addEventListener("DOMContentLoaded", function() {
    loadProjects();
});

function loadProjects() {
    fetch(`${API_URL}/projects/`)
        .then(response => response.json())
        .then(projects => {
            const projectsList = document.getElementById("projects-list");
            projectsList.innerHTML = "";
            projects.forEach(project => {
                const projectCard = document.createElement("div");
                projectCard.className = "col";
                projectCard.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${project.title}</h5>
                            <p class="card-text">${project.description}</p>
                            <a href="project.html?project_id=${project.id}" class="btn btn-primary">View Topics</a>
                        </div>
                    </div>
                `;
                projectsList.appendChild(projectCard);
            });
        })
        .catch(error => console.error("Error loading projects:", error));
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