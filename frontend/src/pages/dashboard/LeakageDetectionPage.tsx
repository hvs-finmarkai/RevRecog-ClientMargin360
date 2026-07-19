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

  const { data, isLoading, isError, error } = useQuery<LeakageResponse>({
    queryKey: ['leakage-detections'],
    queryFn: async () => {
      const response = await apiClient.get('/leakage/leakage-detections/');
      return response.data;
    },
  });

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-danger-100 text-danger-700',
      high: 'bg-danger-50 text-danger-600',
      medium: 'bg-warning-50 text-warning-700',
      low: 'bg-primary-50 text-primary-700',
    };
    return `badge ${colors[severity] || 'badge-primary'}`;
  };

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
          <p className="text-lg font-medium text-navy-900">Failed to load leakage data</p>
          <p className="text-sm text-navy-500 mt-1">{(error as Error)?.message || 'An unexpected error occurred'}</p>
        </div>
      </div>
    );
  }

  const leakages: LeakageDetection[] = Array.isArray(data) ? data : data?.results || [];

  if (leakages.length === 0) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="page-title">Leakage Detection</h1>
            <p className="text-sm text-navy-500 mt-1">AI-detected revenue leakages and unbilled work</p>
          </div>
        </div>
        <div className="flex items-center justify-center h-48">
          <p className="text-navy-500">No leakage detections found</p>
        </div>
      </div>
    );
  }

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
