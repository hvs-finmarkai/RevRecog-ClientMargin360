import apiClient from '../../lib/axios';

export interface DashboardOverview {
  totalRevenue: number;
  recognizedRevenue: number;
  billedAmount: number;
  outstandingAmount: number;
  activeContracts: number;
  totalClients: number;
  averageMargin: number;
  leakageAmount: number;
  revenueGrowth: number;
  marginTrend: 'up' | 'down' | 'neutral';
}

export interface RevenueTrendPoint {
  month: string;
  recognized: number;
  billed: number;
}

export interface MarginSummary {
  averageMargin: number;
  clientMargins: Array<{
    clientId: string;
    clientName: string;
    margin: number;
    revenue: number;
    trend: 'up' | 'down' | 'neutral';
  }>;
  atRiskClients: number;
  healthyClients: number;
}

export interface LeakageSummary {
  totalLeakage: number;
  leakagePercentage: number;
  sources: Array<{
    source: string;
    amount: number;
    percentage: number;
    severity: 'high' | 'medium' | 'low';
  }>;
  recommendations: string[];
}

export interface CollectionsSummary {
  totalOutstanding: number;
  collected: number;
  overdue: number;
  averageDSO: number;
  agingBuckets: Array<{
    bucket: string;
    amount: number;
    count: number;
  }>;
}

export interface DashboardFilters {
  dateFrom?: string;
  dateTo?: string;
  clientId?: string;
  period?: 'monthly' | 'quarterly' | 'yearly';
}

export const getOverview = async (filters?: DashboardFilters): Promise<DashboardOverview> => {
  const { data } = await apiClient.get('/dashboard/overview', { params: filters });
  return data;
};

export const getRevenueTrend = async (filters?: DashboardFilters): Promise<RevenueTrendPoint[]> => {
  const { data } = await apiClient.get('/dashboard/revenue-trend', { params: filters });
  return data;
};

export const getMarginSummary = async (filters?: DashboardFilters): Promise<MarginSummary> => {
  const { data } = await apiClient.get('/dashboard/margin-summary', { params: filters });
  return data;
};

export const getLeakageSummary = async (filters?: DashboardFilters): Promise<LeakageSummary> => {
  const { data } = await apiClient.get('/dashboard/leakage-summary', { params: filters });
  return data;
};

export const getCollectionsSummary = async (filters?: DashboardFilters): Promise<CollectionsSummary> => {
  const { data } = await apiClient.get('/dashboard/collections-summary', { params: filters });
  return data;
};
