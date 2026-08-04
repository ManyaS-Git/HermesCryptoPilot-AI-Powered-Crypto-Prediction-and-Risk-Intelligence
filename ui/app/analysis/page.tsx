'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { fetchMarketAnalysis, fetchKlines } from '@/lib/api';
import { MarketAnalysis, Candle } from '@/lib/types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { TrendingUp, Gauge, AlertCircle, CheckCircle } from 'lucide-react';

const SYMBOLS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA'];

export default function AnalysisPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');
  const [analysis, setAnalysis] = useState<MarketAnalysis | null>(null);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadAnalysis = async () => {
      setLoading(true);
      try {
        const [data, klines] = await Promise.all([
          fetchMarketAnalysis(selectedSymbol),
          fetchKlines(selectedSymbol, '1h', 168).catch(() => []),
        ]);
        setAnalysis(data);
        setCandles(klines);
      } catch (error) {
        console.error('[Hermes] Error loading analysis:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAnalysis();
  }, [selectedSymbol]);

  const priceData = candles.map((c) => ({
    time: new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    price: c.close,
    volume: c.volume,
  }));

  const indicatorData = analysis
    ? Object.entries(analysis.indicators).map(([name, value]) => ({
        name: name.replace('_', ' '),
        value: Math.round((value as number) * 100),
      }))
    : [];

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-foreground">Market Analysis</h1>
            <p className="text-muted-foreground mt-1">
              Technical analysis and market insights
            </p>
          </div>
          <div className="w-40">
            <Select value={selectedSymbol} onValueChange={(val) => val && setSelectedSymbol(val)}>
              <SelectTrigger className="bg-card border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SYMBOLS.map((symbol) => (
                  <SelectItem key={symbol} value={symbol}>
                    {symbol}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-64 bg-card animate-pulse rounded-lg border border-border" />
          ))}
        </div>
      ) : analysis ? (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-border">
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-2">Current Price</p>
                <p className="text-3xl font-bold text-foreground">
                  ${analysis.current_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
              </CardContent>
            </Card>
            <Card className="border-border">
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-2">Volatility</p>
                <p className="text-3xl font-bold text-accent">
                  {(analysis.volatility * 100).toFixed(2)}%
                </p>
              </CardContent>
            </Card>
            <Card className="border-border">
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-2">Sentiment</p>
                <div className="flex items-center gap-2">
                  <p className="text-3xl font-bold text-primary">
                    {(analysis.sentiment_score * 100).toFixed(0)}%
                  </p>
                  {analysis.sentiment_score > 0.6 ? (
                    <CheckCircle className="w-6 h-6 text-green-400" />
                  ) : (
                    <AlertCircle className="w-6 h-6 text-red-400" />
                  )}
                </div>
              </CardContent>
            </Card>
            <Card className="border-border">
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground mb-2">Trend</p>
                <div className="flex items-center gap-2">
                  <p className="text-lg font-bold text-foreground capitalize">
                    {analysis.trend}
                  </p>
                  <TrendingUp className="w-5 h-5 text-primary" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Price Chart */}
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Price Movement ({selectedSymbol}/USDT)</CardTitle>
            </CardHeader>
            <CardContent>
              {priceData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={priceData}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} />
                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                    <XAxis dataKey="time" stroke="#6b7280" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a1a',
                        border: '1px solid #2d2d2d',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="price"
                      stroke="#8b5cf6"
                      strokeWidth={2}
                      fill="url(#priceGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-64 flex items-center justify-center text-muted-foreground">
                  No price data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Indicator Radar */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Signals */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Technical Signals</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-card rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Gauge className="w-5 h-5 text-primary" />
                      <p className="font-semibold text-foreground">Current Signal</p>
                    </div>
                    <p className="text-lg text-accent">{analysis.technical_signal}</p>
                  </div>
                  <div className="p-4 bg-card rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      <p className="font-semibold text-foreground">Trend Direction</p>
                    </div>
                    <p className="text-lg capitalize text-primary">{analysis.trend}</p>
                  </div>
                  <div className="p-4 bg-card rounded-lg border border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-primary" />
                      <p className="font-semibold text-foreground">Regime</p>
                    </div>
                    <p className="text-lg text-accent capitalize">{analysis.regime.replace('_', ' ')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Indicator Bars */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Indicator Scores</CardTitle>
              </CardHeader>
              <CardContent>
                {indicatorData.length > 0 ? (
                  <div className="space-y-3">
                    {indicatorData.map((item) => (
                      <div key={item.name} className="flex items-center gap-3">
                        <span className="w-28 text-sm text-muted-foreground capitalize">{item.name}</span>
                        <div className="flex-1 bg-border rounded-full h-3">
                          <div
                            className="bg-primary h-3 rounded-full transition-all"
                            style={{ width: `${Math.min(100, Math.max(0, item.value))}%` }}
                          />
                        </div>
                        <span className="w-12 text-right text-sm font-medium text-foreground">{item.value}%</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-muted-foreground">
                    No indicator data
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-card rounded-lg border border-border">
          <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground">Unable to load analysis</p>
        </div>
      )}
    </div>
  );
}
