'use client';

import { Card, CardContent } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  change?: number;
  trend?: 'up' | 'down';
  color?: 'primary' | 'accent' | 'success' | 'warning' | 'destructive';
}

export function StatCard({
  label,
  value,
  icon: Icon,
  change,
  trend,
  color = 'primary',
}: StatCardProps) {
  const colorClasses = {
    primary: 'text-primary',
    accent: 'text-accent',
    success: 'text-green-400',
    warning: 'text-yellow-400',
    destructive: 'text-red-400',
  };

  const bgClasses = {
    primary: 'bg-primary/10',
    accent: 'bg-accent/10',
    success: 'bg-green-400/10',
    warning: 'bg-yellow-400/10',
    destructive: 'bg-red-400/10',
  };

  const trendColor = trend === 'up' ? 'text-green-400' : 'text-red-400';

  return (
    <Card className="border-border">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-muted-foreground mb-2">{label}</p>
            <p className="text-3xl font-bold text-foreground">{value}</p>
            {change !== undefined && (
              <p className={`text-xs mt-2 ${trendColor}`}>
                {trend === 'up' ? '+' : ''}{change.toFixed(2)}%
              </p>
            )}
          </div>
          <div className={`${bgClasses[color]} p-3 rounded-lg`}>
            <Icon className={`w-6 h-6 ${colorClasses[color]}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
