import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import DashboardLayout from '@/layouts/DashboardLayout';
import AuthLayout from '@/layouts/AuthLayout';
import { useAuthStore } from '@/store/authStore';

// Lazy-loaded page components
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const OverviewPage = lazy(() => import('@/pages/dashboard/OverviewPage'));
const ContractsPage = lazy(() => import('@/pages/dashboard/ContractsPage'));
const InvoicesPage = lazy(() => import('@/pages/dashboard/InvoicesPage'));
const BillablesPage = lazy(() => import('@/pages/dashboard/BillablesPage'));
const RevenueRecognitionPage = lazy(() => import('@/pages/dashboard/RevenueRecognitionPage'));
const ClientProfitabilityPage = lazy(() => import('@/pages/dashboard/ClientProfitabilityPage'));
const LeakageDetectionPage = lazy(() => import('@/pages/dashboard/LeakageDetectionPage'));
const CollectionsPage = lazy(() => import('@/pages/dashboard/CollectionsPage'));
const ReportsPage = lazy(() => import('@/pages/dashboard/ReportsPage'));
const AlertsPage = lazy(() => import('@/pages/dashboard/AlertsPage'));
const SettingsPage = lazy(() => import('@/pages/dashboard/SettingsPage'));

// Loading fallback
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin" />
        <p className="text-sm text-navy-500">Loading...</p>
      </div>
    </div>
  );
}

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Auth routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>

        {/* Dashboard routes (protected) */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<OverviewPage />} />
          <Route path="/dashboard/contracts" element={<ContractsPage />} />
          <Route path="/dashboard/invoices" element={<InvoicesPage />} />
          <Route path="/dashboard/billables" element={<BillablesPage />} />
          <Route path="/dashboard/revenue-recognition" element={<RevenueRecognitionPage />} />
          <Route path="/dashboard/client-profitability" element={<ClientProfitabilityPage />} />
          <Route path="/dashboard/leakage" element={<LeakageDetectionPage />} />
          <Route path="/dashboard/collections" element={<CollectionsPage />} />
          <Route path="/dashboard/reports" element={<ReportsPage />} />
          <Route path="/dashboard/alerts" element={<AlertsPage />} />
          <Route path="/dashboard/settings" element={<SettingsPage />} />
        </Route>

        {/* Redirect root to dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* 404 - Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Suspense>
  );
}
