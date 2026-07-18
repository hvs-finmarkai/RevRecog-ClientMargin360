import { useEffect } from 'react';
import { PieChart, Download, TrendingUp, TrendingDown } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatPercent, cn } from '@/lib/utils';

export default function ClientProfitabilityPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Client Profitability');
  }, [setPageTitle]);

  const clients = [
    { name: 'Acme Corp', revenue: 5000000, costs: 3250000, margin: 35.0, dso: 38, leakage: 50000, trend: 'up' },
    { name: 'TechVista Ltd', revenue: 3200000, costs: 2240000, margin: 30.0, dso: 45, leakage: 120000, trend: 'down' },
    { name: 'GlobalSync Inc', revenue: 8500000, costs: 5100000, margin: 40.0, dso: 32, leakage: 0, trend: 'up' },
    { name: 'DataFlow Systems', revenue: 1200000, costs: 960000, margin: 20.0, dso: 67, leakage: 80000, trend: 'down' },
    { name: 'CloudNine Solutions', revenue: 4700000, costs: 3055000, margin: 35.0, dso: 41, leakage: 25000, trend: 'up' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Client Profitability</h1>
          <p className="text-sm text-navy-500 mt-1">360° view of client margins, LTV, and profitability metrics</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary"><Download className="w-4 h-4 mr-2" />Export</button>
          <button className="btn-primary"><PieChart className="w-4 h-4 mr-2" />Full Analysis</button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-sm text-navy-500">Avg Gross Margin</p>
          <p className="text-xl font-bold text-navy-900 mt-1">34.2%</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Top Client Margin</p>
          <p className="text-xl font-bold text-success-600 mt-1">40.0%</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">At-Risk Clients</p>
          <p className="text-xl font-bold text-danger-600 mt-1">2</p>
        </div>
        <div className="card text-center">
          <p className="text-sm text-navy-500">Total Leakage</p>
          <p className="text-xl font-bold text-warning-600 mt-1">{formatCurrency(275000, { compact: true })}</p>
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Client</th>
                <th className="table-header">Revenue</th>
                <th className="table-header">Costs</th>
                <th className="table-header">Margin %</th>
                <th className="table-header">DSO</th>
                <th className="table-header">Leakage</th>
                <th className="table-header">Trend</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((c) => (
                <tr key={c.name} className="border-b border-navy-50 hover:bg-navy-50/50 cursor-pointer transition-colors">
                  <td className="table-cell font-medium">{c.name}</td>
                  <td className="table-cell">{formatCurrency(c.revenue, { compact: true })}</td>
                  <td className="table-cell">{formatCurrency(c.costs, { compact: true })}</td>
                  <td className="table-cell">
                    <span className={cn('font-medium', c.margin >= 30 ? 'text-success-600' : 'text-danger-600')}>
                      {formatPercent(c.margin)}
                    </span>
                  </td>
                  <td className="table-cell">
                    <span className={cn(c.dso > 60 ? 'text-danger-600 font-medium' : '')}>{c.dso} days</span>
                  </td>
                  <td className="table-cell">
                    {c.leakage > 0 ? (
                      <span className="text-danger-600">{formatCurrency(c.leakage, { compact: true })}</span>
                    ) : (
                      <span className="text-success-600">None</span>
                    )}
                  </td>
                  <td className="table-cell">
                    {c.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-success-500" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-danger-500" />
                    )}
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
