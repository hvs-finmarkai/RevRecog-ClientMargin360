import { useEffect } from 'react';
import { TrendingUp, Brain, CheckCircle, Clock } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatPercent, formatStatus, getStatusColor } from '@/lib/utils';

export default function RevenueRecognitionPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Revenue Recognition');
  }, [setPageTitle]);

  const entries = [
    { contract: 'CTR-2024-001', client: 'Acme Corp', method: 'Percentage of Completion', total: 5000000, recognized: 3750000, percent: 75, status: 'approved', confidence: 94 },
    { contract: 'CTR-2024-002', client: 'TechVista Ltd', method: 'Time Elapsed', total: 3200000, recognized: 1600000, percent: 50, status: 'pending_review', confidence: 87 },
    { contract: 'CTR-2024-003', client: 'GlobalSync Inc', method: 'Milestone', total: 8500000, recognized: 5100000, percent: 60, status: 'approved', confidence: 96 },
    { contract: 'CTR-2024-005', client: 'CloudNine', method: 'Straight Line', total: 4700000, recognized: 1175000, percent: 25, status: 'draft', confidence: 82 },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Revenue Recognition</h1>
          <p className="text-sm text-navy-500 mt-1">AI-powered ASC 606 / Ind AS 115 compliant revenue recognition</p>
        </div>
        <button className="btn-primary"><Brain className="w-4 h-4 mr-2" />Run AI Analysis</button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <TrendingUp className="w-5 h-5 text-primary-500 mx-auto" />
          <p className="text-sm text-navy-500 mt-2">Recognized (MTD)</p>
          <p className="text-xl font-bold text-navy-900 mt-1">{formatCurrency(11625000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <Clock className="w-5 h-5 text-warning-500 mx-auto" />
          <p className="text-sm text-navy-500 mt-2">Deferred</p>
          <p className="text-xl font-bold text-navy-900 mt-1">{formatCurrency(9775000, { compact: true })}</p>
        </div>
        <div className="card text-center">
          <CheckCircle className="w-5 h-5 text-success-500 mx-auto" />
          <p className="text-sm text-navy-500 mt-2">Approved</p>
          <p className="text-xl font-bold text-navy-900 mt-1">32</p>
        </div>
        <div className="card text-center">
          <Brain className="w-5 h-5 text-primary-500 mx-auto" />
          <p className="text-sm text-navy-500 mt-2">Avg AI Confidence</p>
          <p className="text-xl font-bold text-navy-900 mt-1">91.2%</p>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Contract</th>
                <th className="table-header">Client</th>
                <th className="table-header">Method</th>
                <th className="table-header">Total Value</th>
                <th className="table-header">Recognized</th>
                <th className="table-header">% Complete</th>
                <th className="table-header">AI Conf.</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.contract} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium text-primary-600">{e.contract}</td>
                  <td className="table-cell">{e.client}</td>
                  <td className="table-cell text-xs">{e.method}</td>
                  <td className="table-cell">{formatCurrency(e.total)}</td>
                  <td className="table-cell font-medium">{formatCurrency(e.recognized)}</td>
                  <td className="table-cell">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-navy-100 rounded-full overflow-hidden">
                        <div className="h-full bg-primary-500 rounded-full" style={{ width: `${e.percent}%` }} />
                      </div>
                      <span className="text-xs">{formatPercent(e.percent, 0)}</span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className={`text-xs font-medium ${e.confidence >= 90 ? 'text-success-600' : 'text-warning-600'}`}>
                      {e.confidence}%
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={getStatusColor(e.status)}>{formatStatus(e.status)}</span>
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
