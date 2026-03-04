import React from 'react';
import { useHVACStore } from '../../store';
import { DimensionMode } from '../../types/hvac';
import clsx from 'clsx';

export const IDODToggle: React.FC = () => {
  const { dimensionMode, toggleDimensionMode } = useHVACStore();
  const isOD = dimensionMode === DimensionMode.EXTERNAL_OD;

  return (
    <button
      onClick={toggleDimensionMode}
      className={clsx(
        'flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all',
        isOD
          ? 'bg-blue-600 border-blue-500 text-white'
          : 'bg-cyan-700 border-cyan-500 text-white'
      )}
      title="Toggle ID/OD dimension mode"
    >
      <span className={clsx('px-2 py-0.5 rounded-full', isOD ? 'bg-blue-800' : 'bg-transparent text-cyan-300')}>
        OD
      </span>
      <span>/</span>
      <span className={clsx('px-2 py-0.5 rounded-full', !isOD ? 'bg-cyan-900' : 'bg-transparent text-blue-300')}>
        ID
      </span>
    </button>
  );
};
