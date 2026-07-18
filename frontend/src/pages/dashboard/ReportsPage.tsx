import { useEffect } from 'react';
import { BarChart3, Download, FileText, Calendar } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

export default function ReportsPage() {
  const { setPageTitle } = useAppStore();

  useEffect(() => {
    setPageTitle('Reports & Analytics');
  }, [setPageTitle]);

  const reports = [
    { name: 'Revenue Recognition Summary', type: 'Monthly', lastRun: '2024-12-15', format: 'PDF' },
    { name: 'Client Profitability Report', type: 'Quarterly', lastRun: '2024-12-01', format: 'Excel' },
    { name: 'Aging Analysis Report', type: 'Weekly', lastRun: '2024-12-14', format: 'PDF' },
    { name: 'Leakage Detection Report', type: 'Monthly', lastRun: '2024-12-10', format: 'PDF' },
    { name: 'DSO Trend Report', type: 'Monthly', lastRun: '2024-12-12', format: 'Excel' },
    { name: 'Contract Performance Report', type: 'Quarterly', lastRun: '2024-12-01', format: 'PDF' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="text-sm text-navy-500 mt-1">Generate and schedule financial reports</p>
        </div>
        <button className="btn-primary"><BarChart3 className="w-4 h-4 mr-2" />Custom Report</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((report) => (
          <div key={report.name} className="card-hover">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-navy-900">{report.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Calendar className="w-3 h-3 text-navy-400" />
                    <span className="text-xs text-navy-500">{report.type} • Last: {report.lastRun}</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between mt-4 pt-3 border-t border-navy-100">
              <span className="badge-primary">{report.format}</span>
              <button className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium">
                <Download className="w-3.5 h-3.5" />
                Download
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
