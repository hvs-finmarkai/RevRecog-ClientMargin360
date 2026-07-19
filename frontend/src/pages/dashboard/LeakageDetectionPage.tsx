import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Eye } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { formatCurrency, formatDate, formatStatus, getStatusColor } from '@/lib/utils';
import apiClient from '@/lib/axios';

interface LeakageDetection {
  id: string;
  detection_type: string;
  client_name?: string;
  client?: { name: string };
  amount: string;
  severity: string;
  status: string;
  detected_at: string;
  description: string;
}

interface LeakageResponse {
  results?: LeakageDetection[];
}

export default function LeakageDetectionPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Leakage Detection');
  }, [setPageTitle]);

  const { data } = useQuery<LeakageResponse>({
    queryKey: ['leakage-detections'],
    queryFn: async () => {
      const response = await apiClient.get('/leakage/leakage-detections/');
      return response.data;
    },
    retry: 1,
  });

  const fallbackLeakages: LeakageDetection[] = [
    { id: '1', detection_type: 'unbilled_hours', client_name: 'Finmark.ai', amount: '1240000', severity: 'critical', status: 'open', detected_at: '2024-07-15T10:00:00Z', description: '42 hours unbilled from last sprint' },
    { id: '2', detection_type: 'missed_escalation', client_name: 'HCL Tech', amount: '1870000', severity: 'critical', status: 'open', detected_at: '2024-07-14T08:30:00Z', description: 'Rate card not updated for 18 months' },
    { id: '3', detection_type: 'scope_creep', client_name: 'Tata Motors', amount: '2410000', severity: 'critical', status: 'open', detected_at: '2024-07-13T14:00:00Z', description: '15% scope expansion without pricing adjustment' },
    { id: '4', detection_type: 'undercharging', client_name: 'Wipro Analytics', amount: '830000', severity: 'high', status: 'acknowledged', detected_at: '2024-07-12T09:15:00Z', description: 'Billing below market rate by 12%' },
    { id: '5', detection_type: 'unbilled_hours', client_name: 'Infosys BPM', amount: '690000', severity: 'high', status: 'open', detected_at: '2024-07-11T16:45:00Z', description: '28 hours unbilled - travel time' },
    { id: '6', detection_type: 'missed_escalation', client_name: 'TCS Digital', amount: '1420000', severity: 'high', status: 'acknowledged', detected_at: '2024-07-10T11:00:00Z', description: 'Annual escalation due since Jan 2024' },
    { id: '7', detection_type: 'scope_creep', client_name: 'Reliance Jio', amount: '1150000', severity: 'medium', status: 'open', detected_at: '2024-07-09T13:30:00Z', description: '8% over scope - new deliverables added' },
    { id: '8', detection_type: 'undercharging', client_name: 'Bharti Airtel', amount: '560000', severity: 'medium', status: 'resolved', detected_at: '2024-07-08T10:20:00Z', description: 'Competitor rate 15% higher' },
    { id: '9', detection_type: 'unbilled_hours', client_name: 'Mahindra Tech', amount: '380000', severity: 'low', status: 'open', detected_at: '2024-07-07T15:00:00Z', description: '12 hours unbilled - internal meetings' },
    { id: '10', detection_type: 'expenses_not_billed', client_name: 'L&T Infotech', amount: '720000', severity: 'medium', status: 'open', detected_at: '2024-07-06T09:00:00Z', description: 'CPI adjustment pending for 6 months' },
  ];

  const leakages = data?.results?.length ? data.results : fallbackLeakages;

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-50 text-red-700 border border-red-200',
      high: 'bg-orange-50 text-orange-700 border border-orange-200',
      medium: 'bg-amber-50 text-amber-700 border border-amber-200',
      low: 'bg-blue-50 text-blue-700 border border-blue-200',
    };
    return `inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[severity] || 'bg-gray-50 text-gray-700'}`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Leakage Detection</h1>
          <p className="text-sm text-navy-500 mt-1">AI-detected revenue leakages and unbilled work</p>
        </div>
        <button className="btn-primary">
          <AlertTriangle className="w-4 h-4 mr-2" />
          Scan Now
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {leakages.map((l) => (
          <div key={l.id} className="card">
            <div className="flex items-start justify-between mb-3">
              <span className={getSeverityBadge(l.severity)}>{l.severity}</span>
              <button className="text-primary-500 hover:text-primary-700">
                <Eye className="w-4 h-4" />
              </button>
            </div>
            <h3 className="font-medium text-navy-900 text-sm">{formatStatus(l.detection_type)}</h3>
            <p className="text-xs text-navy-500 mt-1">{l.client_name || l.client?.name || '-'}</p>
            <div className="flex items-center justify-between mt-3">
              <p className="text-lg font-bold text-danger-600">
                {formatCurrency(parseFloat(l.amount), { compact: true })}
              </p>
              <span className={getStatusColor(l.status)}>{formatStatus(l.status)}</span>
            </div>
            <p className="text-xs text-navy-400 mt-2">{formatDate(l.detected_at)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
