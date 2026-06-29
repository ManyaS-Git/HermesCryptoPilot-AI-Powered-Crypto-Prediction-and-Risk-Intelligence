'use client';

import { useLatestPredictions } from '../hooks/useApiHooks';
import { ArrowUpCircle, ArrowDownCircle, Clock } from 'lucide-react';
import { cn } from '../lib/utils';

export default function PredictionCard({ asset }: { asset: string }) {
  const { data: predictions, isLoading, isError } = useLatestPredictions();

  if (isLoading) return <CardWrapper><div className="animate-pulse flex space-x-4"><div className="h-10 bg-zinc-800 rounded w-full"></div></div></CardWrapper>;
  if (isError) return <CardWrapper><div className="text-red-500 text-sm">Error loading prediction</div></CardWrapper>;

  const prediction = predictions?.find(p => p.asset === asset);

  if (!prediction) {
    return (
      <CardWrapper>
        <div className="text-zinc-500 text-sm text-center py-4">
          No predictions yet. Click &apos;▶ Run Prediction&apos; to generate your first forecast for {asset}.
        </div>
      </CardWrapper>
    );
  }

  const isUp = prediction.signal_direction === 'UP';
  const confidence = (prediction.fused_probability * 100).toFixed(1);
  const date = new Date(prediction.timestamp);

  return (
    <CardWrapper>
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-zinc-100">{asset} Prediction</h3>
        <div className="flex items-center gap-1 text-xs text-zinc-500">
          <Clock className="w-3 h-3" />
          Updated: {date.toLocaleTimeString()} UTC
        </div>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex flex-col items-center">
          {isUp ? (
            <ArrowUpCircle className="w-12 h-12 text-emerald-500 mb-2" />
          ) : (
            <ArrowDownCircle className="w-12 h-12 text-red-500 mb-2" />
          )}
          <span className={cn("text-2xl font-bold", isUp ? "text-emerald-500" : "text-red-500")}>
            {isUp ? 'UP' : 'DOWN'}
          </span>
        </div>

        <div className="flex-1">
          <div className="text-sm text-zinc-400 mb-2">Confidence Gauge</div>
          {/* Simple Radial-like progress bar since we aren't using a heavy charting lib for this small gauge */}
          <div className="relative w-full h-4 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className={cn("absolute top-0 left-0 h-full transition-all duration-1000", isUp ? "bg-emerald-500" : "bg-red-500")}
              style={{ width: `${confidence}%` }}
            />
          </div>
          <div className="mt-2 text-right font-mono text-sm text-zinc-300">{confidence}%</div>
        </div>
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
