import { ReactNode, useEffect, useState } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

type TrendDirection = 'up' | 'down' | 'neutral';
type MetricColor = 'blue' | 'green' | 'purple' | 'amber' | 'red';

interface MetricCardProps {
  icon?: ReactNode;
  label: string;
  value: string | number;
  trend?: TrendDirection;
  trendValue?: string;
  color?: MetricColor;
  className?: string;
}

const colorStyles: Record<MetricColor, { bg: string; icon: string }> = {
  blue: { bg: 'bg-blue-50', icon: 'text-blue-600' },
  green: { bg: 'bg-green-50', icon: 'text-green-600' },
  purple: { bg: 'bg-purple-50', icon: 'text-purple-600' },
  amber: { bg: 'bg-amber-50', icon: 'text-amber-600' },
  red: { bg: 'bg-red-50', icon: 'text-red-600' },
};

const trendConfig: Record<TrendDirection, { icon: typeof TrendingUp; color: string }> = {
  up: { icon: TrendingUp, color: 'text-green-600' },
  down: { icon: TrendingDown, color: 'text-red-600' },
  neutral: { icon: Minus, color: 'text-gray-500' },
};

function MetricCard({ icon, label, value, trend, trendValue, color = 'blue', className }: MetricCardProps) {
  const [displayValue, setDisplayValue] = useState<string | number>('');

  useEffect(() => {
    const timer = setTimeout(() => setDisplayValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const TrendIcon = trend ? trendConfig[trend].icon : null;

  return (
    <div className={twMerge('bg-white rounded-xl border border-gray-200 p-5 shadow-sm', className)}>
      <div className="flex items-start justify-between">
        {icon && (
          <div className={clsx('p-2.5 rounded-lg', colorStyles[color].bg)}>
            <div className={colorStyles[color].icon}>{icon}</div>
          </div>
        )}
        {trend && TrendIcon && (
          <div className={clsx('flex items-center gap-1 text-sm font-medium', trendConfig[trend].color)}>
            <TrendIcon className="h-4 w-4" />
            {trendValue && <span>{trendValue}</span>}
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-gray-500 font-medium">{label}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1 transition-all duration-500">
          {displayValue}
        </p>
      </div>
    </div>
  );
}

export { MetricCard };
export type { MetricCardProps };
