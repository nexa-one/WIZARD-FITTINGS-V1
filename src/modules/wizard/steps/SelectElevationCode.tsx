import React from 'react';
import { ElevationCode } from '../../../types/hvac';
import clsx from 'clsx';

const CODES = [
  { code: ElevationCode.E1, desc: 'Level 1' },
  { code: ElevationCode.E2, desc: 'Level 2' },
  { code: ElevationCode.E3, desc: 'Level 3' },
  { code: ElevationCode.E4, desc: 'Level 4' },
  { code: ElevationCode.E5, desc: 'Level 5' },
  { code: ElevationCode.UP, desc: 'Upward' },
  { code: ElevationCode.DOWN, desc: 'Downward' },
  { code: ElevationCode.LEVEL, desc: 'Level/Flat' },
  { code: ElevationCode.DROP, desc: 'Drop Down' },
  { code: ElevationCode.RISE, desc: 'Rise Up' },
];

interface Props {
  selected: string | null;
  onSelect: (c: string) => void;
}

export const SelectElevationCode: React.FC<Props> = ({ selected, onSelect }) => (
  <div className="space-y-2">
    <div className="text-xs text-gray-400 mb-2">Select elevation code:</div>
    <div className="grid grid-cols-3 gap-2">
      {CODES.map(({ code, desc }) => (
        <button
          key={code}
          onClick={() => onSelect(code)}
          className={clsx(
            'flex flex-col items-center gap-1 p-2 rounded border text-xs transition-all',
            selected === code
              ? 'bg-blue-600/20 border-blue-500 text-blue-300'
              : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
          )}
        >
          <span className="font-bold text-sm">{code}</span>
          <span className="text-center text-gray-500">{desc}</span>
        </button>
      ))}
    </div>
  </div>
);
