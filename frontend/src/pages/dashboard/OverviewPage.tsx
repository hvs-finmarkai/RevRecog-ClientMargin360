import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, BarChart3, AlertTriangle, Users, IndianRupee } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency } from '@/lib/utils';
import apiClient from '@/lib/axios';

interface OverviewData {
  total_contract_value: string;
  monthly_revenue: string;
  revenue_leakage: string;
  overdue_receivables: string;
  active_clients: number;
  active_contracts: number;
  generated_at: string;
}

export default function OverviewPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Dashboard');
  }, [setPageTitle]);

  const { data, isLoading, isError, error } = useQuery<OverviewData>({
    queryKey: ['analytics-overview'],
    queryFn: async () => {
      const response = await apiClient.get('/analytics/analytics/overview/');
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
          <p className="text-lg font-medium text-navy-900">Failed to load dashboard data</p>
          <p className="text-sm text-navy-500 mt-1">{(error as Error)?.message || 'An unexpected error occurred'}</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-navy-500">No data available</p>
      </div>
    );
  }

  const metrics = [
    {
      label: 'Total Contract Value',
      value: formatCurrency(parseFloat(data.total_contract_value), { compact: true }),
      icon: FileText,
      iconBg: '#EFF6FF',
      iconColor: '#3B82F6',
    },
    {
      label: 'Monthly Revenue',
      value: formatCurrency(parseFloat(data.monthly_revenue), { compact: true }),
      icon: BarChart3,
      iconBg: '#ECFDF5',
      iconColor: '#10B981',
    },
    {
      label: 'Revenue Leakage',
      value: formatCurrency(parseFloat(data.revenue_leakage), { compact: true }),
      icon: AlertTriangle,
      iconBg: '#FEF2F2',
      iconColor: '#EF4444',
    },
    {
      label: 'Active Clients',
      value: String(data.active_clients),
      icon: Users,
      iconBg: '#F5F3FF',
      iconColor: '#8B5CF6',
    },
    {
      label: 'Overdue Receivables',
      value: formatCurrency(parseFloat(data.overdue_receivables), { compact: true }),
      icon: IndianRupee,
      iconBg: '#FFF7ED',
      iconColor: '#F97316',
    },
  ];

  const savingPotential = parseFloat(data.revenue_leakage) * 12;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {metrics.map((metric) => (
          <div key={metric.label} className="metric-card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-500" style={{ fontSize: 13 }}>
                  {metric.label}
                </p>
                <p className="font-bold mt-1" style={{ fontSize: 24, color: 'var(--text)' }}>
                  {metric.value}
                </p>
              </div>
              <div
                className="flex items-center justify-center rounded-full"
                style={{
                  width: 44,
                  height: 44,
                  backgroundColor: metric.iconBg,
                }}
              >
                <metric.icon size={22} style={{ color: metric.iconColor }} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div
        className="rounded-xl p-5 flex items-center justify-between"
        style={{
          background: 'linear-gradient(135deg, #FFFBEB, #FEF3C7)',
          border: '1px solid #FDE68A',
        }}
      >
        <div>
          <p className="text-sm font-medium" style={{ color: '#92400E' }}>
            Saving Potential
          </p>
          <p className="text-2xl font-bold mt-1" style={{ color: '#78350F' }}>
            {formatCurrency(savingPotential, { compact: true })}
          </p>
          <p className="text-xs mt-1" style={{ color: '#A16207' }}>
            Estimated annual savings from leakage prevention & billing optimization
          </p>
        </div>
        <div
          className="flex items-center justify-center rounded-full"
          style={{ width: 56, height: 56, backgroundColor: '#FDE68A' }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#92400E" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
          </svg>
        </div>
      </div>
    </div>
  );
}
