import React from 'react';
import { PlanCode } from '../../../types/hvac';
import clsx from 'clsx';

const CODES = [
  { code: PlanCode.L, desc: 'Left Turn' },
  { code: PlanCode.R, desc: 'Right Turn' },
  { code: PlanCode.S, desc: 'Straight' },
  { code: PlanCode.T, desc: 'Tee' },
  { code: PlanCode.X, desc: 'Cross' },
  { code: PlanCode.LU, desc: 'Left-Up' },
  { code: PlanCode.LD, desc: 'Left-Down' },
  { code: PlanCode.RU, desc: 'Right-Up' },
  { code: PlanCode.RD, desc: 'Right-Down' },
];

interface Props {
  selected: string | null;
  onSelect: (c: string) => void;
}

export const SelectPlanCode: React.FC<Props> = ({ selected, onSelect }) => (
  <div className="space-y-2">
    <div className="text-xs text-gray-400 mb-2">Select plan code:</div>
    <div className="grid grid-cols-3 gap-2">
      {CODES.map(({ code, desc }) => (
        <button
          key={code}
          onClick={() => onSelect(code)}
          className={clsx(
            'flex flex-col items-center gap-1 p-2 rounded border text-xs transition-all',
            selected === code
              ? 'bg-cyan-600/20 border-cyan-500 text-cyan-300'
              : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
          )}
        >
          <span className="font-bold text-base">{code}</span>
          <span className="text-center text-gray-500">{desc}</span>
        </button>
      ))}
    </div>
  </div>
);
