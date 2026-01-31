from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    ORCHESTRATOR = "orchestrator-agent"
    DESIGN = "design-architect-agent"
    FRONTEND = "frontend-developer-agent"
    BACKEND = "backend-developer-agent"
    DEVOPS = "devops-agent"


class ProjectStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Project Schemas
class ProjectCreate(BaseModel):
    prompt: str = Field(..., min_length=10, description="The main idea/prompt for the web application")
    name: Optional[str] = Field(None, description="Optional project name")


class ProjectResponse(BaseModel):
    id: str
    name: str
    prompt: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    repo_url: Optional[str] = None
    deploy_url: Optional[str] = None


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


# Agent Schemas
class AgentTriggerRequest(BaseModel):
    project_id: str
    agent_type: AgentType
    context: Optional[dict] = None


class AgentStatusResponse(BaseModel):
    agent: AgentType
    status: AgentStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None


class AgentPipelineStatus(BaseModel):
    project_id: str
    current_agent: Optional[AgentType] = None
    agents: list[AgentStatusResponse]


# Agent Handover Schema (matches JSON schema)
class AgentHandover(BaseModel):
    agent_id: str
    project_id: str
    timestamp: datetime
    status: str
    summary: str
    artifacts: list[dict] = []
    next_agent: Optional[str] = None
    context: dict = {}


# Health Check
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    timestamp: datetime
