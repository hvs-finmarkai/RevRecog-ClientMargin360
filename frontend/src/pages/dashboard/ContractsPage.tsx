import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
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

  const { data } = useQuery<ContractsResponse>({
    queryKey: ['contracts'],
    queryFn: async () => {
      const response = await apiClient.get('/contracts/contracts/');
      return response.data;
    },
    retry: 1,
  });

  const fallbackContracts: Contract[] = [
    { id: '1', contract_number: 'CTR-001', client_name: 'Denave India', billing_model: 'T&M', billing_model_display: 'Time & Material', total_value: '245000000', status: 'active', start_date: '2024-01-01', end_date: '2025-12-31' },
    { id: '2', contract_number: 'CTR-002', client_name: 'Infosys BPM', billing_model: 'Milestone', billing_model_display: 'Fixed Milestone', total_value: '182000000', status: 'active', start_date: '2024-03-01', end_date: '2025-09-30' },
    { id: '3', contract_number: 'CTR-003', client_name: 'TCS Digital', billing_model: 'Retainer', billing_model_display: 'Monthly Retainer', total_value: '320000000', status: 'active', start_date: '2024-02-01', end_date: '2026-01-31' },
    { id: '4', contract_number: 'CTR-004', client_name: 'Wipro Analytics', billing_model: 'Performance', billing_model_display: 'Performance-Based', total_value: '158000000', status: 'active', start_date: '2024-04-01', end_date: '2025-03-31' },
    { id: '5', contract_number: 'CTR-005', client_name: 'HCL Tech', billing_model: 'Hybrid', billing_model_display: 'Hybrid', total_value: '221000000', status: 'under_review', start_date: '2024-01-15', end_date: '2025-07-14' },
    { id: '6', contract_number: 'CTR-006', client_name: 'Reliance Jio', billing_model: 'Retainer', billing_model_display: 'Monthly Retainer', total_value: '285000000', status: 'active', start_date: '2024-05-01', end_date: '2026-04-30' },
    { id: '7', contract_number: 'CTR-007', client_name: 'Bharti Airtel', billing_model: 'T&M', billing_model_display: 'Time & Material', total_value: '124000000', status: 'active', start_date: '2024-06-01', end_date: '2025-05-31' },
    { id: '8', contract_number: 'CTR-008', client_name: 'Tata Motors', billing_model: 'Milestone', billing_model_display: 'Fixed Milestone', total_value: '197000000', status: 'at_risk', start_date: '2024-02-01', end_date: '2025-01-31' },
  ];

  const contracts = data?.results?.length ? data.results : fallbackContracts;

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
