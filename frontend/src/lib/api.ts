const API_BASE = import.meta.env.VITE_API_URL || '';

export interface Project {
  id: string;
  name: string;
  prompt: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  repo_url?: string;
  preview_url?: string;
  deploy_url?: string;
}

export interface AgentStatus {
  agent: string;
  status: 'idle' | 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface PipelineStatus {
  project_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  current_agent?: string;
  agents: AgentStatus[];
  progress: number;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  listProjects: () => request<ProjectListResponse>('/api/projects/'),

  getProject: (id: string) => request<Project>(`/api/projects/${id}`),

  createProject: (prompt: string, name?: string) =>
    request<Project>('/api/projects/', {
      method: 'POST',
      body: JSON.stringify({ prompt, name }),
    }),

  getPipelineStatus: (projectId: string) =>
    request<PipelineStatus>(`/api/projects/${projectId}/pipeline`),

  startPipeline: (projectId: string) =>
    request<{ message: string }>(`/api/projects/${projectId}/pipeline/start`, {
      method: 'POST',
    }),
};
