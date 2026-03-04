import React from 'react';
import { useHVACStore } from '../../store';
import clsx from 'clsx';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useHVACStore();

  return (
    <button
      onClick={toggleTheme}
      className={clsx(
        'px-3 py-1.5 rounded-full text-xs font-semibold border transition-all',
        theme === 'dark'
          ? 'bg-gray-800 border-gray-600 text-gray-300 hover:bg-gray-700'
          : 'bg-yellow-100 border-yellow-400 text-yellow-800 hover:bg-yellow-200'
      )}
      title="Toggle theme"
    >
      {theme === 'dark' ? '🌙 Dark' : '☀️ Light'}
    </button>
  );
};
