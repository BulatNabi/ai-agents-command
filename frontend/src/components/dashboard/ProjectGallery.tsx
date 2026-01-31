import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { Project } from '@/lib/api';

interface ProjectGalleryProps {
  projects: Project[];
  onSelect?: (project: Project) => void;
  isLoading?: boolean;
}

function getStatusBadge(status: Project['status']) {
  const styles = {
    pending: 'bg-yellow-500/20 text-yellow-400',
    in_progress: 'bg-blue-500/20 text-blue-400',
    completed: 'bg-green-500/20 text-green-400',
    failed: 'bg-red-500/20 text-red-400',
  };

  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[status as keyof typeof styles]}`}>
      {status.replace('_', ' ')}
    </span>
  );
}

function ProjectCard({
  project,
  onSelect,
}: {
  project: Project;
  onSelect?: (project: Project) => void;
}) {
  return (
    <Card
      className="cursor-pointer transition-all hover:border-primary/50 hover:shadow-lg hover:shadow-primary/10"
      onClick={() => onSelect?.(project)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg">{project.name}</CardTitle>
          {getStatusBadge(project.status)}
        </div>
        <CardDescription className="line-clamp-2">{project.prompt}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>{new Date(project.created_at).toLocaleDateString()}</span>
          {project.deploy_url && (
            <>
              <span>•</span>
              <a
                href={project.deploy_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                View Live
              </a>
            </>
          )}
          {project.repo_url && (
            <>
              <span>•</span>
              <a
                href={project.repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                GitHub
              </a>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function ProjectGallery({ projects, onSelect, isLoading }: ProjectGalleryProps) {
  if (isLoading) {
    return (
      <Card className="border-primary/20 bg-card/50 backdrop-blur">
        <CardHeader>
          <CardTitle>Your Projects</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-primary/20 bg-card/50 backdrop-blur">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Your Projects</CardTitle>
          <span className="text-sm text-muted-foreground">{projects.length} projects</span>
        </div>
      </CardHeader>
      <CardContent>
        {projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-muted-foreground">No projects yet</p>
            <p className="text-sm text-muted-foreground">
              Enter your idea above to create your first project
            </p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} onSelect={onSelect} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
