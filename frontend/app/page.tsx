'use client';

import { useState } from 'react';
import SystemHealth from '@/components/SystemHealth';
import PredictionCard from '@/components/PredictionCard';
import MarketChart from '@/components/MarketChart';
import KellyCard from '@/components/KellyCard';
import AccuracyChart from '@/components/AccuracyChart';
import AgentRuns from '@/components/AgentRuns';
import PredictionHistory from '@/components/PredictionHistory';
import { useTriggerWorkflow } from '@/hooks/useApiHooks';
import { Play } from 'lucide-react';

export default function Dashboard() {
  const [selectedAsset, setSelectedAsset] = useState<string>('BTC');
  const triggerWorkflow = useTriggerWorkflow();

  const handleRunPrediction = () => {
    triggerWorkflow.mutate(selectedAsset);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 p-6 md:p-12 font-sans">
      
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Hermes Crypto Prediction</h1>
          <div className="flex items-center gap-4 text-sm text-zinc-400">
            <span className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              Live Refreshing every 5s
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <select 
            value={selectedAsset}
            onChange={(e) => setSelectedAsset(e.target.value)}
            className="bg-zinc-900 border border-zinc-800 text-zinc-200 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none"
          >
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
          </select>
          
          <button 
            onClick={handleRunPrediction}
            disabled={triggerWorkflow.isPending}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:cursor-not-allowed text-white font-medium py-2.5 px-5 rounded-lg transition-colors"
          >
            <Play className="w-4 h-4 fill-current" />
            {triggerWorkflow.isPending ? 'Running...' : 'Run Prediction'}
          </button>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Row 1: System Health */}
        <SystemHealth />
        
        {/* Row 2: Prediction Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PredictionCard asset="BTC" />
          <PredictionCard asset="ETH" />
        </div>

        {/* Row 3: History & Markets */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PredictionHistory asset={selectedAsset} />
          <MarketChart asset={selectedAsset} />
        </div>
        
        {/* Row 4: Kelly Size & Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <KellyCard asset={selectedAsset} />
          <AccuracyChart />
        </div>
        
        {/* Row 5: Agent Activity */}
        <div className="grid grid-cols-1 gap-6">
          <AgentRuns />
        </div>

      </div>
    </div>
  );
}
