import { useEffect } from 'react';
import { Wallet, Phone, Search } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, cn } from '@/lib/utils';

export default function CollectionsPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Collections');
  }, [setPageTitle]);

  const collections = [
    { invoice: 'INV-2024-089', client: 'Acme Corp', amount: 850000, due: '2024-11-30', daysPastDue: 15, priority: 'high', status: 'in_progress' },
    { invoice: 'INV-2024-078', client: 'DataFlow', amount: 420000, due: '2024-11-15', daysPastDue: 30, priority: 'critical', status: 'escalated' },
    { invoice: 'INV-2024-085', client: 'TechVista', amount: 320000, due: '2024-12-01', daysPastDue: 14, priority: 'medium', status: 'promised' },
    { invoice: 'INV-2024-091', client: 'GlobalSync', amount: 750000, due: '2024-12-15', daysPastDue: 0, priority: 'low', status: 'pending' },
  ];

  const getPriorityColor = (priority: string) => {
    const map: Record<string, string> = {
      critical: 'text-danger-600 font-bold',
      high: 'text-danger-500 font-medium',
      medium: 'text-warning-600',
      low: 'text-navy-500',
    };
    return map[priority] || '';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Collections</h1>
          <p className="text-sm text-navy-500 mt-1">Manage outstanding payments and follow-ups</p>
        </div>
        <button className="btn-primary"><Phone className="w-4 h-4 mr-2" />Log Follow-up</button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <Wallet className="w-5 h-5 text-navy-500 mx-auto" />
          <p className="text-sm text-navy-500 mt-2">Total Outstanding</p>
          <p className="text-xl font-bold text-navy-900 mt-1">{formatCurrency(2340000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Current (0-30 days)</p>
          <p className="text-xl font-bold text-warning-600 mt-1">{formatCurrency(1070000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Overdue (31-60)</p>
          <p className="text-xl font-bold text-danger-500 mt-1">{formatCurrency(850000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Critical (60+)</p>
          <p className="text-xl font-bold text-danger-700 mt-1">{formatCurrency(420000, { compact: true })}</p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-400" />
        <input type="text" placeholder="Search collections..." className="input-field pl-9" />
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Invoice</th>
                <th className="table-header">Client</th>
                <th className="table-header">Amount</th>
                <th className="table-header">Due Date</th>
                <th className="table-header">Days Past Due</th>
                <th className="table-header">Priority</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {collections.map((c) => (
                <tr key={c.invoice} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{c.invoice}</td>
                  <td className="table-cell">{c.client}</td>
                  <td className="table-cell font-medium">{formatCurrency(c.amount)}</td>
                  <td className="table-cell">{formatDate(c.due)}</td>
                  <td className="table-cell">
                    <span className={cn(c.daysPastDue > 0 ? 'text-danger-600 font-medium' : 'text-success-600')}>
                      {c.daysPastDue > 0 ? `${c.daysPastDue} days` : 'Current'}
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={cn('capitalize', getPriorityColor(c.priority))}>{c.priority}</span>
                  </td>
                  <td className="table-cell">
                    <span className="badge-warning capitalize">{c.status.replace('_', ' ')}</span>
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
