'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { fetchPortfolio } from '@/lib/api';
import { Portfolio, Position } from '@/lib/types';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Wallet } from 'lucide-react';

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPortfolio = async () => {
      setLoading(true);
      try {
        const data = await fetchPortfolio();
        setPortfolio(data);
      } catch (error) {
        console.error('[v0] Error loading portfolio:', error);
      } finally {
        setLoading(false);
      }
    };
    loadPortfolio();
  }, []);

  const performanceData = [
    { date: 'Mon', value: 50000 },
    { date: 'Tue', value: 52000 },
    { date: 'Wed', value: 48000 },
    { date: 'Thu', value: 55000 },
    { date: 'Fri', value: 58000 },
    { date: 'Sat', value: 61000 },
    { date: 'Sun', value: 64000 },
  ];

  const pieData =
    portfolio?.positions.map((p) => ({
      name: p.asset,
      value: p.value,
    })) || [];

  const COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

  if (loading) {
    return (
      <div className="p-8">
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-card animate-pulse rounded-lg border border-border" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-foreground">Portfolio</h1>
        <p className="text-muted-foreground mt-1">
          Your investment positions and performance
        </p>
      </div>

      {portfolio ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-border">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">Total Value</p>
                  <Wallet className="w-4 h-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-foreground">
                  ${portfolio.total_value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Cash available: ${portfolio.cash_balance.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">Gain/Loss</p>
                  {portfolio.total_pnl >= 0 ? (
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-red-400" />
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p
                  className={`text-3xl font-bold ${
                    portfolio.total_pnl >= 0
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  {portfolio.total_pnl >= 0 ? '+' : ''}$
                  {portfolio.total_pnl.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>
                <p
                  className={`text-sm mt-2 ${
                    portfolio.total_pnl_pct >= 0
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  {portfolio.total_pnl_pct >= 0 ? '+' : ''}
                  {portfolio.total_pnl_pct.toFixed(2)}%
                </p>
              </CardContent>
            </Card>

            <Card className="border-border">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-muted-foreground">Positions</p>
                  <DollarSign className="w-4 h-4 text-primary" />
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-foreground">
                  {portfolio.positions.length}
                </p>
                <p className="text-sm text-muted-foreground mt-2">
                  Active holdings
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Chart */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>7-Day Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                    <XAxis dataKey="date" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a1a',
                        border: '1px solid #2d2d2d',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Portfolio Allocation */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Portfolio Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                {pieData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={(entry) => entry.name}
                        outerRadius={80}
                        fill="#8b5cf6"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-64 flex items-center justify-center text-muted-foreground">
                    No positions to display
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Positions Table */}
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Your Positions</CardTitle>
            </CardHeader>
            <CardContent>
              {portfolio.positions.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 text-muted-foreground font-medium">
                          Asset
                        </th>
                        <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                          Quantity
                        </th>
                        <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                          Entry Price
                        </th>
                        <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                          Current Price
                        </th>
                        <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                          Value
                        </th>
                        <th className="text-right py-3 px-4 text-muted-foreground font-medium">
                          Gain/Loss
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.positions.map((position) => (
                        <tr
                          key={position.id}
                          className="border-b border-border hover:bg-card/50 transition-colors"
                        >
                          <td className="py-3 px-4">
                            <span className="font-semibold text-foreground">
                              {position.asset}
                            </span>
                          </td>
                          <td className="text-right py-3 px-4 text-foreground">
                            {position.quantity.toLocaleString()}
                          </td>
                          <td className="text-right py-3 px-4 text-foreground">
                            ${position.entry_price.toFixed(2)}
                          </td>
                          <td className="text-right py-3 px-4 text-foreground">
                            ${position.current_price.toFixed(2)}
                          </td>
                          <td className="text-right py-3 px-4 text-foreground font-semibold">
                            ${position.value.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}
                          </td>
                          <td
                            className={`text-right py-3 px-4 font-semibold ${
                              position.unrealized_pnl_pct >= 0
                                ? 'text-green-400'
                                : 'text-red-400'
                            }`}
                          >
                            {position.unrealized_pnl_pct >= 0 ? '+' : ''}
                            {position.unrealized_pnl_pct.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No positions yet
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="text-center py-16 bg-card rounded-lg border border-border">
          <Wallet className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">Unable to load portfolio</p>
        </div>
      )}
    </div>
  );
}
