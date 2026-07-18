import { useQuery } from '@tanstack/react-query';
import {
  getOverview,
  getRevenueTrend,
  getMarginSummary,
  getLeakageSummary,
  DashboardFilters,
} from '../services/api/dashboard';

export function useOverview(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'overview', filters],
    queryFn: () => getOverview(filters),
    staleTime: 60000,
  });
}

export function useRevenueTrend(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'revenue-trend', filters],
    queryFn: () => getRevenueTrend(filters),
    staleTime: 60000,
  });
}

export function useMarginSummary(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'margin-summary', filters],
    queryFn: () => getMarginSummary(filters),
    staleTime: 60000,
  });
}

export function useLeakageSummary(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'leakage-summary', filters],
    queryFn: () => getLeakageSummary(filters),
    staleTime: 60000,
  });
}
