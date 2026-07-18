import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Receipt,
  Clock,
  TrendingUp,
  PieChart,
  AlertTriangle,
  Wallet,
  BarChart3,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  LogOut,
  User,
  Activity,
} from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { useAuthStore } from '@/store/authStore';
import { cn, getInitials } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

const navigationItems: NavItem[] = [
  { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Contracts', href: '/dashboard/contracts', icon: FileText },
  { label: 'Billing & Invoices', href: '/dashboard/invoices', icon: Receipt },
  { label: 'Billables', href: '/dashboard/billables', icon: Clock },
  { label: 'Revenue Recognition', href: '/dashboard/revenue-recognition', icon: TrendingUp },
  { label: 'Client Profitability', href: '/dashboard/client-profitability', icon: PieChart },
  { label: 'Leakage Detection', href: '/dashboard/leakage', icon: AlertTriangle },
  { label: 'Collections', href: '/dashboard/collections', icon: Wallet },
  { label: 'Reports & Analytics', href: '/dashboard/reports', icon: BarChart3 },
  { label: 'Alerts', href: '/dashboard/alerts', icon: Bell },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export default function DashboardLayout() {
  const location = useLocation();
  const { 
    sidebarCollapsed, 
    toggleSidebar, 
    currentPageTitle, 
    systemStatus, 
    unreadAlerts 
  } = useAppStore();
  const { user, logout } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const getStatusBadge = () => {
    switch (systemStatus) {
      case 'operational':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-success-50 text-success-700">
            <span className="w-1.5 h-1.5 rounded-full bg-success-500 animate-pulse-slow" />
            All Systems Operational
          </span>
        );
      case 'degraded':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-warning-50 text-warning-700">
            <span className="w-1.5 h-1.5 rounded-full bg-warning-500" />
            Degraded Performance
          </span>
        );
      case 'maintenance':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700">
            <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
            Under Maintenance
          </span>
        );
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile menu overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex flex-col bg-navy-700 shadow-sidebar transition-all duration-300 ease-in-out',
          sidebarCollapsed ? 'w-[72px]' : 'w-[280px]',
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-white/10">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-white font-bold text-sm leading-tight">Finmark.ai</h1>
                <p className="text-navy-300 text-[10px] leading-tight">RevRecog + ClientMargin360</p>
              </div>
            </div>
          )}
          {sidebarCollapsed && (
            <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center mx-auto">
              <Activity className="w-5 h-5 text-white" />
            </div>
          )}
          {/* Close button for mobile */}
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden text-navy-300 hover:text-white"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto scrollbar-thin py-4 px-3 space-y-1">
          {navigationItems.map((item) => {
            const isActive = location.pathname === item.href || 
              (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
            const Icon = item.icon;
            
            return (
              <NavLink
                key={item.href}
                to={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={cn(
                  isActive ? 'sidebar-link-active' : 'sidebar-link-inactive',
                  sidebarCollapsed && 'justify-center px-2'
                )}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!sidebarCollapsed && (
                  <span className="truncate">{item.label}</span>
                )}
                {!sidebarCollapsed && item.label === 'Alerts' && unreadAlerts > 0 && (
                  <span className="ml-auto inline-flex items-center justify-center w-5 h-5 text-[10px] font-bold text-white bg-danger-500 rounded-full">
                    {unreadAlerts > 9 ? '9+' : unreadAlerts}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <div className="hidden lg:block border-t border-white/10 p-3">
          <button
            onClick={toggleSidebar}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-navy-300 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <>
                <ChevronLeft className="w-4 h-4" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>

        {/* User section */}
        {!sidebarCollapsed && (
          <div className="border-t border-white/10 p-3">
            <div className="flex items-center gap-3 px-2 py-2">
              <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs font-semibold">
                {user ? getInitials(user.name) : 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-navy-400 truncate">
                  {user?.role ? user.role.replace('_', ' ') : 'Analyst'}
                </p>
              </div>
              <button
                onClick={logout}
                className="text-navy-400 hover:text-white transition-colors"
                aria-label="Logout"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
        {sidebarCollapsed && (
          <div className="border-t border-white/10 p-3 flex justify-center">
            <button
              onClick={logout}
              className="text-navy-400 hover:text-white transition-colors p-2"
              aria-label="Logout"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </aside>

      {/* Main content area */}
      <div
        className={cn(
          'flex-1 flex flex-col min-h-screen transition-all duration-300',
          sidebarCollapsed ? 'lg:ml-[72px]' : 'lg:ml-[280px]'
        )}
      >
        {/* Top Header */}
        <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 lg:px-6 bg-white border-b border-navy-100">
          {/* Left side */}
          <div className="flex items-center gap-4">
            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="lg:hidden text-navy-600 hover:text-navy-900"
              aria-label="Open menu"
            >
              <Menu className="w-6 h-6" />
            </button>
            
            <h2 className="text-lg font-semibold text-navy-900">
              {currentPageTitle}
            </h2>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {/* System status badge */}
            <div className="hidden md:block">
              {getStatusBadge()}
            </div>

            {/* Notifications */}
            <button
              className="relative p-2 text-navy-500 hover:text-navy-700 hover:bg-navy-50 rounded-lg transition-colors"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              {unreadAlerts > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full" />
              )}
            </button>

            {/* User avatar */}
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                {user?.avatar ? (
                  <img
                    src={user.avatar}
                    alt={user.name}
                    className="w-8 h-8 rounded-full object-cover"
                  />
                ) : (
                  <User className="w-4 h-4 text-primary-600" />
                )}
              </div>
              <span className="hidden md:block text-sm font-medium text-navy-700">
                {user?.name || 'User'}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
