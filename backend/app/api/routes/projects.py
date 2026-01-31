from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4

from ...models.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectStatus,
    AgentPipelineStatus,
    AgentStatusResponse,
    AgentType,
    AgentStatus
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


# In-memory pipeline states (shared with agents module in real implementation)
_pipeline_states: dict[str, dict[str, AgentStatusResponse]] = {}


def _get_or_create_pipeline(project_id: str) -> dict[str, AgentStatusResponse]:
    """Get or initialize pipeline state for a project."""
    if project_id not in _pipeline_states:
        _pipeline_states[project_id] = {
            agent.value: AgentStatusResponse(
                agent=agent,
                status=AgentStatus.IDLE
            )
            for agent in AgentType
        }
    return _pipeline_states[project_id]


@router.get("/{project_id}/pipeline", response_model=AgentPipelineStatus)
async def get_project_pipeline(project_id: str):
    """Get the pipeline status for a project."""
    agents = _get_or_create_pipeline(project_id)

    # Find current running agent
    current_agent = None
    for agent_type, status in agents.items():
        if status.status == AgentStatus.RUNNING:
            current_agent = AgentType(agent_type)
            break

    return AgentPipelineStatus(
        project_id=project_id,
        current_agent=current_agent,
        agents=list(agents.values())
    )


@router.post("/{project_id}/pipeline/start")
async def start_project_pipeline(project_id: str):
    """Start the agent pipeline for a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")

    # Initialize pipeline if needed
    _get_or_create_pipeline(project_id)

    # Update project status
    _projects[project_id].status = ProjectStatus.IN_PROGRESS
    _projects[project_id].updated_at = datetime.utcnow()

    return {"message": "Pipeline started", "project_id": project_id}
