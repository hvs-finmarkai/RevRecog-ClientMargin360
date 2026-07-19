import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus, AlertTriangle } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatStatus, getStatusColor } from '@/lib/utils';
import apiClient from '@/lib/axios';

interface Contract {
  id: string;
  contract_number: string;
  client_name: string;
  billing_model: string;
  billing_model_display: string;
  total_value: string;
  status: string;
  start_date: string;
  end_date: string;
}

interface ContractsResponse {
  results?: Contract[];
}

export default function ContractsPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Contracts');
  }, [setPageTitle]);

  const { data, isLoading, isError, error } = useQuery<ContractsResponse>({
    queryKey: ['contracts'],
    queryFn: async () => {
      const response = await apiClient.get('/contracts/contracts/');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-danger-500 mx-auto mb-3" />
          <p className="text-lg font-medium text-navy-900">Failed to load contracts</p>
          <p className="text-sm text-navy-500 mt-1">{(error as Error)?.message || 'An unexpected error occurred'}</p>
        </div>
      </div>
    );
  }

  const contracts: Contract[] = Array.isArray(data) ? data : data?.results || [];

  if (contracts.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="page-title">Contracts</h1>
            <p className="text-sm text-navy-500 mt-1">Manage and track all client contracts</p>
          </div>
          <button className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            New Contract
          </button>
        </div>
        <div className="flex items-center justify-center h-48">
          <p className="text-navy-500">No contracts found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Contracts</h1>
          <p className="text-sm text-navy-500 mt-1">Manage and track all client contracts</p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Contract
        </button>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Contract #</th>
                <th className="table-header">Client</th>
                <th className="table-header">Billing Model</th>
                <th className="table-header">Value</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.id} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{c.contract_number}</td>
                  <td className="table-cell">{c.client_name}</td>
                  <td className="table-cell">{c.billing_model_display || formatStatus(c.billing_model)}</td>
                  <td className="table-cell font-medium">{formatCurrency(parseFloat(c.total_value))}</td>
                  <td className="table-cell">
                    <span className={getStatusColor(c.status)}>{formatStatus(c.status)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between px-4 py-3 border-t border-navy-100">
          <p className="text-sm text-navy-500">Showing {contracts.length} contracts</p>
        </div>
      </div>
    </div>
  );
}
