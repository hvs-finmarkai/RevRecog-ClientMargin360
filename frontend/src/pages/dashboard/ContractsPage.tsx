import { useEffect } from 'react';
import { Plus, Search, Filter, Download } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, formatStatus, getStatusColor } from '@/lib/utils';

export default function ContractsPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Contracts');
  }, [setPageTitle]);

  const contracts = [
    { id: 'CTR-2024-001', client: 'Acme Corp', type: 'Fixed Price', value: 5000000, start: '2024-01-15', end: '2024-12-31', status: 'active' },
    { id: 'CTR-2024-002', client: 'TechVista Ltd', type: 'Time & Material', value: 3200000, start: '2024-02-01', end: '2024-11-30', status: 'active' },
    { id: 'CTR-2024-003', client: 'GlobalSync Inc', type: 'Milestone', value: 8500000, start: '2024-03-01', end: '2025-02-28', status: 'active' },
    { id: 'CTR-2024-004', client: 'DataFlow Systems', type: 'Retainer', value: 1200000, start: '2024-01-01', end: '2024-06-30', status: 'expired' },
    { id: 'CTR-2024-005', client: 'CloudNine Solutions', type: 'Fixed Price', value: 4700000, start: '2024-04-15', end: '2025-04-14', status: 'draft' },
  ];

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

      <div className="card">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-400" />
            <input type="text" placeholder="Search contracts..." className="input-field pl-9" />
          </div>
          <select className="input-field w-auto">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="draft">Draft</option>
            <option value="expired">Expired</option>
          </select>
          <button className="btn-secondary">
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Contract ID</th>
                <th className="table-header">Client</th>
                <th className="table-header">Type</th>
                <th className="table-header">Value</th>
                <th className="table-header">Start</th>
                <th className="table-header">End</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {contracts.map((c) => (
                <tr key={c.id} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{c.id}</td>
                  <td className="table-cell">{c.client}</td>
                  <td className="table-cell">{c.type}</td>
                  <td className="table-cell font-medium">{formatCurrency(c.value)}</td>
                  <td className="table-cell">{formatDate(c.start)}</td>
                  <td className="table-cell">{formatDate(c.end)}</td>
                  <td className="table-cell">
                    <span className={getStatusColor(c.status)}>{formatStatus(c.status)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between px-4 py-3 border-t border-navy-100">
          <p className="text-sm text-navy-500">Showing 1-5 of 47 contracts</p>
          <div className="flex gap-2">
            <button className="btn-secondary text-xs py-1.5 px-3" disabled>Previous</button>
            <button className="btn-secondary text-xs py-1.5 px-3">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
