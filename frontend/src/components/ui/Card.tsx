import { ReactNode } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

type PaddingVariant = 'none' | 'sm' | 'md' | 'lg';

interface CardProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  padding?: PaddingVariant;
  hover?: boolean;
  className?: string;
}

const paddingStyles: Record<PaddingVariant, string> = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-7',
};

function Card({ title, subtitle, action, children, padding = 'md', hover = false, className }: CardProps) {
  return (
    <div
      className={twMerge(
        clsx(
          'bg-white rounded-xl border border-gray-200 shadow-sm',
          hover && 'hover:shadow-md hover:border-gray-300 transition-all duration-200',
          paddingStyles[padding],
          className
        )
      )}
    >
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="ml-4">{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

export { Card };
export type { CardProps };
