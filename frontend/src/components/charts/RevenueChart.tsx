import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

interface RevenueDataPoint {
  month: string;
  recognized: number;
  billed: number;
}

interface RevenueChartProps {
  data: RevenueDataPoint[];
  height?: number;
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; dataKey: string; color: string }>; label?: string }) {
  if (!active || !payload) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
      <p className="text-sm font-medium text-gray-900 mb-2">{label}</p>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-sm text-gray-600 capitalize">{entry.dataKey}</span>
          </div>
          <span className="text-sm font-semibold text-gray-900">
            ₹{entry.value.toLocaleString('en-IN')}
          </span>
        </div>
      ))}
    </div>
  );
}

function RevenueChart({ data, height = 350 }: RevenueChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="recognizedGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="billedGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.15} />
            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
        <YAxis
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(val) => `₹${(val / 100000).toFixed(0)}L`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ paddingTop: '20px' }} />
        <Area
          type="monotone"
          dataKey="recognized"
          stroke="#3b82f6"
          strokeWidth={2}
          fill="url(#recognizedGradient)"
          name="Recognized"
        />
        <Area
          type="monotone"
          dataKey="billed"
          stroke="#8b5cf6"
          strokeWidth={2}
          fill="url(#billedGradient)"
          name="Billed"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export { RevenueChart };
export type { RevenueChartProps, RevenueDataPoint };
