export interface SystemHealth {
  status: string;
  services: {
    backend: string;
    sqlite: string;
    openrouter: string;
    binance: string;
    polymarket: string;
    apify: string;
  };
}

export interface Prediction {
  id?: number;
  timestamp: string;
  asset: string;
  signal_direction: string;
  fused_probability: number;
  kelly_size: number;
  expected_value?: number;
  rationale?: string;
}

export interface MarketOdds {
  id?: number;
  timestamp: string;
  asset: string;
  source: string;
  implied_probability: number;
  odds: number;
}

export interface Metric {
  id?: number;
  timestamp: string;
  accuracy: number;
  win_rate: number;
  brier_score: number;
}

export interface AgentRun {
  id?: number;
  timestamp: string;
  agent_name: string;
  status: string;
  execution_time_ms: number;
  error_message: string | null;
  message: string;
}
