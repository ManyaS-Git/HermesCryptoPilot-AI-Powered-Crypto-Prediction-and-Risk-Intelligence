'use client';

import { usePredictionHistory } from '../hooks/useApiHooks';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../lib/utils';

export default function PredictionHistory({ asset }: { asset: string }) {
  const { data: history, isLoading, isError } = usePredictionHistory(asset);

  if (isLoading) return <CardWrapper title={`${asset} History`}><div className="animate-pulse h-16 bg-zinc-800 rounded"></div></CardWrapper>;
  if (isError) return <CardWrapper title={`${asset} History`}><div className="text-red-500 text-sm">Error loading history</div></CardWrapper>;

  if (!history || history.length === 0) {
    return (
      <CardWrapper title={`${asset} History`}>
        <div className="text-zinc-500 text-sm py-2">No history yet.</div>
      </CardWrapper>
    );
  }

  return (
    <CardWrapper title={`${asset} History`}>
      <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-2 custom-scrollbar">
        {history.map((pred, i) => {
          const isUp = pred.signal_direction === 'UP';
          return (
            <div 
              key={i} 
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-md shrink-0 border",
                isUp ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-500" : "bg-red-500/10 border-red-500/20 text-red-500"
              )}
              title={`${isUp ? 'UP' : 'DOWN'} - ${(pred.fused_probability*100).toFixed(0)}%`}
            >
              {isUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            </div>
          );
        })}
      </div>
    </CardWrapper>
  );
}

function CardWrapper({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-sm h-full">
      <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">{title}</h3>
      {children}
    </div>
  );
}
