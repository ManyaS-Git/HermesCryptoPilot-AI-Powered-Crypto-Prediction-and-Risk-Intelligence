import axios from 'axios';
import { SystemHealth, Prediction, MarketOdds, Metric, AgentRun } from '../types';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // FastApi server
});

export const fetchHealth = async (): Promise<SystemHealth> => {
  const { data } = await api.get('/health-check');
  return data;
};

export const fetchLatestPredictions = async (): Promise<Prediction[]> => {
  const { data } = await api.get('/predictions/latest');
  return data;
};

export const fetchPredictionHistory = async (asset: string): Promise<Prediction[]> => {
  const { data } = await api.get(`/predictions/history?asset=${asset}`);
  return data;
};

export const fetchMetrics = async (): Promise<Metric> => {
  const { data } = await api.get('/metrics');
  // Return the most recent metric
  return Array.isArray(data) ? data[0] : data;
};

export const fetchMarkets = async (asset: string): Promise<MarketOdds[]> => {
  const { data } = await api.get(`/markets?asset=${asset}`);
  return data;
};

export const fetchAgentRuns = async (): Promise<AgentRun[]> => {
  const { data } = await api.get('/runs');
  return data;
};

export const triggerWorkflow = async (asset: string): Promise<any> => {
  const { data } = await api.post('/trigger-workflow', { asset });
  return data;
};
