import { useState } from 'react';
import { MainIdeaInput } from '@/components/dashboard/MainIdeaInput';
import { AgentStatusTracker } from '@/components/dashboard/AgentStatusTracker';
import { ProjectGallery } from '@/components/dashboard/ProjectGallery';
import { useProjects, usePipelineStatus } from '@/hooks/useProjects';
import { api } from '@/lib/api';
import type { Project } from '@/lib/api';

function App() {
  const { projects, loading: projectsLoading, createProject } = useProjects();
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const { status: pipelineStatus, loading: pipelineLoading, refetch: refetchPipeline } = usePipelineStatus(activeProjectId);

  const handleSubmit = async (prompt: string) => {
    try {
      setIsCreating(true);
      const project = await createProject(prompt);
      setActiveProjectId(project.id);
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleSelectProject = (project: Project) => {
    setActiveProjectId(project.id);
  };

  const handleStartPipeline = async () => {
    if (!activeProjectId) return;
    try {
      setIsStarting(true);
      await api.startPipeline(activeProjectId);
      refetchPipeline();
    } catch (error) {
      console.error('Failed to start pipeline:', error);
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/30 backdrop-blur-xl">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🏭</span>
            <h1 className="text-xl font-bold">Agentic Web Factory</h1>
          </div>
          <p className="text-sm text-muted-foreground">Prompt → Design → Build → Deploy</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto space-y-8 px-4 py-8">
        {/* Input Section */}
        <section>
          <MainIdeaInput onSubmit={handleSubmit} isLoading={isCreating} />
        </section>

        {/* Pipeline Status */}
        {activeProjectId && (
          <section>
            <AgentStatusTracker
              status={pipelineStatus}
              isLoading={pipelineLoading}
              onStart={handleStartPipeline}
              isStarting={isStarting}
            />
          </section>
        )}

        {/* Projects Gallery */}
        <section>
          <ProjectGallery
            projects={projects}
            onSelect={handleSelectProject}
            isLoading={projectsLoading}
          />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-card/30">
        <div className="container mx-auto flex h-14 items-center justify-center px-4">
          <p className="text-sm text-muted-foreground">
            Built with Claude Code Agents • React • FastAPI
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
