import { useEffect } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatRelativeTime, cn } from '@/lib/utils';

export default function AlertsPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Alerts');
  }, [setPageTitle]);

  const alerts = [
    { id: '1', type: 'payment_overdue', severity: 'critical', title: 'Payment Overdue - Acme Corp', message: 'Invoice INV-2024-089 is 15 days past due. Amount: ₹8.5L', time: '2024-12-15T10:30:00Z', read: false },
    { id: '2', type: 'contract_expiry', severity: 'warning', title: 'Contract Expiring Soon', message: 'CTR-2024-003 with GlobalSync expires in 7 days. Renewal pending.', time: '2024-12-14T14:00:00Z', read: false },
    { id: '3', type: 'leakage_detected', severity: 'error', title: 'Revenue Leakage Detected', message: 'Unbilled work worth ₹2L found for DataFlow Systems project.', time: '2024-12-13T09:15:00Z', read: false },
    { id: '4', type: 'revenue_anomaly', severity: 'warning', title: 'Revenue Recognition Anomaly', message: 'Unusual pattern detected in Q4 entries for TechVista contract.', time: '2024-12-12T16:45:00Z', read: true },
    { id: '5', type: 'margin_threshold', severity: 'info', title: 'Margin Below Threshold', message: 'DataFlow Systems margin dropped to 20%, below 25% threshold.', time: '2024-12-11T11:00:00Z', read: true },
  ];

  const getSeverityIcon = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-danger-100 border-danger-200',
      error: 'bg-danger-50 border-danger-100',
      warning: 'bg-warning-50 border-warning-100',
      info: 'bg-primary-50 border-primary-100',
    };
    return colors[severity] || 'bg-navy-50 border-navy-100';
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Alerts</h1>
          <p className="text-sm text-navy-500 mt-1">System notifications and action items</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary text-sm"><Check className="w-4 h-4 mr-1" />Mark All Read</button>
          <button className="btn-secondary text-sm"><Trash2 className="w-4 h-4 mr-1" />Clear All</button>
        </div>
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={cn(
              'card flex items-start gap-4 border-l-4 transition-colors',
              !alert.read && 'bg-white',
              alert.read && 'bg-navy-50/50 opacity-75',
              alert.severity === 'critical' && 'border-l-danger-500',
              alert.severity === 'error' && 'border-l-danger-400',
              alert.severity === 'warning' && 'border-l-warning-500',
              alert.severity === 'info' && 'border-l-primary-500'
            )}
          >
            <div className={cn('w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 border', getSeverityIcon(alert.severity))}>
              <Bell className="w-4 h-4 text-navy-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <h3 className={cn('text-sm font-semibold text-navy-900', !alert.read && 'font-bold')}>
                  {alert.title}
                </h3>
                <span className="text-xs text-navy-400 whitespace-nowrap">{formatRelativeTime(alert.time)}</span>
              </div>
              <p className="text-sm text-navy-600 mt-1">{alert.message}</p>
              {!alert.read && (
                <div className="flex gap-2 mt-3">
                  <button className="text-xs text-primary-600 hover:text-primary-700 font-medium">View Details</button>
                  <span className="text-navy-300">•</span>
                  <button className="text-xs text-navy-500 hover:text-navy-700">Dismiss</button>
                </div>
              )}
            </div>
            {!alert.read && <div className="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0 mt-2" />}
          </div>
        ))}
      </div>
    </div>
  );
}
