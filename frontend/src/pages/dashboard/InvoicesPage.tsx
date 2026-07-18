import { useEffect } from 'react';
import { Plus, Search, Download } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, formatStatus, getStatusColor } from '@/lib/utils';

export default function InvoicesPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Billing & Invoices');
  }, [setPageTitle]);

  const invoices = [
    { id: 'INV-2024-089', client: 'Acme Corp', amount: 850000, issued: '2024-11-01', due: '2024-11-30', status: 'overdue' },
    { id: 'INV-2024-090', client: 'TechVista Ltd', amount: 420000, issued: '2024-11-15', due: '2024-12-15', status: 'sent' },
    { id: 'INV-2024-091', client: 'GlobalSync Inc', amount: 1500000, issued: '2024-12-01', due: '2024-12-31', status: 'partially_paid' },
    { id: 'INV-2024-092', client: 'DataFlow Systems', amount: 200000, issued: '2024-12-10', due: '2025-01-09', status: 'paid' },
    { id: 'INV-2024-093', client: 'CloudNine', amount: 780000, issued: '2024-12-15', due: '2025-01-14', status: 'draft' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Billing & Invoices</h1>
          <p className="text-sm text-navy-500 mt-1">Track invoices, payments, and billing cycles</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary"><Download className="w-4 h-4 mr-2" />Export</button>
          <button className="btn-primary"><Plus className="w-4 h-4 mr-2" />Create Invoice</button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-sm text-navy-500">Total Billed (MTD)</p>
          <p className="text-xl font-bold text-navy-900 mt-1">{formatCurrency(3750000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Collected</p>
          <p className="text-xl font-bold text-success-600 mt-1">{formatCurrency(2800000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Outstanding</p>
          <p className="text-xl font-bold text-warning-600 mt-1">{formatCurrency(950000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Overdue</p>
          <p className="text-xl font-bold text-danger-600 mt-1">{formatCurrency(850000, { compact: true })}</p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-400" />
        <input type="text" placeholder="Search invoices..." className="input-field pl-9" />
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Invoice #</th>
                <th className="table-header">Client</th>
                <th className="table-header">Amount</th>
                <th className="table-header">Issued</th>
                <th className="table-header">Due</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{inv.id}</td>
                  <td className="table-cell">{inv.client}</td>
                  <td className="table-cell font-medium">{formatCurrency(inv.amount)}</td>
                  <td className="table-cell">{formatDate(inv.issued)}</td>
                  <td className="table-cell">{formatDate(inv.due)}</td>
                  <td className="table-cell">
                    <span className={getStatusColor(inv.status)}>{formatStatus(inv.status)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between px-4 py-3 border-t border-navy-100">
          <p className="text-sm text-navy-500">Showing 1-5 of 93 invoices</p>
          <div className="flex gap-2">
            <button className="btn-secondary text-xs py-1.5 px-3" disabled>Previous</button>
            <button className="btn-secondary text-xs py-1.5 px-3">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
