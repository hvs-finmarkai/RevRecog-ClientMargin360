import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

interface BillingModelDataPoint {
  name: string;
  value: number;
  amount: number;
}

interface BillingModelChartProps {
  data: BillingModelDataPoint[];
  height?: number;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981', '#f43f5e'];

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: BillingModelDataPoint }> }) {
  if (!active || !payload || !payload[0]) return null;

  const item = payload[0].payload;
  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
      <p className="text-sm font-medium text-gray-900">{item.name}</p>
      <p className="text-sm text-gray-600 mt-1">
        ₹{item.amount.toLocaleString('en-IN')}
      </p>
      <p className="text-xs text-gray-500 mt-0.5">{item.value}% of revenue</p>
    </div>
  );
}

function CustomLegend({ payload }: { payload?: Array<{ value: string; color: string }> }) {
  if (!payload) return null;

  return (
    <div className="flex flex-wrap justify-center gap-4 mt-4">
      {payload.map((entry, index) => (
        <div key={index} className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-sm text-gray-600">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}

function BillingModelChart({ data, height = 320 }: BillingModelChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="45%"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={3}
          dataKey="value"
          nameKey="name"
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend content={<CustomLegend />} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export { BillingModelChart };
export type { BillingModelChartProps, BillingModelDataPoint };
