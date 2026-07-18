import { useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  FileText,
  AlertTriangle,
  Users,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatPercent, cn } from '@/lib/utils';

interface StatCard {
  title: string;
  value: string;
  change: number;
  changeLabel: string;
  icon: React.ComponentType<{ className?: string }>;
  iconBg: string;
}

const stats: StatCard[] = [
  {
    title: 'Total Revenue (MTD)',
    value: formatCurrency(24500000, { compact: true }),
    change: 12.5,
    changeLabel: 'vs last month',
    icon: DollarSign,
    iconBg: 'bg-primary-100 text-primary-600',
  },
  {
    title: 'Outstanding Amount',
    value: formatCurrency(8700000, { compact: true }),
    change: -5.2,
    changeLabel: 'vs last month',
    icon: TrendingDown,
    iconBg: 'bg-warning-100 text-warning-600',
  },
  {
    title: 'Active Contracts',
    value: '47',
    change: 3,
    changeLabel: 'new this month',
    icon: FileText,
    iconBg: 'bg-success-100 text-success-600',
  },
  {
    title: 'Revenue Leakage',
    value: formatCurrency(320000, { compact: true }),
    change: -18.3,
    changeLabel: 'vs last month',
    icon: AlertTriangle,
    iconBg: 'bg-danger-100 text-danger-600',
  },
  {
    title: 'Avg Client Margin',
    value: '34.2%',
    change: 2.1,
    changeLabel: 'vs last quarter',
    icon: TrendingUp,
    iconBg: 'bg-success-100 text-success-600',
  },
  {
    title: 'DSO (Days)',
    value: '42',
    change: -3,
    changeLabel: 'days improvement',
    icon: Users,
    iconBg: 'bg-primary-100 text-primary-600',
  },
];

export default function OverviewPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Overview');
  }, [setPageTitle]);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Revenue Intelligence Dashboard</h1>
          <p className="text-sm text-navy-500 mt-1">
            Real-time overview of revenue recognition, client margins, and financial health.
          </p>
        </div>
        <select className="input-field text-sm w-auto">
          <option value="current_month">Current Month</option>
          <option value="last_month">Last Month</option>
          <option value="current_quarter">Current Quarter</option>
          <option value="ytd">Year to Date</option>
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const isPositive = stat.change > 0;
          return (
            <div key={stat.title} className="card-hover">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-navy-500 font-medium">{stat.title}</p>
                  <p className="text-2xl font-bold text-navy-900 mt-1">{stat.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {isPositive ? (
                      <ArrowUpRight className="w-3.5 h-3.5 text-success-500" />
                    ) : (
                      <ArrowDownRight className="w-3.5 h-3.5 text-danger-500" />
                    )}
                    <span className={cn('text-xs font-medium', isPositive ? 'text-success-600' : 'text-danger-600')}>
                      {formatPercent(Math.abs(stat.change))}
                    </span>
                    <span className="text-xs text-navy-400">{stat.changeLabel}</span>
                  </div>
                </div>
                <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', stat.iconBg)}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="section-title mb-4">Revenue Recognition Trend</h3>
          <div className="h-64 flex items-center justify-center bg-navy-50 rounded-lg border border-dashed border-navy-200">
            <p className="text-sm text-navy-400">Revenue chart renders here with Recharts</p>
          </div>
        </div>
        <div className="card">
          <h3 className="section-title mb-4">Client Profitability Matrix</h3>
          <div className="h-64 flex items-center justify-center bg-navy-50 rounded-lg border border-dashed border-navy-200">
            <p className="text-sm text-navy-400">Profitability matrix renders here</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card">
          <h3 className="section-title mb-4">Recent Revenue Entries</h3>
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-100">
                <th className="table-header">Contract</th>
                <th className="table-header">Client</th>
                <th className="table-header">Amount</th>
                <th className="table-header">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-navy-50">
                <td className="table-cell font-medium">CTR-2024-001</td>
                <td className="table-cell">Acme Corp</td>
                <td className="table-cell">{formatCurrency(1250000)}</td>
                <td className="table-cell"><span className="badge-success">Recognized</span></td>
              </tr>
              <tr className="border-b border-navy-50">
                <td className="table-cell font-medium">CTR-2024-015</td>
                <td className="table-cell">TechVista Ltd</td>
                <td className="table-cell">{formatCurrency(890000)}</td>
                <td className="table-cell"><span className="badge-warning">Pending</span></td>
              </tr>
              <tr>
                <td className="table-cell font-medium">CTR-2024-023</td>
                <td className="table-cell">GlobalSync Inc</td>
                <td className="table-cell">{formatCurrency(2100000)}</td>
                <td className="table-cell"><span className="badge-primary">Draft</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="card">
          <h3 className="section-title mb-4">Active Alerts</h3>
          <div className="space-y-3">
            <div className="p-3 rounded-r-lg border-l-4 border-l-danger-500 bg-danger-50/50">
              <p className="text-sm font-medium text-navy-800">Payment Overdue</p>
              <p className="text-xs text-navy-500 mt-0.5">INV-2024-089 is 15 days overdue</p>
            </div>
            <div className="p-3 rounded-r-lg border-l-4 border-l-warning-500 bg-warning-50/50">
              <p className="text-sm font-medium text-navy-800">Contract Expiring</p>
              <p className="text-xs text-navy-500 mt-0.5">CTR-2024-003 expires in 7 days</p>
            </div>
            <div className="p-3 rounded-r-lg border-l-4 border-l-primary-500 bg-primary-50/50">
              <p className="text-sm font-medium text-navy-800">Revenue Anomaly</p>
              <p className="text-xs text-navy-500 mt-0.5">Unusual pattern in Q4 entries</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
