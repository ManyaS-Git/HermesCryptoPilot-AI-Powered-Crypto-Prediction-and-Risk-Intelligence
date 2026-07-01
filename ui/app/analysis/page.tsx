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
import { fetchMarketAnalysis } from '@/lib/api';
import { MarketAnalysis } from '@/lib/types';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from 'recharts';
import { TrendingUp, Gauge, AlertCircle, CheckCircle } from 'lucide-react';

const SYMBOLS = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA'];

export default function AnalysisPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC');
  const [analysis, setAnalysis] = useState<MarketAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadAnalysis = async () => {
      setLoading(true);
      try {
        const data = await fetchMarketAnalysis(selectedSymbol);
        setAnalysis(data);
      } catch (error) {
        console.error('[v0] Error loading analysis:', error);
      } finally {
        setLoading(false);
      }
    };
    loadAnalysis();
  }, [selectedSymbol]);

  const chartData = [
    { name: 'Technical', value: 75 },
    { name: 'Sentiment', value: 65 },
    { name: 'Volume', value: 80 },
    { name: 'Momentum', value: 70 },
    { name: 'Trend', value: 85 },
  ];

  const priceData = [
    { time: '00:00', price: 43200 },
    { time: '04:00', price: 43500 },
    { time: '08:00', price: 42800 },
    { time: '12:00', price: 44100 },
    { time: '16:00', price: 43900 },
    { time: '20:00', price: 44500 },
    { time: '24:00', price: 45200 },
  ];

  const volatilityData = [
    { time: 'Mon', vol: 2.1 },
    { time: 'Tue', vol: 2.3 },
    { time: 'Wed', vol: 1.9 },
    { time: 'Thu', vol: 2.5 },
    { time: 'Fri', vol: 2.2 },
    { time: 'Sat', vol: 2.8 },
    { time: 'Sun', vol: 2.4 },
  ];

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
                  ${analysis.current_price.toFixed(2)}
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
              <CardTitle>Price Movement (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={priceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                  <XAxis dataKey="time" stroke="#6b7280" />
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
                    dataKey="price"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Analysis Radar */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Technical Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={chartData}>
                    <PolarGrid stroke="#2d2d2d" />
                    <PolarAngleAxis dataKey="name" stroke="#6b7280" />
                    <PolarRadiusAxis stroke="#6b7280" />
                    <Radar
                      name="Analysis"
                      dataKey="value"
                      stroke="#8b5cf6"
                      fill="#8b5cf6"
                      fillOpacity={0.3}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Volatility */}
            <Card className="border-border">
              <CardHeader>
                <CardTitle>Weekly Volatility</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={volatilityData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                    <XAxis dataKey="time" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1a1a1a',
                        border: '1px solid #2d2d2d',
                        borderRadius: '0.5rem',
                      }}
                    />
                    <Bar dataKey="vol" fill="#06b6d4" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Signals */}
          <Card className="border-border">
            <CardHeader>
              <CardTitle>Technical Signals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                    <p className="font-semibold text-foreground">Confidence</p>
                  </div>
                  <p className="text-lg text-accent">
                    {(analysis.sentiment_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
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
