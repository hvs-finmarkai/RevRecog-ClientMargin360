import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, AuthTokens, LoginCredentials } from '@/types';
import apiClient from '@/lib/axios';
import toast from 'react-hot-toast';

interface AuthStore {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  setUser: (user: User) => void;
  setTokens: (tokens: AuthTokens) => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => boolean;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const response = await apiClient.post('/auth/login', credentials);
          const { access, refresh, user } = response.data;
          const tokens = { access, refresh };
          
          set({
            user,
            tokens,
            isAuthenticated: true,
            isLoading: false,
          });
          
          localStorage.setItem('auth-tokens', JSON.stringify(tokens));
          
          toast.success(`Welcome back, ${user.first_name || user.email}!`);
        } catch (error: unknown) {
          set({ isLoading: false });
          const err = error as { response?: { data?: { non_field_errors?: string[]; detail?: string } } };
          const message = err.response?.data?.non_field_errors?.[0] || err.response?.data?.detail || 'Login failed. Please check your credentials.';
          toast.error(message);
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
        });
        localStorage.removeItem('auth-tokens');
        localStorage.removeItem('auth-storage');
        toast.success('Logged out successfully');
      },

      refreshUser: async () => {
        try {
          const response = await apiClient.get('/auth/me');
          set({ user: response.data.data });
        } catch {
          // If refresh fails, logout
          get().logout();
        }
      },

      setUser: (user: User) => set({ user }),
      
      setTokens: (tokens: AuthTokens) => {
        set({ tokens });
        localStorage.setItem('auth-tokens', JSON.stringify(tokens));
      },
      
      setLoading: (isLoading: boolean) => set({ isLoading }),

      checkAuth: () => {
        const state = get();
        if (!state.tokens) return false;
        
        // Check if token is expired
        if (state.tokens.expiresAt < Date.now()) {
          get().logout();
          return false;
        }
        
        return state.isAuthenticated;
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
