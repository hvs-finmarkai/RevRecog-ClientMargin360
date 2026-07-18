import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';

/**
 * Merge Tailwind CSS classes with conflict resolution
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format a number as Indian Rupees (INR)
 */
export function formatCurrency(amount: number, options?: {
  showSymbol?: boolean;
  decimals?: number;
  compact?: boolean;
}): string {
  const { showSymbol = true, decimals = 2, compact = false } = options || {};

  if (compact) {
    if (amount >= 10000000) {
      return `${showSymbol ? '₹' : ''}${(amount / 10000000).toFixed(1)}Cr`;
    }
    if (amount >= 100000) {
      return `${showSymbol ? '₹' : ''}${(amount / 100000).toFixed(1)}L`;
    }
    if (amount >= 1000) {
      return `${showSymbol ? '₹' : ''}${(amount / 1000).toFixed(1)}K`;
    }
  }

  const formatter = new Intl.NumberFormat('en-IN', {
    style: showSymbol ? 'currency' : 'decimal',
    currency: 'INR',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return formatter.format(amount);
}

/**
 * Format a date string to a readable format
 */
export function formatDate(dateString: string | Date, formatStr: string = 'dd MMM yyyy'): string {
  if (!dateString) return '-';
  const date = typeof dateString === 'string' ? parseISO(dateString) : dateString;
  if (!isValid(date)) return '-';
  return format(date, formatStr);
}

/**
 * Format a date string to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  if (!dateString) return '-';
  const date = parseISO(dateString);
  if (!isValid(date)) return '-';
  return formatDistanceToNow(date, { addSuffix: true });
}

/**
 * Format a percentage value
 */
export function formatPercent(value: number, decimals: number = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Get status badge color class
 */
export function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    // Contract statuses
    active: 'badge-success',
    draft: 'badge-primary',
    completed: 'badge-success',
    terminated: 'badge-danger',
    expired: 'badge-warning',
    on_hold: 'badge-warning',
    
    // Invoice statuses
    paid: 'badge-success',
    sent: 'badge-primary',
    partially_paid: 'badge-warning',
    overdue: 'badge-danger',
    cancelled: 'badge-danger',
    disputed: 'badge-danger',
    
    // General
    pending: 'badge-warning',
    approved: 'badge-success',
    rejected: 'badge-danger',
    resolved: 'badge-success',
    detected: 'badge-warning',
    critical: 'badge-danger',
    high: 'badge-danger',
    medium: 'badge-warning',
    low: 'badge-primary',
    
    // Client statuses
    at_risk: 'badge-danger',
    inactive: 'badge-warning',
    churned: 'badge-danger',
  };
  return colorMap[status] || 'badge-primary';
}

/**
 * Capitalize first letter of a string
 */
export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Format a status string for display (replace underscores with spaces and capitalize)
 */
export function formatStatus(status: string): string {
  if (!status) return '-';
  return status
    .split('_')
    .map(word => capitalize(word))
    .join(' ');
}

/**
 * Generate initials from a name
 */
export function getInitials(name: string): string {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text || '';
  return text.slice(0, maxLength) + '...';
}

/**
 * Calculate percentage
 */
export function calculatePercent(value: number, total: number): number {
  if (total === 0) return 0;
  return (value / total) * 100;
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Generate a random color from a string (for avatars, charts)
 */
export function stringToColor(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
    '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16',
  ];
  return colors[Math.abs(hash) % colors.length];
}

/**
 * Format number with Indian number system separators
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-IN').format(num);
}

/**
 * Days between two dates
 */
export function daysBetween(date1: string, date2: string): number {
  const d1 = parseISO(date1);
  const d2 = parseISO(date2);
  const diffTime = Math.abs(d2.getTime() - d1.getTime());
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}
