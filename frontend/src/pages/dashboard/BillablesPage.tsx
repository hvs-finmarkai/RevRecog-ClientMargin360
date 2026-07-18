import { useEffect } from 'react';
import { Clock, Search, Filter } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, formatStatus, getStatusColor } from '@/lib/utils';

export default function BillablesPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Billables');
  }, [setPageTitle]);

  const billables = [
    { id: 'BL-001', client: 'Acme Corp', desc: 'Senior Developer - 160 hrs', type: 'time', amount: 480000, date: '2024-12-01', status: 'unbilled' },
    { id: 'BL-002', client: 'TechVista Ltd', desc: 'Cloud Infrastructure Setup', type: 'milestone', amount: 350000, date: '2024-12-05', status: 'approved' },
    { id: 'BL-003', client: 'GlobalSync Inc', desc: 'Travel Expenses - Dec', type: 'expense', amount: 45000, date: '2024-12-10', status: 'billed' },
    { id: 'BL-004', client: 'Acme Corp', desc: 'QA Engineer - 80 hrs', type: 'time', amount: 160000, date: '2024-12-12', status: 'unbilled' },
    { id: 'BL-005', client: 'DataFlow Systems', desc: 'Software License', type: 'material', amount: 120000, date: '2024-12-15', status: 'rejected' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Billables</h1>
          <p className="text-sm text-navy-500 mt-1">Track billable hours, expenses, and milestones</p>
        </div>
        <button className="btn-primary"><Clock className="w-4 h-4 mr-2" />Log Billable</button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card text-center">
          <p className="text-sm text-navy-500">Unbilled Amount</p>
          <p className="text-xl font-bold text-warning-600 mt-1">{formatCurrency(640000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Billed This Month</p>
          <p className="text-xl font-bold text-success-600 mt-1">{formatCurrency(1200000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Written Off</p>
          <p className="text-xl font-bold text-danger-600 mt-1">{formatCurrency(120000, { compact: true })}</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-400" />
          <input type="text" placeholder="Search billables..." className="input-field pl-9" />
        </div>
        <button className="btn-secondary"><Filter className="w-4 h-4 mr-2" />Filters</button>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">ID</th>
                <th className="table-header">Client</th>
                <th className="table-header">Description</th>
                <th className="table-header">Type</th>
                <th className="table-header">Amount</th>
                <th className="table-header">Date</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {billables.map((b) => (
                <tr key={b.id} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{b.id}</td>
                  <td className="table-cell">{b.client}</td>
                  <td className="table-cell max-w-[200px] truncate">{b.desc}</td>
                  <td className="table-cell capitalize">{b.type}</td>
                  <td className="table-cell font-medium">{formatCurrency(b.amount)}</td>
                  <td className="table-cell">{formatDate(b.date)}</td>
                  <td className="table-cell">
                    <span className={getStatusColor(b.status)}>{formatStatus(b.status)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
