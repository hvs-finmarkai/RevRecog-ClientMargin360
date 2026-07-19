import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Eye, EyeOff, TrendingUp } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const storedTokens = localStorage.getItem('auth-tokens');
  if (storedTokens) {
    try {
      const tokens = JSON.parse(storedTokens);
      if (tokens.accessToken) {
        return <Navigate to="/dashboard" replace />;
      }
    } catch {}
  }

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data);
      navigate('/dashboard');
    } catch {
    }
  };

  return (
    <div className="flex h-screen">
      <div
        className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center px-12"
        style={{ backgroundColor: '#0F172A' }}
      >
        <div className="max-w-md text-center">
          <div className="flex items-center justify-center gap-3 mb-8">
            <div
              className="flex items-center justify-center rounded-xl"
              style={{ width: 48, height: 48, backgroundColor: '#4F46E5' }}
            >
              <TrendingUp size={28} className="text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-white">Finmark.ai</h1>
              <p className="text-sm text-slate-400">RevRecog AI</p>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">
            RevRecog AI + ClientMargin360
          </h2>
          <p className="text-slate-300 text-lg mb-6">
            Automated Revenue Recognition, Billing & Real-Time Client Profitability
          </p>
          <div className="space-y-3 text-left">
            {[
              "AI-Powered Revenue Recognition",
              "Real-time Client Profitability",
              "Automated Billing & Invoicing",
              "Leakage Detection",
              "Multi-dimensional Dashboards",
            ].map((feature) => (
              <div key={feature} className="flex items-center gap-3 text-slate-300">
                <div className="h-2 w-2 rounded-full bg-indigo-500" />
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>
          <div className="mt-12 pt-8 border-t border-white/10">
            <p className="text-xs text-slate-500">Finmark.ai</p>
            <p className="text-xs text-slate-600">© 2025 All rights reserved</p>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center px-8 bg-white">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <div
              className="flex items-center justify-center rounded-xl"
              style={{ width: 44, height: 44, backgroundColor: '#4F46E5' }}
            >
              <TrendingUp size={24} className="text-white" />
            </div>
            <div>
              <div className="font-bold text-lg" style={{ color: '#0F172A' }}>Finmark.ai</div>
              <div className="text-gray-400 text-xs">RevRecog AI</div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h2>
          <p className="text-gray-500 mb-8">Sign in to your account to continue</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Email Address
              </label>
              <input
                {...register('email')}
                type="email"
                placeholder="admin@finmark.ai"
                className="input-field"
                autoComplete="email"
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  className="input-field pr-10"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full"
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0' }}>
            <p className="text-xs text-gray-500 font-medium mb-1">Demo Credentials</p>
            <p className="text-xs text-gray-600">
              Email: <span className="font-mono">admin@finmark.ai</span>
            </p>
            <p className="text-xs text-gray-600">
              Password: <span className="font-mono">Finmark@2026</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
