import React from 'react';
import { PlanCode } from '../../../types/hvac';
import { useTranslation } from '../../../i18n/useTranslation';
import clsx from 'clsx';

interface Props {
  selected: string | null;
  onSelect: (c: string) => void;
}

export const SelectPlanCode: React.FC<Props> = ({ selected, onSelect }) => {
  const t = useTranslation();

  const CODES = [
    { code: PlanCode.L, desc: t.planLeftTurn },
    { code: PlanCode.R, desc: t.planRightTurn },
    { code: PlanCode.S, desc: t.planStraight },
    { code: PlanCode.T, desc: t.planTee },
    { code: PlanCode.X, desc: t.planCross },
    { code: PlanCode.LU, desc: t.planLeftUp },
    { code: PlanCode.LD, desc: t.planLeftDown },
    { code: PlanCode.RU, desc: t.planRightUp },
    { code: PlanCode.RD, desc: t.planRightDown },
  ];

  return (
    <div className="space-y-2">
      <div className="text-xs text-gray-400 mb-2">{t.selectPlanPrompt}</div>
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
};
