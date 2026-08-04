/* ------------------------------------------------------------------ */
/*  TypeScript interfaces matching the Hermes backend API responses     */
/* ------------------------------------------------------------------ */

export interface Prediction {
  id: string;
  asset: string;
  symbol: string; // derived: asset + "USDT"
  interval: string;
  direction: 'UP' | 'DOWN';
  status: 'completed' | 'active' | 'failed';
  probability: number; // 0..1
  expected_return: number; // decimal, e.g. 0.001 = 0.1%
  expected_price: number | null;
  target_price: number | null;
  stop_loss: number | null;
  confidence_lower: number | null;
  confidence_upper: number | null;
  model_ensemble: string;
  model_weights: Record<string, number>;
  kelly_size: number;
  risk_score: number;
  var_95: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  fused_probability: number;
  technical_probability: number;
  consensus_probability: number;
  sentiment_score: number | null;
  market_regime: string;
  model_predictions: ModelPrediction[];
  rationale: string;
  llm_summary: string;
  created_at: string;
}

export interface ModelPrediction {
  model_name: string;
  direction: string;
  probability: number;
  expected_return: number;
  sample_count: number;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'analyzing' | 'idle';
  last_run: string | null;
  execution_time_ms: number | null;
  last_asset: string | null;
}

export interface DashboardStats {
  total_predictions: number;
  active_agents: number;
  total_value: number;
  risk_score: number;
  fear_greed: number;
  fear_greed_label: string;
  top_movers: AssetInfo[];
}

export interface AssetInfo {
  symbol: string;
  name: string;
  price: number;
  change_pct_24h: number;
  market_cap: number;
  volume_24h: number;
}

export interface Ticker {
  symbol: string;
  price: number;
  bid: number;
  ask: number;
  high_24h: number;
  low_24h: number;
  volume_24h: number;
  change_24h: number;
  change_pct_24h: number;
  timestamp: string;
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface FearGreedValue {
  value: number;
  classification: string;
  timestamp: string;
}

export interface MarketAnalysis {
  current_price: number;
  volatility: number;
  sentiment_score: number;
  trend: string;
  technical_signal: string;
  indicators: Record<string, number>;
  regime: string;
}

export interface Portfolio {
  total_value: number;
  cash_balance: number;
  total_pnl: number;
  total_pnl_pct: number;
  unrealized_pnl: number;
  realized_pnl: number;
  positions: Position[];
  allocation: Record<string, number>;
  diversification_score: number;
  risk_score: number;
}

export interface Position {
  id: string;
  asset: string;
  side: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}
