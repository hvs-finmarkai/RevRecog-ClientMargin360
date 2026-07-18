import { Outlet, Navigate } from 'react-router-dom';
import { Activity } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export default function AuthLayout() {
  const { isAuthenticated } = useAuthStore();

  // If already authenticated, redirect to dashboard
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex bg-background">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-navy-700 relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 25px 25px, white 2px, transparent 0)`,
            backgroundSize: '50px 50px',
          }} />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-white font-bold text-xl">Finmark.ai</h1>
              <p className="text-navy-300 text-xs">Revenue Intelligence Platform</p>
            </div>
          </div>

          {/* Feature highlights */}
          <div className="space-y-8">
            <div>
              <h2 className="text-3xl font-bold text-white leading-tight">
                RevRecog AI +<br />ClientMargin360
              </h2>
              <p className="text-navy-300 mt-4 text-lg max-w-md">
                Intelligent revenue recognition and client profitability analysis powered by AI.
              </p>
            </div>

            <div className="space-y-4">
              <FeatureItem text="ASC 606 / Ind AS 115 compliant revenue recognition" />
              <FeatureItem text="Real-time client profitability & margin tracking" />
              <FeatureItem text="AI-powered leakage detection & alerts" />
              <FeatureItem text="Automated billing & collections management" />
            </div>
          </div>

          {/* Footer */}
          <div className="text-navy-400 text-sm">
            <p>© 2024 Finmark.ai — Built for Denave PnL Management</p>
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-primary-500 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-navy-900 font-bold text-xl">Finmark.ai</h1>
              <p className="text-navy-500 text-xs">Revenue Intelligence Platform</p>
            </div>
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  );
}

function FeatureItem({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
        <div className="w-2 h-2 rounded-full bg-primary-400" />
      </div>
      <span className="text-navy-200 text-sm">{text}</span>
    </div>
  );
}
