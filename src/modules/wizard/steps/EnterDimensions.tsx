import React from 'react';
import { FittingType, ShapeType } from '../../../types/hvac';

interface DimValues {
  shapeType: ShapeType;
  inletWidth: number;
  inletHeight: number;
  inletDiameter: number;
  outletWidth: number;
  outletHeight: number;
  outletDiameter: number;
  length: number;
  neckLength: number;
}

interface Props {
  fittingType: FittingType;
  values: DimValues;
  onChange: (values: DimValues) => void;
}

export const EnterDimensions: React.FC<Props> = ({ fittingType, values, onChange }) => {
  const set = (key: keyof DimValues, value: number | ShapeType) =>
    onChange({ ...values, [key]: value });

  const isRound = values.shapeType === ShapeType.ROUND;
  const hasOutlet = [FittingType.TRANSITION, FittingType.REDUCER].includes(fittingType);

  const label = 'text-xs text-gray-400 mb-0.5 block';
  const input = 'w-full px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none';
  const select = 'w-full px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none';

  return (
    <div className="space-y-3">
      <div>
        <label className={label}>Shape Type</label>
        <select className={select} value={values.shapeType} onChange={(e) => set('shapeType', e.target.value as ShapeType)}>
          <option value={ShapeType.RECTANGULAR}>Rectangular</option>
          <option value={ShapeType.ROUND}>Round</option>
          <option value={ShapeType.OVAL}>Oval</option>
        </select>
      </div>

      <div className="text-xs font-semibold text-gray-400">Inlet Dimensions</div>
      {!isRound ? (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={label}>Width (")</label>
            <input type="number" className={input} value={values.inletWidth} onChange={(e) => set('inletWidth', Number(e.target.value))} />
          </div>
          <div>
            <label className={label}>Height (")</label>
            <input type="number" className={input} value={values.inletHeight} onChange={(e) => set('inletHeight', Number(e.target.value))} />
          </div>
        </div>
      ) : (
        <div>
          <label className={label}>Diameter (")</label>
          <input type="number" className={input} value={values.inletDiameter} onChange={(e) => set('inletDiameter', Number(e.target.value))} />
        </div>
      )}

      {hasOutlet && (
        <>
          <div className="text-xs font-semibold text-gray-400">Outlet Dimensions</div>
          {!isRound ? (
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className={label}>Width (")</label>
                <input type="number" className={input} value={values.outletWidth} onChange={(e) => set('outletWidth', Number(e.target.value))} />
              </div>
              <div>
                <label className={label}>Height (")</label>
                <input type="number" className={input} value={values.outletHeight} onChange={(e) => set('outletHeight', Number(e.target.value))} />
              </div>
            </div>
          ) : (
            <div>
              <label className={label}>Outlet Diameter (")</label>
              <input type="number" className={input} value={values.outletDiameter} onChange={(e) => set('outletDiameter', Number(e.target.value))} />
            </div>
          )}
        </>
      )}

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label}>Length (")</label>
          <input type="number" className={input} value={values.length} onChange={(e) => set('length', Number(e.target.value))} />
        </div>
        <div>
          <label className={label}>Neck Length (")</label>
          <input type="number" className={input} value={values.neckLength} onChange={(e) => set('neckLength', Number(e.target.value))} />
        </div>
      </div>
    </div>
  );
};
