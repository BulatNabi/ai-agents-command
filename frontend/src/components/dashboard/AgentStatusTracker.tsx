import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { PipelineStatus, AgentStatus } from '@/lib/api';

interface AgentStatusTrackerProps {
  status: PipelineStatus | null;
  isLoading?: boolean;
}

const AGENT_ORDER = [
  { id: 'orchestrator-agent', label: 'Orchestrator', icon: '🎯' },
  { id: 'design-architect-agent', label: 'Design', icon: '🎨' },
  { id: 'frontend-developer-agent', label: 'Frontend', icon: '⚛️' },
  { id: 'backend-developer-agent', label: 'Backend', icon: '🔧' },
  { id: 'devops-agent', label: 'Deploy', icon: '🚀' },
];

function getStatusColor(status: AgentStatus['status']): string {
  switch (status) {
    case 'running':
      return 'bg-primary animate-pulse';
    case 'completed':
      return 'bg-green-500';
    case 'failed':
      return 'bg-destructive';
    default:
      return 'bg-muted';
  }
}

function AgentNode({
  agent,
  status,
  isActive,
}: {
  agent: (typeof AGENT_ORDER)[number];
  status?: AgentStatus;
  isActive: boolean;
}) {
  const statusClass = status ? getStatusColor(status.status) : 'bg-muted';

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`relative flex h-16 w-16 items-center justify-center rounded-full border-2 transition-all ${
          isActive ? 'border-primary scale-110' : 'border-border'
        } ${statusClass}`}
      >
        <span className="text-2xl">{agent.icon}</span>
        {status?.status === 'running' && (
          <span className="absolute -right-1 -top-1 flex h-4 w-4">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
            <span className="relative inline-flex h-4 w-4 rounded-full bg-primary" />
          </span>
        )}
      </div>
      <span className="text-sm font-medium">{agent.label}</span>
      {status && (
        <span className="text-xs text-muted-foreground capitalize">{status.status}</span>
      )}
    </div>
  );
}

export function AgentStatusTracker({ status, isLoading }: AgentStatusTrackerProps) {
  const agentStatusMap = new Map(status?.agents.map((a: AgentStatus) => [a.agent, a]));

  return (
    <Card className="border-primary/20 bg-card/50 backdrop-blur">
      <CardHeader>
        <CardTitle>Agent Pipeline</CardTitle>
        <CardDescription>
          {status?.current_agent
            ? `Currently running: ${status.current_agent}`
            : isLoading
              ? 'Loading pipeline status...'
              : 'Waiting for project to start'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between gap-4">
          {AGENT_ORDER.map((agent, index) => (
            <div key={agent.id} className="flex items-center">
              <AgentNode
                agent={agent}
                status={agentStatusMap.get(agent.id)}
                isActive={status?.current_agent === agent.id}
              />
              {index < AGENT_ORDER.length - 1 && (
                <div className="mx-4 h-0.5 w-8 bg-border" />
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
