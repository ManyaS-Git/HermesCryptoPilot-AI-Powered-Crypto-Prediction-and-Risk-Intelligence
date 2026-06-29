'use client';

import { useLatestPredictions } from '../hooks/useApiHooks';
import { Target } from 'lucide-react';

export default function KellyCard({ asset }: { asset: string }) {
  const { data: predictions, isLoading, isError } = useLatestPredictions();

  if (isLoading) return <CardWrapper><div className="animate-pulse h-20 bg-zinc-800 rounded"></div></CardWrapper>;
  if (isError) return <CardWrapper><div className="text-red-500 text-sm">Error loading Kelly size</div></CardWrapper>;

  const prediction = predictions?.find(p => p.asset === asset);

  if (!prediction) {
    return (
      <CardWrapper>
        <div className="text-zinc-500 text-sm">No Kelly recommendation available.</div>
      </CardWrapper>
    );
  }

  const kellyPct = (prediction.kelly_size * 100).toFixed(1);
  const maxPosition = 20.0; // From backend config
  const fillWidth = Math.min((prediction.kelly_size / (maxPosition/100)) * 100, 100);

  return (
    <CardWrapper>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
          <Target className="w-4 h-4 text-amber-500" />
          Kelly Position Size
        </h3>
        <span className="text-amber-500 font-mono font-bold">{kellyPct}%</span>
      </div>
      
      <div className="relative w-full h-3 bg-zinc-800 rounded-full overflow-hidden mb-2">
        <div 
          className="absolute top-0 left-0 h-full bg-amber-500 transition-all duration-1000"
          style={{ width: `${fillWidth}%` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-zinc-500">
        <span>0%</span>
        <span>Max Allowed ({maxPosition}%)</span>
      </div>
      
      {prediction.rationale && (
        <div className="mt-4 text-xs text-zinc-400 bg-zinc-950 p-2 rounded-md border border-zinc-800">
          <span className="font-semibold text-zinc-300">Rationale:</span> {prediction.rationale}
        </div>
      )}
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
