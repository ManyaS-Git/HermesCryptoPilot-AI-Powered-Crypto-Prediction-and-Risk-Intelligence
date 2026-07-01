'use client';

import { useEffect, useState } from 'react';
import { StatCard } from '@/components/stat-card';
import { PredictionCard } from '@/components/prediction-card';
import { AgentStatus } from '@/components/agent-status';
import { Button } from '@/components/ui/button';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Zap,
  AlertCircle,
  RefreshCw,
  Plus,
} from 'lucide-react';
import {
  fetchDashboardStats,
  fetchPredictions,
  fetchAgents,
  createPrediction,
} from '@/lib/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  DashboardStats,
  Prediction,
  Agent,
} from '@/lib/types';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPredictionModalOpen, setIsPredictionModalOpen] = useState(false);
  const [newAsset, setNewAsset] = useState('');
  const [submittingPrediction, setSubmittingPrediction] = useState(false);
  const [predictionResult, setPredictionResult] = useState<Prediction | null>(null);

  const handleCreatePrediction = async () => {
    if (!newAsset) return;
    setSubmittingPrediction(true);
    try {
      const result = await createPrediction({
        asset: newAsset.toUpperCase(),
        direction: 'UP',
        confidence: 0,
        price: 0,
      });
      setPredictionResult(result);
      
      const [statsData, predictionsData, agentsData] = await Promise.all([
        fetchDashboardStats(),
        fetchPredictions(),
        fetchAgents(),
      ]);
      setStats(statsData);
      setPredictions(predictionsData.slice(0, 3));
      setAgents(agentsData.slice(0, 3));
    } catch (error) {
      console.error('Error creating prediction:', error);
    } finally {
      setSubmittingPrediction(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [statsData, predictionsData, agentsData] = await Promise.all([
          fetchDashboardStats(),
          fetchPredictions(),
          fetchAgents(),
        ]);
        setStats(statsData);
        setPredictions(predictionsData.slice(0, 3));
        setAgents(agentsData.slice(0, 3));
      } catch (error) {
        console.error('[v0] Error loading dashboard:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time crypto prediction & agent orchestration
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            size="lg"
            className="gap-2"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
          <Dialog 
            open={isPredictionModalOpen} 
            onOpenChange={(open) => {
              setIsPredictionModalOpen(open);
              if (!open) {
                setTimeout(() => {
                  setPredictionResult(null);
                  setNewAsset('');
                }, 200);
              }
            }}
          >
            <DialogTrigger
              render={
                <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
                  <Plus className="w-4 h-4" />
                  New Prediction
                </Button>
              }
            />
            <DialogContent className="sm:max-w-[425px]">
              {predictionResult ? (
                <>
                  <DialogHeader>
                    <DialogTitle>Prediction Generated</DialogTitle>
                    <DialogDescription>
                      The AI swarm has successfully analyzed {predictionResult.asset}.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-6 flex flex-col items-center justify-center space-y-4">
                    <div className="text-5xl font-bold flex items-center gap-3">
                      {predictionResult.direction === 'UP' ? (
                        <TrendingUp className="text-green-500 w-12 h-12" />
                      ) : (
                        <TrendingDown className="text-red-500 w-12 h-12" />
                      )}
                      <span className={predictionResult.direction === 'UP' ? 'text-green-500' : 'text-red-500'}>
                        {predictionResult.direction}
                      </span>
                    </div>
                    <div className="text-muted-foreground text-lg">
                      Confidence: {predictionResult.confidence.toFixed(1)}%
                    </div>
                    {predictionResult.target_price > 0 && (
                      <div className="text-sm font-medium">
                        Target: ${predictionResult.target_price.toLocaleString()} | Stop: ${predictionResult.stop_loss.toLocaleString()}
                      </div>
                    )}
                  </div>
                  <DialogFooter>
                    <Button 
                      type="button" 
                      onClick={() => { 
                        setIsPredictionModalOpen(false); 
                        setTimeout(() => {
                          setPredictionResult(null); 
                          setNewAsset(''); 
                        }, 200);
                      }}
                    >
                      Close
                    </Button>
                  </DialogFooter>
                </>
              ) : (
                <>
                  <DialogHeader>
                    <DialogTitle>Start New Prediction</DialogTitle>
                    <DialogDescription>
                      Enter the cryptocurrency symbol (e.g. BTC) to trigger the agent swarm.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="asset" className="text-right text-foreground">
                        Asset
                      </Label>
                      <Input
                        id="asset"
                        value={newAsset}
                        onChange={(e) => setNewAsset(e.target.value)}
                        placeholder="BTC"
                        className="col-span-3 bg-card text-foreground"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" disabled={submittingPrediction} onClick={handleCreatePrediction}>
                      {submittingPrediction ? "Starting..." : "Run Agents"}
                    </Button>
                  </DialogFooter>
                </>
              )}
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Predictions"
          value={stats?.total_predictions || 0}
          icon={Target}
          color="primary"
        />
        <StatCard
          label="Active Predictions"
          value={stats?.active_predictions || 0}
          icon={TrendingUp}
          color="accent"
        />
        <StatCard
          label="Success Rate"
          value={`${(stats?.success_rate || 0).toFixed(1)}%`}
          icon={Zap}
          color="success"
          change={stats?.success_rate}
        />
        <StatCard
          label="Total Return"
          value={`${(stats?.total_return || 0).toFixed(2)}%`}
          icon={AlertCircle}
          color={stats?.total_return && stats.total_return >= 0 ? 'success' : 'destructive'}
          trend={stats?.total_return && stats.total_return >= 0 ? 'up' : 'down'}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Predictions */}
        <div className="lg:col-span-2">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-1">
              Recent Predictions
            </h2>
            <p className="text-sm text-muted-foreground">
              Latest market analysis and predictions
            </p>
          </div>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-card animate-pulse rounded-lg border border-border" />
              ))}
            </div>
          ) : predictions.length > 0 ? (
            <div className="space-y-4">
              {predictions.map((prediction) => (
                <PredictionCard key={prediction.id} prediction={prediction} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-card rounded-lg border border-border">
              <Target className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">No predictions yet</p>
            </div>
          )}
        </div>

        {/* Agents */}
        <div>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-1">
              Active Agents
            </h2>
            <p className="text-sm text-muted-foreground">
              Agent status & performance
            </p>
          </div>
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-32 bg-card animate-pulse rounded-lg border border-border" />
              ))}
            </div>
          ) : agents.length > 0 ? (
            <div className="space-y-4">
              {agents.map((agent) => (
                <AgentStatus key={agent.id} agent={agent} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 bg-card rounded-lg border border-border">
              <Zap className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">No agents active</p>
            </div>
          )}
        </div>
      </div>

      {/* Risk Alert */}
      {stats && stats.risk_score > 0.7 && (
        <div className="mt-8 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-400">High Risk Alert</p>
            <p className="text-sm text-red-300 mt-1">
              Current risk score is {(stats.risk_score * 100).toFixed(1)}%. Consider adjusting your positions.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
