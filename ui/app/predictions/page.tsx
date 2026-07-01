'use client';

import { useEffect, useState } from 'react';
import { PredictionCard } from '@/components/prediction-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { fetchPredictions } from '@/lib/api';
import { Prediction } from '@/lib/types';
import { Plus, Search } from 'lucide-react';

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [filteredPredictions, setFilteredPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    const loadPredictions = async () => {
      setLoading(true);
      try {
        const data = await fetchPredictions();
        setPredictions(data);
        setFilteredPredictions(data);
      } catch (error) {
        console.error('[v0] Error loading predictions:', error);
      } finally {
        setLoading(false);
      }
    };
    loadPredictions();
  }, []);

  useEffect(() => {
    let filtered = predictions;

    if (searchTerm) {
      filtered = filtered.filter(
        (p) =>
          p.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.asset.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((p) => p.status === statusFilter);
    }

    setFilteredPredictions(filtered);
  }, [searchTerm, statusFilter, predictions]);

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground">Predictions</h1>
          <p className="text-muted-foreground mt-1">
            View all crypto price predictions
          </p>
        </div>
        <Button size="lg" className="gap-2 bg-primary hover:bg-primary/90">
          <Plus className="w-4 h-4" />
          New Prediction
        </Button>
      </div>

      {/* Filters */}
      <div className="mb-8 flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
          <Input
            placeholder="Search by symbol or asset..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-card border-border"
          />
        </div>
        <Select value={statusFilter} onValueChange={(val) => val && setStatusFilter(val)}>
          <SelectTrigger className="w-40 bg-card border-border">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="failed">Failed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Predictions Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-64 bg-card animate-pulse rounded-lg border border-border" />
          ))}
        </div>
      ) : filteredPredictions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredPredictions.map((prediction) => (
            <PredictionCard key={prediction.id} prediction={prediction} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-card rounded-lg border border-border">
          <Search className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">
            {predictions.length === 0
              ? 'No predictions yet'
              : 'No predictions match your filters'}
          </p>
        </div>
      )}

      {/* Summary */}
      {predictions.length > 0 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 bg-card rounded-lg border border-border">
            <p className="text-sm text-muted-foreground">Total</p>
            <p className="text-2xl font-bold text-foreground">{predictions.length}</p>
          </div>
          <div className="p-4 bg-card rounded-lg border border-border">
            <p className="text-sm text-muted-foreground">Active</p>
            <p className="text-2xl font-bold text-accent">
              {predictions.filter((p) => p.status === 'active').length}
            </p>
          </div>
          <div className="p-4 bg-card rounded-lg border border-border">
            <p className="text-sm text-muted-foreground">Completed</p>
            <p className="text-2xl font-bold text-green-400">
              {predictions.filter((p) => p.status === 'completed').length}
            </p>
          </div>
          <div className="p-4 bg-card rounded-lg border border-border">
            <p className="text-sm text-muted-foreground">Failed</p>
            <p className="text-2xl font-bold text-red-400">
              {predictions.filter((p) => p.status === 'failed').length}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
