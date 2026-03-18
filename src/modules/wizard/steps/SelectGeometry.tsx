import React from 'react';
import { FittingType } from '../../../types/hvac';
import { useTranslation } from '../../../i18n/useTranslation';
import clsx from 'clsx';

interface Props {
  selected: FittingType | null;
  onSelect: (t: FittingType) => void;
}

export const SelectGeometry: React.FC<Props> = ({ selected, onSelect }) => {
  const t = useTranslation();

  const FITTINGS = [
    { type: FittingType.STRAIGHT_DUCT, label: t.fittingStraightDuct, icon: '▬' },
    { type: FittingType.ELBOW_90, label: t.fittingElbow90, icon: '↱' },
    { type: FittingType.ELBOW_45, label: t.fittingElbow45, icon: '↗' },
    { type: FittingType.TRANSITION, label: t.fittingTransition, icon: '◁▷' },
    { type: FittingType.REDUCER, label: t.fittingReducer, icon: '◈' },
    { type: FittingType.OFFSET, label: t.fittingOffset, icon: '⟿' },
    { type: FittingType.TEE, label: t.fittingTee, icon: '⊤' },
    { type: FittingType.CROSS, label: t.fittingCross, icon: '✛' },
    { type: FittingType.CAP, label: t.fittingCap, icon: '⊓' },
    { type: FittingType.REGISTER_BOX, label: t.fittingRegisterBox, icon: '▭' },
  ];

  return (
    <div className="space-y-2">
      <div className="text-xs text-gray-400 mb-2">{t.selectGeometryPrompt}</div>
      <div className="grid grid-cols-2 gap-2">
        {FITTINGS.map(({ type, label, icon }) => (
          <button
            key={type}
            onClick={() => onSelect(type)}
            className={clsx(
              'flex flex-col items-center gap-1 p-3 rounded border text-xs transition-all',
              selected === type
                ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500 hover:text-white'
            )}
          >
            <span className="text-xl">{icon}</span>
            <span className="text-center leading-tight">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
