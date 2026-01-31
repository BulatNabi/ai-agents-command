from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4

from ...models.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatus
)

router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory storage for PoC (replace with database later)
_projects: dict[str, ProjectResponse] = {}


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """Create a new project from a prompt."""
    project_id = str(uuid4())[:8]
    now = datetime.utcnow()

    # Generate name from prompt if not provided
    name = project.name or f"project-{project_id}"

    new_project = ProjectResponse(
        id=project_id,
        name=name,
        prompt=project.prompt,
        status=ProjectStatus.PENDING,
        created_at=now,
        updated_at=now
    )

    _projects[project_id] = new_project
    return new_project


@router.get("/", response_model=ProjectListResponse)
async def list_projects():
    """List all projects."""
    projects = list(_projects.values())
    return ProjectListResponse(projects=projects, total=len(projects))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get a specific project by ID."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return _projects[project_id]


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, status: ProjectStatus = None, repo_url: str = None, deploy_url: str = None):
    """Update a project's status or URLs."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")

    project = _projects[project_id]

    if status:
        project.status = status
    if repo_url:
        project.repo_url = repo_url
    if deploy_url:
        project.deploy_url = deploy_url

    project.updated_at = datetime.utcnow()
    _projects[project_id] = project

    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    del _projects[project_id]
