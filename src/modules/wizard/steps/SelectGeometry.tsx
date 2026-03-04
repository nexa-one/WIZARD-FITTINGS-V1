import React from 'react';
import { FittingType } from '../../../types/hvac';
import clsx from 'clsx';

const FITTINGS = [
  { type: FittingType.STRAIGHT_DUCT, label: 'Straight Duct', icon: '▬' },
  { type: FittingType.ELBOW_90, label: 'Elbow 90°', icon: '↱' },
  { type: FittingType.ELBOW_45, label: 'Elbow 45°', icon: '↗' },
  { type: FittingType.TRANSITION, label: 'Transition', icon: '◁▷' },
  { type: FittingType.REDUCER, label: 'Reducer', icon: '◈' },
  { type: FittingType.OFFSET, label: 'Offset', icon: '⟿' },
  { type: FittingType.TEE, label: 'Tee', icon: '⊤' },
  { type: FittingType.CROSS, label: 'Cross', icon: '✛' },
  { type: FittingType.CAP, label: 'Cap', icon: '⊓' },
  { type: FittingType.REGISTER_BOX, label: 'Register Box', icon: '▭' },
];

interface Props {
  selected: FittingType | null;
  onSelect: (t: FittingType) => void;
}

export const SelectGeometry: React.FC<Props> = ({ selected, onSelect }) => (
  <div className="space-y-2">
    <div className="text-xs text-gray-400 mb-2">Select fitting geometry type:</div>
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
