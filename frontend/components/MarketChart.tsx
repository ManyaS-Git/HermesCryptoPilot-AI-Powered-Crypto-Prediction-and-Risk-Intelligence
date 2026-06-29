'use client';

import { useMarkets } from '../hooks/useApiHooks';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export default function MarketChart({ asset }: { asset: string }) {
  const { data: markets, isLoading, isError } = useMarkets(asset);

  if (isLoading) return <CardWrapper title={`${asset} Market Odds`}><div className="animate-pulse h-48 bg-zinc-800 rounded"></div></CardWrapper>;
  if (isError) return <CardWrapper title={`${asset} Market Odds`}><div className="text-red-500 text-sm">Error loading market odds</div></CardWrapper>;

  if (!markets || markets.length === 0) {
    return (
      <CardWrapper title={`${asset} Market Odds`}>
        <div className="text-zinc-500 text-sm flex h-48 items-center justify-center">
          No market data available yet.
        </div>
      </CardWrapper>
    );
  }

  // Format data for Recharts
  const chartData = markets.map(m => ({
    name: m.source,
    probability: Number((m.implied_probability * 100).toFixed(1))
  }));

  return (
    <CardWrapper title={`${asset} Market Odds (Implied %)`}>
      <div className="h-48 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#3f3f46" />
            <XAxis type="number" domain={[0, 100]} hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa', fontSize: 12 }} />
            <Tooltip 
              cursor={{ fill: '#27272a' }}
              contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px', color: '#f4f4f5' }}
              formatter={(value: any) => [`${value}%`, 'Implied Probability']}
            />
            <Bar dataKey="probability" radius={[0, 4, 4, 0]} barSize={24}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.name === 'Polymarket' ? '#3b82f6' : '#8b5cf6'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </CardWrapper>
  );
}

function CardWrapper({ title, children }: { title: string, children: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 shadow-sm">
      <h3 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">{title}</h3>
      {children}
    </div>
  );
}
