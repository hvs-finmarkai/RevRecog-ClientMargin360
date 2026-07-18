// ============================================
// User & Authentication Types
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  department?: string;
  lastLogin?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export type UserRole = 'admin' | 'finance_manager' | 'analyst' | 'viewer';

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// ============================================
// Client Types
// ============================================

export interface Client {
  id: string;
  name: string;
  code: string;
  industry: string;
  contactPerson: string;
  contactEmail: string;
  contactPhone?: string;
  address?: string;
  gstNumber?: string;
  panNumber?: string;
  creditTerms: number;
  status: ClientStatus;
  riskScore: number;
  totalRevenue: number;
  totalOutstanding: number;
  margin: number;
  contracts: number;
  createdAt: string;
  updatedAt: string;
}

export type ClientStatus = 'active' | 'inactive' | 'at_risk' | 'churned';

export interface ClientProfitability {
  clientId: string;
  clientName: string;
  revenue: number;
  directCosts: number;
  indirectCosts: number;
  grossMargin: number;
  grossMarginPercent: number;
  netMargin: number;
  netMarginPercent: number;
  revenueLeakage: number;
  leakagePercent: number;
  collectionEfficiency: number;
  dso: number;
  ltv: number;
  cac: number;
  period: string;
}

// ============================================
// Contract Types
// ============================================

export interface Contract {
  id: string;
  contractNumber: string;
  clientId: string;
  clientName: string;
  title: string;
  description?: string;
  type: ContractType;
  status: ContractStatus;
  startDate: string;
  endDate: string;
  totalValue: number;
  currency: string;
  billingFrequency: BillingFrequency;
  paymentTerms: number;
  revenueRecognitionMethod: RevenueRecognitionMethod;
  performanceObligations: PerformanceObligation[];
  amendments: ContractAmendment[];
  createdAt: string;
  updatedAt: string;
}

export type ContractType = 'fixed_price' | 'time_material' | 'milestone' | 'retainer' | 'hybrid';

export type ContractStatus = 'draft' | 'active' | 'completed' | 'terminated' | 'expired' | 'on_hold';

export type BillingFrequency = 'monthly' | 'quarterly' | 'milestone' | 'on_delivery' | 'upfront';

export type RevenueRecognitionMethod = 
  | 'percentage_of_completion'
  | 'completed_contract'
  | 'milestone'
  | 'straight_line'
  | 'output_method'
  | 'input_method';

export interface PerformanceObligation {
  id: string;
  contractId: string;
  description: string;
  type: 'distinct' | 'combined' | 'series';
  standaloneSellingPrice: number;
  allocatedPrice: number;
  satisfactionMethod: 'over_time' | 'point_in_time';
  progressMeasure: 'input' | 'output' | 'time_elapsed';
  percentComplete: number;
  revenueRecognized: number;
  status: 'pending' | 'in_progress' | 'satisfied';
}

export interface ContractAmendment {
  id: string;
  contractId: string;
  type: 'scope_change' | 'price_change' | 'extension' | 'termination';
  description: string;
  effectiveDate: string;
  valueImpact: number;
  status: 'pending' | 'approved' | 'rejected';
  createdAt: string;
}

// ============================================
// Invoice & Billing Types
// ============================================

export interface Invoice {
  id: string;
  invoiceNumber: string;
  clientId: string;
  clientName: string;
  contractId: string;
  contractNumber: string;
  type: InvoiceType;
  status: InvoiceStatus;
  issueDate: string;
  dueDate: string;
  amount: number;
  taxAmount: number;
  totalAmount: number;
  currency: string;
  paidAmount: number;
  outstandingAmount: number;
  lineItems: InvoiceLineItem[];
  payments: Payment[];
  createdAt: string;
  updatedAt: string;
}

export type InvoiceType = 'standard' | 'proforma' | 'credit_note' | 'debit_note';

export type InvoiceStatus = 'draft' | 'sent' | 'partially_paid' | 'paid' | 'overdue' | 'cancelled' | 'disputed';

export interface InvoiceLineItem {
  id: string;
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
  taxRate: number;
  taxAmount: number;
  sacCode?: string;
}

export interface Payment {
  id: string;
  invoiceId: string;
  amount: number;
  paymentDate: string;
  paymentMethod: 'bank_transfer' | 'cheque' | 'upi' | 'card' | 'cash';
  referenceNumber: string;
  status: 'completed' | 'pending' | 'failed' | 'reversed';
}

// ============================================
// Billable Types
// ============================================

export interface Billable {
  id: string;
  contractId: string;
  clientId: string;
  clientName: string;
  description: string;
  type: BillableType;
  quantity: number;
  rate: number;
  amount: number;
  date: string;
  status: BillableStatus;
  invoiceId?: string;
  employeeId?: string;
  employeeName?: string;
  projectCode?: string;
  createdAt: string;
}

export type BillableType = 'time' | 'expense' | 'material' | 'milestone' | 'fixed_fee';

export type BillableStatus = 'unbilled' | 'billed' | 'approved' | 'rejected' | 'written_off';

// ============================================
// Revenue Recognition Types
// ============================================

export interface RevenueRecognitionEntry {
  id: string;
  contractId: string;
  contractNumber: string;
  clientId: string;
  clientName: string;
  period: string;
  method: RevenueRecognitionMethod;
  totalContractValue: number;
  revenueRecognized: number;
  revenueDeferred: number;
  cumulativeRecognized: number;
  percentComplete: number;
  status: RevRecogStatus;
  journalEntryId?: string;
  notes?: string;
  aiConfidence?: number;
  aiRecommendation?: string;
  createdAt: string;
  updatedAt: string;
}

export type RevRecogStatus = 'draft' | 'pending_review' | 'approved' | 'posted' | 'reversed';

export interface RevenueSchedule {
  id: string;
  contractId: string;
  periods: RevenueSchedulePeriod[];
  totalValue: number;
  totalRecognized: number;
  totalDeferred: number;
}

export interface RevenueSchedulePeriod {
  period: string;
  planned: number;
  actual: number;
  variance: number;
  status: 'future' | 'current' | 'completed';
}

// ============================================
// Leakage Detection Types
// ============================================

export interface LeakageItem {
  id: string;
  type: LeakageType;
  severity: 'low' | 'medium' | 'high' | 'critical';
  clientId: string;
  clientName: string;
  contractId?: string;
  contractNumber?: string;
  description: string;
  estimatedAmount: number;
  status: LeakageStatus;
  detectedAt: string;
  resolvedAt?: string;
  resolution?: string;
  assignedTo?: string;
}

export type LeakageType = 
  | 'unbilled_work'
  | 'rate_mismatch'
  | 'scope_creep'
  | 'missed_escalation'
  | 'billing_error'
  | 'delayed_billing'
  | 'write_off'
  | 'discount_overuse';

export type LeakageStatus = 'detected' | 'investigating' | 'confirmed' | 'resolved' | 'dismissed';

// ============================================
// Collections Types
// ============================================

export interface CollectionItem {
  id: string;
  invoiceId: string;
  invoiceNumber: string;
  clientId: string;
  clientName: string;
  amount: number;
  dueDate: string;
  daysPastDue: number;
  agingBucket: AgingBucket;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: CollectionStatus;
  lastFollowUp?: string;
  nextFollowUp?: string;
  notes?: string;
  assignedTo?: string;
}

export type AgingBucket = 'current' | '1-30' | '31-60' | '61-90' | '90+';

export type CollectionStatus = 'pending' | 'in_progress' | 'promised' | 'escalated' | 'collected' | 'written_off';

// ============================================
// Alert Types
// ============================================

export interface Alert {
  id: string;
  type: AlertType;
  severity: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  entityType: 'contract' | 'invoice' | 'client' | 'revenue' | 'collection';
  entityId: string;
  isRead: boolean;
  isActionRequired: boolean;
  actionUrl?: string;
  createdAt: string;
  readAt?: string;
}

export type AlertType = 
  | 'contract_expiry'
  | 'payment_overdue'
  | 'revenue_anomaly'
  | 'leakage_detected'
  | 'margin_threshold'
  | 'collection_escalation'
  | 'billing_reminder'
  | 'compliance_warning';

// ============================================
// Dashboard & Analytics Types
// ============================================

export interface DashboardMetrics {
  totalRevenue: number;
  revenueGrowth: number;
  totalOutstanding: number;
  dso: number;
  averageMargin: number;
  marginTrend: number;
  revenueLeakage: number;
  leakageTrend: number;
  activeContracts: number;
  expiringContracts: number;
  collectionRate: number;
  alertsCount: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  [key: string]: string | number;
}

export interface TimeSeriesData {
  date: string;
  [key: string]: string | number;
}

// ============================================
// Common / Shared Types
// ============================================

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrevious: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  errors?: Record<string, string[]>;
}

export interface FilterParams {
  search?: string;
  status?: string;
  clientId?: string;
  startDate?: string;
  endDate?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}

export interface SelectOption {
  value: string;
  label: string;
}

export type Theme = 'light' | 'dark' | 'system';

export interface AppState {
  sidebarCollapsed: boolean;
  theme: Theme;
  currentPageTitle: string;
}
