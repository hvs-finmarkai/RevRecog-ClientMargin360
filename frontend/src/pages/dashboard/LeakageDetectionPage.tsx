import { useEffect } from 'react';
import { AlertTriangle, Search, Eye } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, formatStatus, getStatusColor } from '@/lib/utils';

export default function LeakageDetectionPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Leakage Detection');
  }, [setPageTitle]);

  const leakages = [
    { id: 'LK-001', type: 'Unbilled Work', client: 'Acme Corp', amount: 125000, severity: 'high', detected: '2024-12-10', status: 'detected' },
    { id: 'LK-002', type: 'Rate Mismatch', client: 'TechVista Ltd', amount: 85000, severity: 'medium', detected: '2024-12-12', status: 'investigating' },
    { id: 'LK-003', type: 'Scope Creep', client: 'DataFlow', amount: 200000, severity: 'critical', detected: '2024-12-08', status: 'confirmed' },
    { id: 'LK-004', type: 'Missed Escalation', client: 'GlobalSync', amount: 45000, severity: 'low', detected: '2024-12-15', status: 'resolved' },
    { id: 'LK-005', type: 'Delayed Billing', client: 'CloudNine', amount: 95000, severity: 'medium', detected: '2024-12-14', status: 'detected' },
  ];

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-danger-100 text-danger-700',
      high: 'bg-danger-50 text-danger-600',
      medium: 'bg-warning-50 text-warning-700',
      low: 'bg-primary-50 text-primary-700',
    };
    return `badge ${colors[severity] || 'badge-primary'}`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Leakage Detection</h1>
          <p className="text-sm text-navy-500 mt-1">AI-detected revenue leakages and unbilled work</p>
        </div>
        <button className="btn-primary"><AlertTriangle className="w-4 h-4 mr-2" />Scan Now</button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-sm text-navy-500">Total Leakage (MTD)</p>
          <p className="text-xl font-bold text-danger-600 mt-1">{formatCurrency(550000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Active Issues</p>
          <p className="text-xl font-bold text-warning-600 mt-1">8</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Recovered</p>
          <p className="text-xl font-bold text-success-600 mt-1">{formatCurrency(230000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Recovery Rate</p>
          <p className="text-xl font-bold text-navy-900 mt-1">72%</p>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-navy-400" />
        <input type="text" placeholder="Search leakages..." className="input-field pl-9" />
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">ID</th>
                <th className="table-header">Type</th>
                <th className="table-header">Client</th>
                <th className="table-header">Amount</th>
                <th className="table-header">Severity</th>
                <th className="table-header">Detected</th>
                <th className="table-header">Status</th>
                <th className="table-header">Action</th>
              </tr>
            </thead>
            <tbody>
              {leakages.map((l) => (
                <tr key={l.id} className="border-b border-navy-50 hover:bg-navy-50/50 transition-colors">
                  <td className="table-cell font-medium text-primary-600">{l.id}</td>
                  <td className="table-cell">{l.type}</td>
                  <td className="table-cell">{l.client}</td>
                  <td className="table-cell font-medium text-danger-600">{formatCurrency(l.amount)}</td>
                  <td className="table-cell">
                    <span className={getSeverityBadge(l.severity)}>{l.severity}</span>
                  </td>
                  <td className="table-cell">{formatDate(l.detected)}</td>
                  <td className="table-cell">
                    <span className={getStatusColor(l.status)}>{formatStatus(l.status)}</span>
                  </td>
                  <td className="table-cell">
                    <button className="text-primary-500 hover:text-primary-700">
                      <Eye className="w-4 h-4" />
                    </button>
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
