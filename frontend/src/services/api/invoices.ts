import apiClient from '../../lib/axios';

export interface Invoice {
  id: string;
  contractId: string;
  clientId: string;
  clientName: string;
  invoiceNumber: string;
  amount: number;
  taxAmount: number;
  totalAmount: number;
  status: 'draft' | 'generated' | 'sent' | 'approved' | 'paid' | 'overdue';
  dueDate: string;
  generatedAt: string;
  paidAt?: string;
}

export interface InvoiceFilters {
  clientId?: string;
  contractId?: string;
  status?: string;
  page?: number;
  limit?: number;
  dateFrom?: string;
  dateTo?: string;
}

export interface GenerateInvoicePayload {
  contractId: string;
  periodStart: string;
  periodEnd: string;
  lineItems?: Array<{ description: string; amount: number }>;
}

export interface BulkGeneratePayload {
  contractIds: string[];
  periodStart: string;
  periodEnd: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export const getInvoices = async (filters?: InvoiceFilters): Promise<PaginatedResponse<Invoice>> => {
  const { data } = await apiClient.get('/invoices', { params: filters });
  return data;
};

export const getInvoice = async (id: string): Promise<Invoice> => {
  const { data } = await apiClient.get(`/invoices/${id}`);
  return data;
};

export const generateInvoice = async (payload: GenerateInvoicePayload): Promise<Invoice> => {
  const { data } = await apiClient.post('/invoices/generate', payload);
  return data;
};

export const approveInvoice = async (id: string): Promise<Invoice> => {
  const { data } = await apiClient.post(`/invoices/${id}/approve`);
  return data;
};

export const bulkGenerate = async (payload: BulkGeneratePayload): Promise<{ invoices: Invoice[]; failed: string[] }> => {
  const { data } = await apiClient.post('/invoices/bulk-generate', payload);
  return data;
};
