import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  fetchHealth, 
  fetchLatestPredictions, 
  fetchPredictionHistory, 
  fetchMetrics, 
  fetchMarkets, 
  fetchAgentRuns, 
  triggerWorkflow 
} from '../services/api';

const POLLING_INTERVAL = 5000;

export const useHealth = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: POLLING_INTERVAL,
  });
};

export const useLatestPredictions = () => {
  return useQuery({
    queryKey: ['latestPredictions'],
    queryFn: fetchLatestPredictions,
    refetchInterval: POLLING_INTERVAL,
  });
};

export const usePredictionHistory = (asset: string) => {
  return useQuery({
    queryKey: ['predictionHistory', asset],
    queryFn: () => fetchPredictionHistory(asset),
    refetchInterval: POLLING_INTERVAL,
  });
};

export const useMetrics = () => {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
    refetchInterval: POLLING_INTERVAL,
  });
};

export const useMarkets = (asset: string) => {
  return useQuery({
    queryKey: ['markets', asset],
    queryFn: () => fetchMarkets(asset),
    refetchInterval: POLLING_INTERVAL,
  });
};

export const useAgentRuns = () => {
  return useQuery({
    queryKey: ['agentRuns'],
    queryFn: fetchAgentRuns,
    refetchInterval: POLLING_INTERVAL,
  });
};

export const useTriggerWorkflow = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (asset: string) => triggerWorkflow(asset),
    onSuccess: () => {
      // Invalidate queries to trigger an immediate refetch
      queryClient.invalidateQueries({ queryKey: ['latestPredictions'] });
      queryClient.invalidateQueries({ queryKey: ['agentRuns'] });
    },
  });
};
