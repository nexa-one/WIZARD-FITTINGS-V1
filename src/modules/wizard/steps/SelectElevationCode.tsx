import React from 'react';
import { ElevationCode } from '../../../types/hvac';
import { useTranslation } from '../../../i18n/useTranslation';
import clsx from 'clsx';

interface Props {
  selected: string | null;
  onSelect: (c: string) => void;
}

export const SelectElevationCode: React.FC<Props> = ({ selected, onSelect }) => {
  const t = useTranslation();

  const CODES = [
    { code: ElevationCode.E1, desc: t.elevLevel1 },
    { code: ElevationCode.E2, desc: t.elevLevel2 },
    { code: ElevationCode.E3, desc: t.elevLevel3 },
    { code: ElevationCode.E4, desc: t.elevLevel4 },
    { code: ElevationCode.E5, desc: t.elevLevel5 },
    { code: ElevationCode.UP, desc: t.elevUpward },
    { code: ElevationCode.DOWN, desc: t.elevDownward },
    { code: ElevationCode.LEVEL, desc: t.elevLevelFlat },
    { code: ElevationCode.DROP, desc: t.elevDropDown },
    { code: ElevationCode.RISE, desc: t.elevRiseUp },
  ];

  return (
    <div className="space-y-2">
      <div className="text-xs text-gray-400 mb-2">{t.selectElevationPrompt}</div>
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
};
