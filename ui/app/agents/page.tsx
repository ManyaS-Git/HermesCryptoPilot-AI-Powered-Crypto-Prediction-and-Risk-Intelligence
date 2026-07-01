'use client';

import { useEffect, useState } from 'react';
import { AgentStatus } from '@/components/agent-status';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { fetchAgents } from '@/lib/api';
import { Agent } from '@/lib/types';
import { Activity, Zap, Pause, TrendingUp } from 'lucide-react';

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAgents = async () => {
      setLoading(true);
      try {
        const data = await fetchAgents();
        setAgents(data);
      } catch (error) {
        console.error('[v0] Error loading agents:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAgents();
  }, []);

  const activeCount = agents.filter((a) => a.status === 'active').length;
  const analyzingCount = agents.filter((a) => a.status === 'analyzing').length;
  const totalAccuracy =
    agents.length > 0
      ? agents.reduce((sum, a) => sum + a.accuracy, 0) / agents.length
      : 0;
  const totalPredictions = agents.reduce((sum, a) => sum + a.predictions_made, 0);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground">Agents</h1>
        <p className="text-muted-foreground mt-1">
          Monitor AI agents and their performance
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Agents</p>
                <p className="text-3xl font-bold text-foreground">{agents.length}</p>
              </div>
              <Zap className="w-8 h-8 text-primary/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-3xl font-bold text-green-400">{activeCount}</p>
              </div>
              <Activity className="w-8 h-8 text-green-400/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Accuracy</p>
                <p className="text-3xl font-bold text-accent">
                  {(totalAccuracy * 100).toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-accent/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Predictions</p>
                <p className="text-3xl font-bold text-foreground">
                  {totalPredictions}
                </p>
              </div>
              <Pause className="w-8 h-8 text-primary/50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agents Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-40 bg-card animate-pulse rounded-lg border border-border" />
          ))}
        </div>
      ) : agents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent) => (
            <AgentStatus key={agent.id} agent={agent} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-card rounded-lg border border-border">
          <Zap className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">No agents available</p>
        </div>
      )}

      {/* Agent Details */}
      {agents.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-foreground mb-6">Agent Details</h2>
          <Card className="border-border">
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 text-muted-foreground font-medium">
                        Agent Name
                      </th>
                      <th className="text-left py-3 px-4 text-muted-foreground font-medium">
                        Role
                      </th>
                      <th className="text-center py-3 px-4 text-muted-foreground font-medium">
                        Status
                      </th>
                      <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                        Predictions
                      </th>
                      <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                        Accuracy
                      </th>
                      <th className="text-left py-3 px-4 text-muted-foreground font-medium">
                        Last Update
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents.map((agent) => {
                      const lastUpdate = new Date(agent.last_update);
                      const now = new Date();
                      const minutesAgo = Math.floor(
                        (now.getTime() - lastUpdate.getTime()) / 60000
                      );

                      return (
                        <tr
                          key={agent.id}
                          className="border-b border-border hover:bg-card/50 transition-colors"
                        >
                          <td className="py-3 px-4">
                            <span className="font-semibold text-foreground">
                              {agent.name}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-muted-foreground">
                            {agent.role}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span
                              className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                                agent.status === 'active'
                                  ? 'bg-green-500/20 text-green-400'
                                  : agent.status === 'analyzing'
                                  ? 'bg-yellow-500/20 text-yellow-400'
                                  : 'bg-gray-500/20 text-gray-400'
                              }`}
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-current" />
                              {agent.status}
                            </span>
                          </td>
                          <td className="text-right py-3 px-4 text-foreground">
                            {agent.predictions_made}
                          </td>
                          <td className="text-right py-3 px-4 text-accent font-semibold">
                            {(agent.accuracy * 100).toFixed(1)}%
                          </td>
                          <td className="py-3 px-4 text-muted-foreground text-xs">
                            {minutesAgo < 1 ? 'just now' : `${minutesAgo}m ago`}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
