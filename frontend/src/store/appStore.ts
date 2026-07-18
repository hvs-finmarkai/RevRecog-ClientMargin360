import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Theme } from '@/types';

interface AppStore {
  // Sidebar state
  sidebarCollapsed: boolean;
  sidebarMobileOpen: boolean;
  
  // Theme
  theme: Theme;
  
  // Page state
  currentPageTitle: string;
  breadcrumbs: Breadcrumb[];
  
  // System status
  systemStatus: 'operational' | 'degraded' | 'maintenance';
  
  // Global filters
  selectedPeriod: string;
  selectedClientId: string | null;
  
  // Notifications
  unreadAlerts: number;
  
  // Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarMobileOpen: (open: boolean) => void;
  setTheme: (theme: Theme) => void;
  setPageTitle: (title: string) => void;
  setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => void;
  setSystemStatus: (status: 'operational' | 'degraded' | 'maintenance') => void;
  setSelectedPeriod: (period: string) => void;
  setSelectedClientId: (clientId: string | null) => void;
  setUnreadAlerts: (count: number) => void;
}

export interface Breadcrumb {
  label: string;
  href?: string;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      sidebarCollapsed: false,
      sidebarMobileOpen: false,
      theme: 'light',
      currentPageTitle: 'Overview',
      breadcrumbs: [],
      systemStatus: 'operational',
      selectedPeriod: 'current_month',
      selectedClientId: null,
      unreadAlerts: 0,

      toggleSidebar: () => set({ sidebarCollapsed: !get().sidebarCollapsed }),
      
      setSidebarCollapsed: (collapsed: boolean) => set({ sidebarCollapsed: collapsed }),
      
      setSidebarMobileOpen: (open: boolean) => set({ sidebarMobileOpen: open }),
      
      setTheme: (theme: Theme) => {
        set({ theme });
        // Apply theme to document
        if (theme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
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
