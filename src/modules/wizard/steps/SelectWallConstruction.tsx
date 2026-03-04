import React from 'react';
import { WallType } from '../../../types/hvac';
import clsx from 'clsx';

interface WallValues {
  wallType: WallType;
  gauge: number;
  insulation: number;
  useLiner: boolean;
  holeDiameter: number;
  spacing: number;
}

interface Props {
  values: WallValues;
  onChange: (v: WallValues) => void;
}

export const SelectWallConstruction: React.FC<Props> = ({ values, onChange }) => {
  const set = (key: keyof WallValues, value: unknown) => onChange({ ...values, [key]: value });

  const label = 'text-xs text-gray-400 mb-0.5 block';
  const input = 'w-full px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none';

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        {[WallType.SINGLE_WALL, WallType.DOUBLE_WALL].map((wt) => (
          <button
            key={wt}
            onClick={() => set('wallType', wt)}
            className={clsx(
              'p-3 rounded border text-xs text-center transition-all',
              values.wallType === wt
                ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'
            )}
          >
            <div className="font-bold mb-1">{wt === WallType.SINGLE_WALL ? '◻' : '⬛'}</div>
            <div>{wt === WallType.SINGLE_WALL ? 'Single Wall' : 'Double Wall'}</div>
            <div className="text-gray-500 text-xs mt-0.5">
              {wt === WallType.SINGLE_WALL ? 'Standard' : 'Insulated'}
            </div>
          </button>
        ))}
      </div>

      {values.wallType === WallType.DOUBLE_WALL && (
        <div>
          <label className={label}>Insulation Thickness (")</label>
          <input
            type="number"
            step="0.25"
            className={input}
            value={values.insulation}
            onChange={(e) => set('insulation', Number(e.target.value))}
          />
        </div>
      )}

      <div>
        <label className={label}>Gauge (WG)</label>
        <input
          type="number"
          min={14}
          max={28}
          step={2}
          className={input}
          value={values.gauge}
          onChange={(e) => set('gauge', Number(e.target.value))}
        />
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="wiz-liner"
          checked={values.useLiner}
          onChange={(e) => set('useLiner', e.target.checked)}
          className="accent-blue-500"
        />
        <label htmlFor="wiz-liner" className="text-xs text-gray-400">Liner Perforation</label>
      </div>

      {values.useLiner && (
        <div className="grid grid-cols-2 gap-2 pl-4">
          <div>
            <label className={label}>Hole Dia (")</label>
            <input type="number" step="0.01" className={input} value={values.holeDiameter} onChange={(e) => set('holeDiameter', Number(e.target.value))} />
          </div>
          <div>
            <label className={label}>Spacing (")</label>
            <input type="number" step="0.1" className={input} value={values.spacing} onChange={(e) => set('spacing', Number(e.target.value))} />
          </div>
        </div>
      )}
    </div>
  );
};
