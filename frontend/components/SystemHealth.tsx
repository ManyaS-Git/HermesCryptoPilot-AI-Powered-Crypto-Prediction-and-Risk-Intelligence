'use client';

import { useHealth } from '../hooks/useApiHooks';
import { Activity, Database, Server, CheckCircle2, XCircle } from 'lucide-react';

export default function SystemHealth() {
  const { data: health, isLoading, isError } = useHealth();

  if (isLoading) return <div className="text-zinc-500 text-sm animate-pulse">Loading system health...</div>;
  
  // If there's an error, assume backend is down
  if (isError || !health) {
    return (
      <div className="flex items-center gap-2 text-sm font-medium text-red-500">
        <XCircle className="w-4 h-4" />
        Backend Disconnected ❌
      </div>
    );
  }

  const { services } = health;

  return (
    <div className="flex items-center gap-4 text-xs font-medium text-zinc-400 bg-zinc-900/50 p-2 rounded-lg border border-zinc-800">
      <div className="flex items-center gap-2 text-zinc-200">
        <Server className="w-4 h-4" />
        <span>Backend Connected ✅</span>
      </div>
      <div className="w-px h-4 bg-zinc-700"></div>
      
      <ServiceStatus name="SQLite" status={services?.sqlite} icon={<Database className="w-3 h-3" />} />
      <ServiceStatus name="OpenRouter" status={services?.openrouter} />
      <ServiceStatus name="Binance" status={services?.binance} />
      <ServiceStatus name="Polymarket" status={services?.polymarket} />
    </div>
  );
}

function ServiceStatus({ name, status, icon }: { name: string, status?: string, icon?: React.ReactNode }) {
  const isOnline = status === 'online';
  return (
    <div className="flex items-center gap-1.5">
      {icon}
      <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
      <span>{name}</span>
    </div>
  );
}
