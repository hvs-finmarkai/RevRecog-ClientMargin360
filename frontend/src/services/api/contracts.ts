import apiClient from '../../lib/axios';

export interface Contract {
  id: string;
  clientId: string;
  clientName: string;
  contractType: string;
  billingModel: 'T&M' | 'Milestone' | 'Retainer' | 'Performance' | 'Hybrid';
  totalValue: number;
  recognizedRevenue: number;
  billedAmount: number;
  startDate: string;
  endDate: string;
  status: 'active' | 'completed' | 'pending' | 'expired';
  createdAt: string;
}

export interface ContractFilters {
  clientId?: string;
  status?: string;
  billingModel?: string;
  page?: number;
  limit?: number;
  search?: string;
}

export interface CreateContractPayload {
  clientId: string;
  contractType: string;
  billingModel: string;
  totalValue: number;
  startDate: string;
  endDate: string;
  terms?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export const getContracts = async (filters?: ContractFilters): Promise<PaginatedResponse<Contract>> => {
  const { data } = await apiClient.get('/contracts', { params: filters });
  return data;
};

export const getContract = async (id: string): Promise<Contract> => {
  const { data } = await apiClient.get(`/contracts/${id}`);
  return data;
};

export const createContract = async (payload: CreateContractPayload): Promise<Contract> => {
  const { data } = await apiClient.post('/contracts', payload);
  return data;
};

export const updateContract = async (id: string, payload: Partial<CreateContractPayload>): Promise<Contract> => {
  const { data } = await apiClient.patch(`/contracts/${id}`, payload);
  return data;
};

export const uploadContract = async (file: File): Promise<{ id: string; parsedData: Record<string, unknown> }> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post('/contracts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const parseContract = async (id: string): Promise<{ extractedTerms: Record<string, unknown>; confidence: number }> => {
  const { data } = await apiClient.post(`/contracts/${id}/parse`);
  return data;
};
