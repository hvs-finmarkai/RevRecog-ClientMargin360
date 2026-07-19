import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Receipt,
  AlertTriangle,
  TrendingUp,
  Bell,
  ShieldCheck,
  LogOut,
  Sun,
  Moon,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useAppStore } from '@/store/appStore';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/dashboard/contracts', label: 'Contracts', icon: FileText },
  { to: '/dashboard/revenue-recognition', label: 'Revenue', icon: BarChart3 },
  { to: '/dashboard/invoices', label: 'Invoices', icon: Receipt },
  { to: '/dashboard/leakage', label: 'Leakage', icon: AlertTriangle },
  { to: '/dashboard/client-profitability', label: 'Profitability', icon: TrendingUp },
  { to: '/dashboard/alerts', label: 'Alerts', icon: Bell },
  { to: '/dashboard/admin', label: 'Admin', icon: ShieldCheck },
];

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { currentPageTitle, theme, toggleTheme } = useAppStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  const userInitials = user
    ? `${(user as unknown as { first_name?: string }).first_name?.[0] || user.name?.[0] || ''}${(user as unknown as { last_name?: string }).last_name?.[0] || user.name?.split(' ')[1]?.[0] || ''}`.toUpperCase()
    : 'DA';

  const userName = user
    ? `${(user as unknown as { first_name?: string }).first_name || ''} ${(user as unknown as { last_name?: string }).last_name || ''}`.trim() || user.name || 'Demo Admin'
    : 'Demo Admin';

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 flex flex-col transition-all duration-300 lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: 260, backgroundColor: 'var(--sidebar-bg)', borderRight: '1px solid var(--sidebar-border)' }}
      >
        <div className="flex items-center gap-2 px-4 h-16" style={{ borderBottom: '1px solid var(--sidebar-border)' }}>
          <div
            className="flex items-center justify-center rounded-xl"
            style={{ width: 36, height: 36, backgroundColor: '#4F46E5' }}
          >
            <TrendingUp size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold" style={{ color: 'var(--sidebar-text)' }}>Finmark.ai</h1>
            <p className="text-xs" style={{ color: 'var(--sidebar-text-secondary)' }}>RevRecog AI</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/dashboard'}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'border-l-[3px] border-[#4F46E5]'
                    : 'border-l-[3px] border-transparent'
                }`
              }
              style={({ isActive }) => ({
                backgroundColor: isActive ? 'var(--sidebar-active)' : undefined,
                color: 'var(--sidebar-text)',
              })}
              onMouseEnter={(e) => {
                if (!e.currentTarget.classList.contains('active')) {
                  e.currentTarget.style.backgroundColor = 'var(--sidebar-hover)';
                }
              }}
              onMouseLeave={(e) => {
                const isActive = e.currentTarget.getAttribute('aria-current') === 'page';
                if (!isActive) {
                  e.currentTarget.style.backgroundColor = '';
                }
              }}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="px-4 py-4" style={{ borderTop: '1px solid var(--sidebar-border)' }}>
          <div className="flex items-center gap-3">
            <div
              className="flex items-center justify-center rounded-full text-white text-sm font-semibold"
              style={{ width: 36, height: 36, backgroundColor: '#4F46E5' }}
            >
              {userInitials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate" style={{ color: 'var(--sidebar-text)' }}>{userName}</div>
              <div className="text-xs truncate" style={{ color: 'var(--sidebar-text-secondary)' }}>Finance Team</div>
            </div>
            <button
              onClick={handleLogout}
              className="transition-colors"
              style={{ color: 'var(--sidebar-text-secondary)' }}
              title="Logout"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header
          className="flex items-center justify-between px-6 py-3 shrink-0"
          style={{ backgroundColor: 'var(--card-bg)', borderBottom: '1px solid var(--gray-200)' }}
        >
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden text-gray-600"
              onClick={() => setMobileOpen(true)}
            >
              <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M3 12h18M3 6h18M3 18h18" />
              </svg>
            </button>
            <h1 className="text-lg font-semibold" style={{ color: 'var(--text)' }}>{currentPageTitle}</h1>
          </div>

          <div className="flex items-center gap-4">
            <span className="hidden md:inline text-xs" style={{ color: 'var(--gray-500)' }}>
              RevRecog AI + ClientMargin360 • Finmark.ai
            </span>

            <div
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
              style={{ backgroundColor: '#ECFDF5', border: '1px solid #A7F3D0' }}
            >
              <span className="status-dot" style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#10B981' }} />
              <span style={{ color: '#065F46' }}>System Online</span>
            </div>

            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg transition-colors"
              style={{ color: 'var(--gray-500)' }}
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6" style={{ backgroundColor: 'var(--bg)' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
