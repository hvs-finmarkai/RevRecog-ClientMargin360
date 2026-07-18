import { Sun, Moon } from 'lucide-react';
import { useAppStore } from '@/store/appStore';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useAppStore();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 text-navy-500 hover:text-navy-700 hover:bg-navy-50 dark:text-navy-300 dark:hover:text-white dark:hover:bg-white/10 rounded-lg transition-colors"
      aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  );
}
