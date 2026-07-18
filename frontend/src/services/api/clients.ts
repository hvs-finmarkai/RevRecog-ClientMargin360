import apiClient from '../../lib/axios';

export interface Client {
  id: string;
  name: string;
  industry: string;
  contractCount: number;
  totalRevenue: number;
  margin: number;
  healthScore: number;
  status: 'active' | 'inactive' | 'at-risk';
  createdAt: string;
}

export interface ClientProfitability {
  clientId: string;
  clientName: string;
  revenue: number;
  costs: number;
  margin: number;
  marginPercentage: number;
  trend: 'up' | 'down' | 'neutral';
  monthlyBreakdown: Array<{ month: string; revenue: number; costs: number; margin: number }>;
}

export interface ClientHealth {
  clientId: string;
  overallScore: number;
  paymentTimeliness: number;
  contractAdherence: number;
  marginHealth: number;
  riskFactors: string[];
  recommendations: string[];
}

export interface ClientFilters {
  status?: string;
  industry?: string;
  page?: number;
  limit?: number;
  search?: string;
}

export interface CreateClientPayload {
  name: string;
  industry: string;
  contactEmail?: string;
  contactPhone?: string;
}

export const getClients = async (filters?: ClientFilters): Promise<{ data: Client[]; total: number; page: number; limit: number }> => {
  const { data } = await apiClient.get('/clients', { params: filters });
  return data;
};

export const getClient = async (id: string): Promise<Client> => {
  const { data } = await apiClient.get(`/clients/${id}`);
  return data;
};

export const createClient = async (payload: CreateClientPayload): Promise<Client> => {
  const { data } = await apiClient.post('/clients', payload);
  return data;
};

export const getClientProfitability = async (id: string): Promise<ClientProfitability> => {
  const { data } = await apiClient.get(`/clients/${id}/profitability`);
  return data;
};

export const getClientHealth = async (id: string): Promise<ClientHealth> => {
  const { data } = await apiClient.get(`/clients/${id}/health`);
  return data;
};
