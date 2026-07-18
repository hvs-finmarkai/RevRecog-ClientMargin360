import { InputHTMLAttributes, ReactNode, forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

type InputVariant = 'default' | 'filled';

interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  helperText?: string;
  prefixIcon?: ReactNode;
  suffixIcon?: ReactNode;
  variant?: InputVariant;
  containerClassName?: string;
}

const variantStyles: Record<InputVariant, string> = {
  default: 'bg-white border-gray-300 focus:border-blue-500',
  filled: 'bg-gray-50 border-gray-200 focus:border-blue-500 focus:bg-white',
};

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, prefixIcon, suffixIcon, variant = 'default', className, containerClassName, ...props }, ref) => {
    return (
      <div className={twMerge('w-full', containerClassName)}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
        )}
        <div className="relative">
          {prefixIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              {prefixIcon}
            </div>
          )}
          <input
            ref={ref}
            className={twMerge(
              clsx(
                'w-full rounded-lg border px-3 py-2 text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 placeholder:text-gray-400',
                variantStyles[variant],
                prefixIcon && 'pl-10',
                suffixIcon && 'pr-10',
                error && 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
                className
              )
            )}
            {...props}
          />
          {suffixIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
              {suffixIcon}
            </div>
          )}
        </div>
        {error && <p className="mt-1.5 text-sm text-red-600">{error}</p>}
        {!error && helperText && <p className="mt-1.5 text-sm text-gray-500">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export type { InputProps };
