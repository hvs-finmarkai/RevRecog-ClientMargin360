import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Cell,
} from 'recharts';

interface MarginDataPoint {
  client: string;
  margin: number;
}

interface MarginChartProps {
  data: MarginDataPoint[];
  height?: number;
  threshold?: number;
}

function getBarColor(margin: number): string {
  if (margin >= 15) return '#10b981';
  if (margin >= 12) return '#f59e0b';
  return '#ef4444';
}

function CustomTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (!active || !payload || !payload[0]) return null;

  const margin = payload[0].value;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
      <p className="text-sm font-medium text-gray-900">{label}</p>
      <div className="flex items-center gap-2 mt-1">
        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: getBarColor(margin) }} />
        <span className="text-sm text-gray-600">Margin: {margin.toFixed(1)}%</span>
      </div>
    </div>
  );
}

function MarginChart({ data, height = 350, threshold = 12 }: MarginChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
        <XAxis
          dataKey="client"
          tick={{ fontSize: 11, fill: '#64748b' }}
          axisLine={false}
          tickLine={false}
          interval={0}
          angle={-20}
          textAnchor="end"
          height={60}
        />
        <YAxis
          tick={{ fontSize: 12, fill: '#64748b' }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(val) => `${val}%`}
          domain={[0, 'auto']}
        />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine
          y={threshold}
          stroke="#ef4444"
          strokeDasharray="4 4"
          strokeWidth={1.5}
          label={{ value: `${threshold}% threshold`, position: 'right', fontSize: 11, fill: '#ef4444' }}
        />
        <Bar dataKey="margin" radius={[4, 4, 0, 0]} maxBarSize={48}>
          {data.map((entry, index) => (
            <Cell key={index} fill={getBarColor(entry.margin)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export { MarginChart };
export type { MarginChartProps, MarginDataPoint };
