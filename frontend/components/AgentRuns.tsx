'use client';

import { useAgentRuns } from '../hooks/useApiHooks';
import { Terminal, CheckCircle2, Clock } from 'lucide-react';

export default function AgentRuns() {
  const { data: runs, isLoading, isError } = useAgentRuns();

  if (isLoading) return <CardWrapper><div className="animate-pulse h-48 bg-zinc-800 rounded"></div></CardWrapper>;
  if (isError) return <CardWrapper><div className="text-red-500 text-sm">Error loading agent runs</div></CardWrapper>;

  if (!runs || runs.length === 0) {
    return (
      <CardWrapper>
        <div className="text-zinc-500 text-sm flex h-48 items-center justify-center">
          No agent activity recorded.
        </div>
      </CardWrapper>
    );
  }

  return (
    <CardWrapper>
      <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2 mb-4">
        <Terminal className="w-4 h-4" />
        Recent Agent Activity
      </h3>
      
      <div className="space-y-3 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
        {runs.map((run, i) => {
          const date = new Date(run.timestamp);
          return (
            <div key={i} className="flex gap-3 text-sm bg-zinc-950 p-3 rounded-lg border border-zinc-800/50">
              <div className="mt-0.5">
                {run.status === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                ) : (
                  <Clock className="w-4 h-4 text-zinc-500" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-semibold text-zinc-200">{run.agent_name}</span>
                  <span className="text-xs text-zinc-500 font-mono">{date.toLocaleTimeString()}</span>
                </div>
                <div className="text-zinc-400">{run.message}</div>
                {run.execution_time_ms && (
                  <div className="text-xs text-zinc-600 mt-1">Duration: {run.execution_time_ms}ms</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </CardWrapper>
  );
}

function CardWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-sm">
      {children}
    </div>
  );
}
