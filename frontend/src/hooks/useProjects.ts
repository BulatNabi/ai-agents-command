import { useState, useEffect, useCallback } from 'react';
import { api, type Project, type PipelineStatus } from '@/lib/api';

export function useProjects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.listProjects();
      setProjects(data.projects);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = useCallback(async (prompt: string, name?: string) => {
    const project = await api.createProject(prompt, name);
    setProjects((prev) => [project, ...prev]);
    return project;
  }, []);

  return {
    projects,
    loading,
    error,
    refetch: fetchProjects,
    createProject,
  };
}

export function usePipelineStatus(projectId: string | null) {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      const data = await api.getPipelineStatus(projectId);
      setStatus(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch status');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchStatus();

    // Poll every 3 seconds when there's an active project
    if (projectId) {
      const interval = setInterval(fetchStatus, 3000);
      return () => clearInterval(interval);
    }
  }, [projectId, fetchStatus]);

  return { status, loading, error, refetch: fetchStatus };
}
