import { useEffect } from 'react';
import { Settings, User, Bell, Shield, Database, Palette } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

export default function SettingsPage() {
  const { setPageTitle, theme, toggleTheme } = useAppStore();

  useEffect(() => {
    setPageTitle('Settings');
  }, [setPageTitle]);

  const sections = [
    { icon: User, title: 'Profile', desc: 'Manage your account information and preferences' },
    { icon: Bell, title: 'Notifications', desc: 'Configure alert thresholds and notification channels' },
    { icon: Shield, title: 'Security', desc: 'Password, two-factor authentication, and sessions' },
    { icon: Database, title: 'Data & Integration', desc: 'API keys, webhooks, and third-party connections' },
    { icon: Palette, title: 'Appearance', desc: 'Theme, display density, and date format preferences' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="text-sm text-navy-500 mt-1">Manage application configuration and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {sections.map((section) => {
            const Icon = section.icon;
            return (
              <div key={section.title} className="card-hover cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-navy-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-navy-900">{section.title}</h3>
                    <p className="text-xs text-navy-500 mt-0.5">{section.desc}</p>
                  </div>
                  <Settings className="w-4 h-4 text-navy-400" />
                </div>
              </div>
            );
          })}
        </div>

        <div className="space-y-4">
          <div className="card">
            <h3 className="text-sm font-semibold text-navy-900 mb-3">Quick Settings</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-navy-600">Theme</span>
                <select
                  value={theme}
                  onChange={() => toggleTheme()}
                  className="input-field w-auto text-xs py-1"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-navy-600">Currency</span>
                <span className="text-sm font-medium text-navy-900">INR (₹)</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-navy-600">Date Format</span>
                <span className="text-sm font-medium text-navy-900">DD MMM YYYY</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-navy-600">Fiscal Year</span>
                <span className="text-sm font-medium text-navy-900">Apr - Mar</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-sm font-semibold text-navy-900 mb-3">System Info</h3>
            <div className="space-y-2 text-xs text-navy-500">
              <div className="flex justify-between">
                <span>Version</span>
                <span className="font-mono">1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span>Environment</span>
                <span className="font-mono">Production</span>
              </div>
              <div className="flex justify-between">
                <span>API Status</span>
                <span className="text-success-600 font-medium">Connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
