from fastapi import APIRouter, HTTPException, BackgroundTasks
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
async def start_project_pipeline(project_id: str, background_tasks: BackgroundTasks):
    """Start the agent pipeline for a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")

    # Initialize pipeline
    agents = _get_or_create_pipeline(project_id)

    # Update project status
    _projects[project_id].status = ProjectStatus.IN_PROGRESS
    _projects[project_id].updated_at = datetime.utcnow()

    # Start the orchestrator agent
    orchestrator_key = AgentType.ORCHESTRATOR.value
    agents[orchestrator_key] = AgentStatusResponse(
        agent=AgentType.ORCHESTRATOR,
        status=AgentStatus.RUNNING,
        started_at=datetime.utcnow()
    )

    # Run pipeline in background
    background_tasks.add_task(run_pipeline, project_id)

    return {"message": "Pipeline started", "project_id": project_id}


async def run_pipeline(project_id: str):
    """Background task to run the agent pipeline using Claude CLI."""
    from ...core.claude_bridge import get_claude_bridge

    agents = _pipeline_states.get(project_id, {})
    project = _projects.get(project_id)

    if not project:
        return

    bridge = get_claude_bridge()
    user_prompt = project.prompt

    # Agent prompts for each phase
    agent_prompts = {
        AgentType.ORCHESTRATOR: f"""You are the Project Orchestrator. Analyze this project request and create a detailed development plan.

User Request: {user_prompt}

Create a structured plan including:
1. Project name and description
2. Technical stack recommendations
3. Key features to implement
4. File structure
5. Step-by-step implementation order

Output your plan in a structured format.""",

        AgentType.DESIGN: f"""You are the Design Architect. Based on the project request, create a design specification.

User Request: {user_prompt}

Create:
1. Color palette (primary, secondary, accent colors)
2. Typography recommendations
3. Component hierarchy
4. Layout structure
5. UI/UX guidelines

Be specific with hex colors and component names.""",

        AgentType.FRONTEND: f"""You are the Frontend Developer. Build the React frontend for this project.

User Request: {user_prompt}

Using React, TypeScript, and Tailwind CSS:
1. Create the main components
2. Implement responsive layouts
3. Add proper styling
4. Include any necessary state management

Generate the actual code files.""",

        AgentType.BACKEND: f"""You are the Backend Developer. Build the API for this project.

User Request: {user_prompt}

Using FastAPI and Python:
1. Create API endpoints
2. Define data models
3. Implement business logic
4. Add proper error handling

Generate the actual code files.""",

        AgentType.DEVOPS: f"""You are the DevOps Engineer. Set up deployment for this project.

User Request: {user_prompt}

Create:
1. Dockerfile for the application
2. GitHub Actions workflow for CI/CD
3. Deployment configuration

Use the GitHub MCP to create a new repository and push the code."""
    }

    agent_order = [
        AgentType.ORCHESTRATOR,
        AgentType.DESIGN,
        AgentType.FRONTEND,
        AgentType.BACKEND,
        AgentType.DEVOPS,
    ]

    context = {"user_prompt": user_prompt}

    for agent_type in agent_order:
        agent_key = agent_type.value

        # Set agent to running
        agents[agent_key] = AgentStatusResponse(
            agent=agent_type,
            status=AgentStatus.RUNNING,
            started_at=datetime.utcnow()
        )

        try:
            # Call Claude CLI
            result = await bridge.invoke_agent(
                agent_name=agent_key,
                prompt=agent_prompts[agent_type],
                project_id=project_id,
                context=context
            )

            # Update context with this agent's output for next agent
            context[agent_key] = result.get("output", "")

            # Set agent status based on result
            if result["success"]:
                agents[agent_key] = AgentStatusResponse(
                    agent=agent_type,
                    status=AgentStatus.COMPLETED,
                    started_at=agents[agent_key].started_at,
                    completed_at=datetime.utcnow(),
                    output=result["output"][:500] if result["output"] else "Completed"
                )
            else:
                agents[agent_key] = AgentStatusResponse(
                    agent=agent_type,
                    status=AgentStatus.FAILED,
                    started_at=agents[agent_key].started_at,
                    completed_at=datetime.utcnow(),
                    error=result.get("error", "Unknown error")
                )
                # Stop pipeline on failure
                project.status = ProjectStatus.FAILED
                project.updated_at = datetime.utcnow()
                return

        except Exception as e:
            agents[agent_key] = AgentStatusResponse(
                agent=agent_type,
                status=AgentStatus.FAILED,
                started_at=agents[agent_key].started_at,
                completed_at=datetime.utcnow(),
                error=str(e)
            )
            project.status = ProjectStatus.FAILED
            project.updated_at = datetime.utcnow()
            return

    # All agents completed successfully
    project.status = ProjectStatus.COMPLETED
    project.updated_at = datetime.utcnow()
