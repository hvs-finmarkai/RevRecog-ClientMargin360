import { useState, useRef, useEffect, ReactNode } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ChevronDown, Search, X, Check } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
  icon?: ReactNode;
}

interface SelectProps {
  options: SelectOption[];
  value?: string | string[];
  onChange: (value: string | string[]) => void;
  placeholder?: string;
  searchable?: boolean;
  multiple?: boolean;
  label?: string;
  error?: string;
  className?: string;
}

function Select({ options, value, onChange, placeholder = 'Select...', searchable = false, multiple = false, label, error, className }: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = options.filter((opt) =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  );

  const selectedValues = multiple ? (value as string[] || []) : value ? [value as string] : [];

  const handleSelect = (optionValue: string) => {
    if (multiple) {
      const current = value as string[] || [];
      const updated = current.includes(optionValue)
        ? current.filter((v) => v !== optionValue)
        : [...current, optionValue];
      onChange(updated);
    } else {
      onChange(optionValue);
      setIsOpen(false);
      setSearch('');
    }
  };

  const removeValue = (optionValue: string) => {
    if (multiple) {
      const current = value as string[] || [];
      onChange(current.filter((v) => v !== optionValue));
    }
  };

  const displayLabel = () => {
    if (selectedValues.length === 0) return placeholder;
    if (!multiple) {
      const opt = options.find((o) => o.value === selectedValues[0]);
      return opt?.label || placeholder;
    }
    return null;
  };

  return (
    <div ref={containerRef} className={twMerge('relative w-full', className)}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'w-full flex items-center justify-between rounded-lg border px-3 py-2 text-sm text-left transition-colors',
          error ? 'border-red-500' : 'border-gray-300 hover:border-gray-400 focus:border-blue-500',
          'focus:outline-none focus:ring-2 focus:ring-blue-500/20 bg-white'
        )}
      >
        <div className="flex flex-wrap gap-1 flex-1 min-w-0">
          {multiple && selectedValues.length > 0 ? (
            selectedValues.map((v) => {
              const opt = options.find((o) => o.value === v);
              return (
                <span key={v} className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs font-medium">
                  {opt?.label}
                  <X className="h-3 w-3 cursor-pointer" onClick={(e) => { e.stopPropagation(); removeValue(v); }} />
                </span>
              );
            })
          ) : (
            <span className={clsx(selectedValues.length === 0 && 'text-gray-400')}>
              {displayLabel()}
            </span>
          )}
        </div>
        <ChevronDown className={clsx('h-4 w-4 text-gray-400 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
          {searchable && (
            <div className="p-2 border-b border-gray-100">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search..."
                  className="w-full pl-8 pr-3 py-1.5 text-sm rounded border border-gray-200 focus:outline-none focus:border-blue-500"
                  autoFocus
                />
              </div>
            </div>
          )}
          <div className="max-h-60 overflow-y-auto py-1">
            {filteredOptions.length === 0 ? (
              <div className="px-3 py-2 text-sm text-gray-500">No options found</div>
            ) : (
              filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option.value)}
                  className={clsx(
                    'w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-gray-50 transition-colors',
                    selectedValues.includes(option.value) && 'bg-blue-50 text-blue-700'
                  )}
                >
                  {option.icon && <span>{option.icon}</span>}
                  <span className="flex-1">{option.label}</span>
                  {selectedValues.includes(option.value) && <Check className="h-4 w-4 text-blue-600" />}
                </button>
              ))
            )}
          </div>
        </div>
      )}
      {error && <p className="mt-1.5 text-sm text-red-600">{error}</p>}
    </div>
  );
}

export { Select };
export type { SelectProps, SelectOption };
