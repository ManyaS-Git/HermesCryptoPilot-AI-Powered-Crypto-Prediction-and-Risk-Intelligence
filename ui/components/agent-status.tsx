'use client';

import { Agent } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Zap, Pause } from 'lucide-react';

interface AgentStatusProps {
  agent: Agent;
}

export function AgentStatus({ agent }: AgentStatusProps) {
  const statusIcons: Record<string, React.ReactNode> = {
    active: <Activity className="w-4 h-4 text-green-400" />,
    analyzing: <Zap className="w-4 h-4 text-yellow-400" />,
    idle: <Pause className="w-4 h-4 text-gray-400" />,
  };

  const statusColors: Record<string, string> = {
    active: 'bg-green-500/20 text-green-400',
    analyzing: 'bg-yellow-500/20 text-yellow-400',
    idle: 'bg-gray-500/20 text-gray-400',
  };

  return (
    <Card className="border-border">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              {statusIcons[agent.status] || statusIcons.idle}
              <h3 className="font-semibold text-foreground">{agent.name}</h3>
              <Badge className={statusColors[agent.status] || statusColors.idle}>{agent.status}</Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-3">{agent.role}</p>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-xs text-muted-foreground">Last Asset</p>
                <p className="text-lg font-semibold text-accent">{agent.last_asset || '—'}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Latency</p>
                <p className="text-lg font-semibold text-accent">
                  {agent.execution_time_ms != null ? `${Math.round(agent.execution_time_ms)}ms` : '—'}
                </p>
              </div>
            </div>
          </div>

          <div className="text-right">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
              {(agent.status === 'active' || agent.status === 'analyzing') ? (
                <div className="w-8 h-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
              ) : (
                <Pause className="w-6 h-6 text-muted-foreground" />
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
