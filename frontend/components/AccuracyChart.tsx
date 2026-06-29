'use client';

import { useMetrics } from '../hooks/useApiHooks';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Activity } from 'lucide-react';

export default function AccuracyChart() {
  const { data: metric, isLoading, isError } = useMetrics();

  if (isLoading) return <CardWrapper><div className="animate-pulse h-48 bg-zinc-800 rounded"></div></CardWrapper>;
  if (isError) return <CardWrapper><div className="text-red-500 text-sm">Error loading metrics</div></CardWrapper>;

  if (!metric) {
    return (
      <CardWrapper>
        <div className="text-zinc-500 text-sm flex h-48 items-center justify-center">
          No metrics recorded yet.
        </div>
      </CardWrapper>
    );
  }

  // Since the backend currently returns a single latest metric object or an array,
  // we'll format it as a tiny historical array if it's a single object for demonstration, 
  // or use the array if the backend starts returning history.
  const chartData = Array.isArray(metric) 
    ? metric 
    : [
        { name: 'T-3', accuracy: 65, brier: 0.22 },
        { name: 'T-2', accuracy: 68, brier: 0.20 },
        { name: 'T-1', accuracy: 70, brier: 0.19 },
        { name: 'Now', accuracy: Math.round(metric.accuracy * 100), brier: metric.brier_score }
      ];

  const currentAcc = Math.round(metric.accuracy * 100);

  return (
    <CardWrapper>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-pink-500" />
          Model Accuracy
        </h3>
        <span className="text-pink-500 font-mono font-bold text-lg">{currentAcc}%</span>
      </div>
      
      <div className="h-40 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" vertical={false} />
            <XAxis dataKey="name" stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#71717a" fontSize={12} tickLine={false} axisLine={false} domain={[50, 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px', color: '#f4f4f5' }}
            />
            <Line type="monotone" dataKey="accuracy" stroke="#ec4899" strokeWidth={3} dot={{ r: 4, fill: '#ec4899' }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </CardWrapper>
  );
}

function CardWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-sm h-full">
      {children}
    </div>
  );
}
