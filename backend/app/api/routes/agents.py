from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from ...models.schemas import (
    AgentTriggerRequest,
    AgentStatusResponse,
    AgentPipelineStatus,
    AgentType,
    AgentStatus
)
from ...core.claude_bridge import get_claude_bridge

router = APIRouter(prefix="/agents", tags=["agents"])

# In-memory agent status tracking (replace with proper state management later)
_agent_states: dict[str, dict[str, AgentStatusResponse]] = {}


def _get_or_create_project_agents(project_id: str) -> dict[str, AgentStatusResponse]:
    """Get or initialize agent states for a project."""
    if project_id not in _agent_states:
        _agent_states[project_id] = {
            agent.value: AgentStatusResponse(
                agent=agent,
                status=AgentStatus.IDLE
            )
            for agent in AgentType
        }
    return _agent_states[project_id]


@router.post("/trigger", response_model=AgentStatusResponse)
async def trigger_agent(request: AgentTriggerRequest, background_tasks: BackgroundTasks):
    """Trigger a specific agent for a project."""
    agents = _get_or_create_project_agents(request.project_id)
    agent_key = request.agent_type.value

    # Check if agent is already running
    if agents[agent_key].status == AgentStatus.RUNNING:
        raise HTTPException(
            status_code=409,
            detail=f"Agent {request.agent_type} is already running for this project"
        )

    # Update status to running
    agents[agent_key] = AgentStatusResponse(
        agent=request.agent_type,
        status=AgentStatus.RUNNING,
        started_at=datetime.utcnow()
    )

    # Run agent in background
    background_tasks.add_task(
        _run_agent,
        request.project_id,
        request.agent_type,
        request.context
    )

    return agents[agent_key]


async def _run_agent(project_id: str, agent_type: AgentType, context: dict | None):
    """Background task to run an agent."""
    bridge = get_claude_bridge()
    agents = _get_or_create_project_agents(project_id)
    agent_key = agent_type.value

    try:
        # Build prompt based on agent type
        prompt = _build_agent_prompt(agent_type, context)

        result = await bridge.invoke_agent(
            agent_name=agent_type.value,
            prompt=prompt,
            project_id=project_id,
            context=context
        )

        agents[agent_key] = AgentStatusResponse(
            agent=agent_type,
            status=AgentStatus.COMPLETED if result["success"] else AgentStatus.FAILED,
            started_at=agents[agent_key].started_at,
            completed_at=datetime.utcnow(),
            output=result["output"][:1000] if result["output"] else None,
            error=result["error"] if not result["success"] else None
        )

    except Exception as e:
        agents[agent_key] = AgentStatusResponse(
            agent=agent_type,
            status=AgentStatus.FAILED,
            started_at=agents[agent_key].started_at,
            completed_at=datetime.utcnow(),
            error=str(e)
        )


def _build_agent_prompt(agent_type: AgentType, context: dict | None) -> str:
    """Build a prompt for the given agent type."""
    base_prompts = {
        AgentType.ORCHESTRATOR: "Analyze this project request and create a development plan.",
        AgentType.DESIGN: "Create a design specification based on the project requirements.",
        AgentType.FRONTEND: "Implement the frontend based on the design specification.",
        AgentType.BACKEND: "Implement the backend API based on the project requirements.",
        AgentType.DEVOPS: "Set up deployment configuration for this project."
    }

    prompt = base_prompts.get(agent_type, "Execute your specialized task.")

    if context and "prompt" in context:
        prompt = f"{prompt}\n\nProject prompt: {context['prompt']}"

    return prompt


@router.get("/status/{project_id}", response_model=AgentPipelineStatus)
async def get_pipeline_status(project_id: str):
    """Get the status of all agents for a project."""
    agents = _get_or_create_project_agents(project_id)

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


@router.get("/logs/{project_id}")
async def get_agent_logs(project_id: str):
    """Get all agent logs for a project."""
    bridge = get_claude_bridge()
    logs = bridge.get_project_logs(project_id)
    return {"project_id": project_id, "logs": logs}
