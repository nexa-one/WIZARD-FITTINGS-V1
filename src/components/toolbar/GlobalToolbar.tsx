import React from 'react';
import { useHVACStore } from '../../store';
import { IDODToggle } from '../ui/IDODToggle';
import { ThemeToggle } from '../ui/ThemeToggle';
import clsx from 'clsx';

export const GlobalToolbar: React.FC = () => {
  const { viewMode, setViewMode, language, toggleLanguage, waterGauge, setWaterGauge, currentOrder } = useHVACStore();

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-gray-900 border-b border-gray-700 min-h-[52px] flex-wrap">
      <div className="flex items-center gap-2 mr-4">
        <div className="w-7 h-7 bg-blue-500 rounded flex items-center justify-center text-white font-bold text-xs">
          H
        </div>
        <span className="text-white font-bold text-sm whitespace-nowrap">HVAC Parametric Engine v7.0</span>
      </div>

      <div className="h-5 w-px bg-gray-700" />

      <IDODToggle />

      <div className="h-5 w-px bg-gray-700" />

      <div className="flex items-center bg-gray-800 rounded-full p-0.5 gap-0.5">
        {(['3D_VISUAL', 'CNC_FLAT_PATTERN', 'X_RAY_TRANSPARENT'] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={clsx(
              'px-2 py-1 rounded-full text-xs font-medium transition-all',
              viewMode === mode ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
            )}
          >
            {mode === '3D_VISUAL' ? '3D' : mode === 'CNC_FLAT_PATTERN' ? 'CNC' : 'X-RAY'}
          </button>
        ))}
      </div>

      <div className="h-5 w-px bg-gray-700" />

      <button
        onClick={toggleLanguage}
        className="px-3 py-1.5 rounded-full text-xs font-semibold bg-gray-800 border border-gray-600 text-gray-300 hover:bg-gray-700 transition-all"
      >
        {language === 'en' ? '🇺🇸 USA' : '🇲🇽 LATAM'}
      </button>

      <div className="h-5 w-px bg-gray-700" />

      <div className="flex items-center gap-2">
        <label className="text-xs text-gray-400 whitespace-nowrap">Gauge (WG):</label>
        <input
          type="number"
          value={waterGauge}
          onChange={(e) => setWaterGauge(Number(e.target.value))}
          className="w-16 px-2 py-1 text-xs bg-gray-800 border border-gray-600 rounded text-white focus:border-blue-500 focus:outline-none"
          min={14}
          max={28}
          step={2}
        />
      </div>

      <div className="h-5 w-px bg-gray-700" />

      <ThemeToggle />

      <div className="ml-auto flex items-center gap-2">
        {currentOrder && (
          <span className="text-xs text-gray-400">
            Order: <span className="text-blue-400 font-semibold">{currentOrder.orderId}</span>
            <span className="text-gray-500 ml-1">({currentOrder.items.length} items)</span>
          </span>
        )}
      </div>
    </div>
  );
};
