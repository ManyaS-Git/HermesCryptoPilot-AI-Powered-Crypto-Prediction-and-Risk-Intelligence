'use client';

import { Prediction } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react';

interface PredictionCardProps {
  prediction: Prediction;
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  const isUp = prediction.direction === 'UP';
  const isPositive = prediction.return_pct >= 0;

  const statusColors = {
    active: 'bg-blue-500/20 text-blue-400',
    completed: isPositive
      ? 'bg-green-500/20 text-green-400'
      : 'bg-red-500/20 text-red-400',
    failed: 'bg-red-500/20 text-red-400',
  };

  return (
    <Card className="border-border hover:border-accent/50 transition-colors">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {isUp ? (
              <TrendingUp className="w-5 h-5 text-green-400" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-400" />
            )}
            <div>
              <CardTitle className="text-lg">{prediction.symbol}</CardTitle>
              <p className="text-xs text-muted-foreground">{prediction.asset}</p>
            </div>
          </div>
          <Badge className={statusColors[prediction.status]}>
            {prediction.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">Entry Price</p>
            <p className="text-lg font-semibold">${prediction.price.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Target</p>
            <p className="text-lg font-semibold text-primary">
              ${prediction.target_price.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Confidence</p>
            <p className="text-lg font-semibold">{(prediction.confidence * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Return</p>
            <p className={`text-lg font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
              {isPositive ? '+' : ''}{prediction.return_pct.toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="border-t border-border pt-3">
          <p className="text-xs text-muted-foreground">Agent Consensus</p>
          <div className="flex items-center gap-2 mt-1">
            <div className="flex-1 bg-border rounded-full h-2">
              <div
                className="bg-accent h-2 rounded-full transition-all"
                style={{ width: `${prediction.agents_consensus * 100}%` }}
              />
            </div>
            <span className="text-sm font-medium">{(prediction.agents_consensus * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="text-xs text-muted-foreground">
          Updated: {new Date(prediction.predicted_time).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  );
}
