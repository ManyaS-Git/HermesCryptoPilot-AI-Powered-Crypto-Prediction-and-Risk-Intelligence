/* ------------------------------------------------------------------ */
/*  API client — fetches from the Hermes FastAPI backend                */
/* ------------------------------------------------------------------ */

import type {
  Prediction,
  Agent,
  DashboardStats,
  AssetInfo,
  Ticker,
  Candle,
  FearGreedValue,
  MarketAnalysis,
  Portfolio,
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API ${res.status}: ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

/* ------------------------------------------------------------------ */
/*  Auth                                                               */
/* ------------------------------------------------------------------ */

export async function register(email: string, username: string, password: string) {
  return api<{ access_token: string; refresh_token: string }>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  });
}

export async function login(identifier: string, password: string) {
  return api<{ access_token: string; refresh_token: string }>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  });
}

/* ------------------------------------------------------------------ */
/*  Predictions                                                        */
/* ------------------------------------------------------------------ */

export async function fetchPredictions(): Promise<Prediction[]> {
  const rows = await api<Record<string, unknown>[]>('/api/v1/predictions');
  return rows.map(normalizePrediction);
}

export async function fetchPrediction(id: string): Promise<Prediction> {
  const row = await api<Record<string, unknown>>(`/api/v1/predictions/${id}`);
  return normalizePrediction(row);
}

export async function createPrediction(payload: {
  asset: string;
  interval?: string;
  horizon_bars?: number;
}) {
  return api<Record<string, unknown>>('/api/v1/predictions', {
    method: 'POST',
    body: JSON.stringify({
      asset: payload.asset,
      interval: payload.interval || '1h',
      horizon_bars: payload.horizon_bars || 1,
    }),
  });
}

function normalizePrediction(raw: Record<string, unknown>): Prediction {
  const asset = (raw.asset as string) || 'BTC';
  return {
    id: (raw.id as string) || '',
    asset,
    symbol: `${asset}USDT`,
    interval: (raw.interval as string) || '1h',
    direction: (raw.direction as 'UP' | 'DOWN') || 'UP',
    status: (raw.status as string) === 'completed' ? 'completed' : (raw.status as string) === 'failed' ? 'failed' : 'active',
    probability: Number(raw.probability) || 0.5,
    expected_return: Number(raw.expected_return) || 0,
    expected_price: raw.expected_price != null ? Number(raw.expected_price) : null,
    target_price: raw.target_price != null ? Number(raw.target_price) : null,
    stop_loss: raw.stop_loss != null ? Number(raw.stop_loss) : null,
    confidence_lower: raw.confidence_lower != null ? Number(raw.confidence_lower) : null,
    confidence_upper: raw.confidence_upper != null ? Number(raw.confidence_upper) : null,
    model_ensemble: (raw.model_ensemble as string) || '',
    model_weights: (raw.model_weights as Record<string, number>) || {},
    kelly_size: Number(raw.kelly_size) || 0,
    risk_score: Number(raw.risk_score) || 0,
    var_95: Number(raw.var_95) || 0,
    sharpe_ratio: Number(raw.sharpe_ratio) || 0,
    sortino_ratio: Number(raw.sortino_ratio) || 0,
    max_drawdown: Number(raw.max_drawdown) || 0,
    fused_probability: Number(raw.fused_probability) || 0.5,
    technical_probability: Number(raw.technical_probability) || 0.5,
    consensus_probability: Number(raw.consensus_probability) || 0.5,
    sentiment_score: raw.sentiment_score != null ? Number(raw.sentiment_score) : null,
    market_regime: (raw.market_regime as string) || 'unknown',
    model_predictions: Array.isArray(raw.model_predictions)
      ? (raw.model_predictions as Record<string, unknown>[]).map((m) => ({
          model_name: (m.model_name as string) || '',
          direction: (m.direction as string) || '',
          probability: Number(m.probability) || 0.5,
          expected_return: Number(m.expected_return) || 0,
          sample_count: Number(m.sample_count) || 0,
        }))
      : [],
    rationale: (raw.rationale as string) || '',
    llm_summary: (raw.llm_summary as string) || '',
    created_at: (raw.created_at as string) || new Date().toISOString(),
  };
}

/* ------------------------------------------------------------------ */
/*  Agents                                                             */
/* ------------------------------------------------------------------ */

export async function fetchAgents(): Promise<Agent[]> {
  return api<Agent[]>('/api/v1/agents');
}

/* ------------------------------------------------------------------ */
/*  Market                                                             */
/* ------------------------------------------------------------------ */

export async function fetchTicker(asset: string): Promise<Ticker> {
  return api<Ticker>(`/api/v1/market/ticker/${asset}`);
}

export async function fetchKlines(
  asset: string,
  interval = '1h',
  limit = 200,
): Promise<Candle[]> {
  return api<Candle[]>(`/api/v1/market/klines/${asset}?interval=${interval}&limit=${limit}`);
}

export async function fetchAssets(top = 50): Promise<AssetInfo[]> {
  return api<AssetInfo[]>(`/api/v1/market/assets?top=${top}`);
}

export async function fetchMarketOverview() {
  return api<{
    assets: AssetInfo[];
    fear_greed: FearGreedValue | null;
    top_gainers: AssetInfo[];
    top_losers: AssetInfo[];
  }>('/api/v1/market/overview');
}

export async function fetchFearGreed(): Promise<FearGreedValue | null> {
  return api<FearGreedValue | null>('/api/v1/market/fear-greed');
}

export async function fetchMarketAnalysis(asset: string): Promise<MarketAnalysis> {
  const [ticker, klines, fearGreed] = await Promise.all([
    fetchTicker(asset).catch(() => null),
    fetchKlines(asset, '1h', 200).catch(() => []),
    fetchFearGreed().catch(() => null),
  ]);

  const prices = klines.map((c) => c.close);
  const returns = prices.slice(1).map((p, i) => (p - prices[i]) / prices[i]);
  const volatility = returns.length > 1 ? stdDev(returns) * Math.sqrt(365 * 24) : 0;

  const ema8 = ema(prices, 8);
  const ema26 = ema(prices, 26);
  const trendUp = ema8 > ema26;
  const recentChange = prices.length >= 2 ? (prices[prices.length - 1] - prices[prices.length - 2]) / prices[prices.length - 2] : 0;

  const sentiment = fearGreed ? fearGreed.value / 100 : 0.5;
  const momentumScore = Math.min(1, Math.max(0, 0.5 + recentChange * 50));
  const trendScore = trendUp ? 0.7 : 0.3;

  const technicalSignal =
    momentumScore > 0.6 && trendUp
      ? 'Strong Buy'
      : momentumScore > 0.5
      ? 'Buy'
      : momentumScore < 0.4 && !trendUp
      ? 'Strong Sell'
      : momentumScore < 0.5
      ? 'Sell'
      : 'Neutral';

  return {
    current_price: ticker?.price || (prices.length > 0 ? prices[prices.length - 1] : 0),
    volatility,
    sentiment_score: sentiment,
    trend: trendUp ? 'up' : 'down',
    technical_signal: technicalSignal,
    indicators: {
      momentum: momentumScore,
      trend: trendScore,
      volatility_score: Math.min(1, volatility * 5),
      sentiment,
    },
    regime: volatility > 0.8 ? 'high_volatility' : trendUp ? 'trending_up' : 'ranging',
  };
}

/* ------------------------------------------------------------------ */
/*  Portfolio                                                          */
/* ------------------------------------------------------------------ */

export async function fetchPortfolio(): Promise<Portfolio> {
  return api<Portfolio>('/api/v1/portfolio');
}

/* ------------------------------------------------------------------ */
/*  Dashboard (aggregated)                                             */
/* ------------------------------------------------------------------ */

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const [overview, agents, predictions] = await Promise.allSettled([
    fetchMarketOverview(),
    fetchAgents(),
    fetchPredictions(),
  ]);

  const assets = overview.status === 'fulfilled' ? overview.value.assets : [];
  const fearGreed = overview.status === 'fulfilled' ? overview.value.fear_greed : null;
  const agentList = agents.status === 'fulfilled' ? agents.value : [];
  const predList = predictions.status === 'fulfilled' ? predictions.value : [];

  const activeAgents = agentList.filter(
    (a) => a.status === 'active' || a.status === 'analyzing',
  ).length;

  return {
    total_predictions: predList.length,
    active_agents: activeAgents,
    total_value: 0,
    risk_score: predList.length > 0 ? predList[0].risk_score : 0,
    fear_greed: fearGreed?.value ?? 50,
    fear_greed_label: fearGreed?.classification ?? 'Neutral',
    top_movers: assets.slice(0, 10),
  };
}

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function stdDev(arr: number[]): number {
  if (arr.length < 2) return 0;
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  const variance = arr.reduce((s, v) => s + (v - mean) ** 2, 0) / (arr.length - 1);
  return Math.sqrt(variance);
}

function ema(prices: number[], span: number): number {
  if (prices.length === 0) return 0;
  const k = 2 / (span + 1);
  let emaVal = prices[0];
  for (let i = 1; i < prices.length; i++) {
    emaVal = prices[i] * k + emaVal * (1 - k);
  }
  return emaVal;
}
