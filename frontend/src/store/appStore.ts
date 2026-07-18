import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ThemeMode = 'light' | 'dark';

export interface Breadcrumb {
  label: string;
  href?: string;
}

interface AppStore {
  sidebarCollapsed: boolean;
  sidebarMobileOpen: boolean;
  theme: ThemeMode;
  currentPageTitle: string;
  breadcrumbs: Breadcrumb[];
  systemStatus: 'operational' | 'degraded' | 'maintenance';
  selectedPeriod: string;
  selectedClientId: string | null;
  unreadAlerts: number;

  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarMobileOpen: (open: boolean) => void;
  toggleTheme: () => void;
  setPageTitle: (title: string) => void;
  setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => void;
  setSystemStatus: (status: 'operational' | 'degraded' | 'maintenance') => void;
  setSelectedPeriod: (period: string) => void;
  setSelectedClientId: (clientId: string | null) => void;
  setUnreadAlerts: (count: number) => void;
}

function getInitialTheme(): ThemeMode {
  const stored = localStorage.getItem('app-theme');
  if (stored === 'dark' || stored === 'light') {
    return stored;
  }
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function applyTheme(theme: ThemeMode) {
  localStorage.setItem('app-theme', theme);
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

const initialTheme = getInitialTheme();
applyTheme(initialTheme);

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      sidebarCollapsed: false,
      sidebarMobileOpen: false,
      theme: initialTheme,
      currentPageTitle: 'Overview',
      breadcrumbs: [],
      systemStatus: 'operational',
      selectedPeriod: 'current_month',
      selectedClientId: null,
      unreadAlerts: 0,

      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),

      setSidebarCollapsed: (collapsed: boolean) => set({ sidebarCollapsed: collapsed }),

      setSidebarMobileOpen: (open: boolean) => set({ sidebarMobileOpen: open }),

      toggleTheme: () => {
        const newTheme: ThemeMode = get().theme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
        set({ theme: newTheme });
      },

      setPageTitle: (title: string) => set({ currentPageTitle: title }),

      setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => set({ breadcrumbs }),

      setSystemStatus: (status) => set({ systemStatus: status }),

      setSelectedPeriod: (period: string) => set({ selectedPeriod: period }),

      setSelectedClientId: (clientId: string | null) => set({ selectedClientId: clientId }),

      setUnreadAlerts: (count: number) => set({ unreadAlerts: count }),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
        selectedPeriod: state.selectedPeriod,
      }),
    }
  )
);
