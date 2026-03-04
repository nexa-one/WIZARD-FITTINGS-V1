import React, { useState } from 'react';
import { useHVACStore } from '../../store';
import { FittingType, ShapeType, ConnectionType, WallType } from '../../types/hvac';

export const ParametricBuilder: React.FC = () => {
  const { setCurrentPSD, buildGeometry, waterGauge, dimensionMode } = useHVACStore();

  const [form, setForm] = useState({
    fittingType: FittingType.STRAIGHT_DUCT,
    shapeType: ShapeType.RECTANGULAR,
    inletWidth: 12,
    inletHeight: 12,
    inletDiameter: 12,
    outletWidth: 8,
    outletHeight: 8,
    outletDiameter: 8,
    length: 56,
    neckLength: 6,
    connectionType: ConnectionType.TDC,
    wallType: WallType.SINGLE_WALL,
    insulation: 1.0,
    gauge: waterGauge,
    useLiner: false,
    holeDiameter: 0.25,
    spacing: 0.5,
    notes: '',
    alignment: 'CENTERED' as 'CENTERED' | 'CENTERLINE' | 'LEFT' | 'RIGHT',
  });

  const isRound = form.shapeType === ShapeType.ROUND;
  const isTransition = form.fittingType === FittingType.TRANSITION || form.fittingType === FittingType.REDUCER;
  const isDoubleWall = form.wallType === WallType.DOUBLE_WALL;

  const set = (key: string, value: unknown) => setForm((f) => ({ ...f, [key]: value }));

  const handleBuild = () => {
    setCurrentPSD({
      fittingType: form.fittingType,
      shapeType: form.shapeType,
      inletWidth: isRound ? undefined : form.inletWidth,
      inletHeight: isRound ? undefined : form.inletHeight,
      inletDiameter: isRound ? form.inletDiameter : undefined,
      outletWidth: isTransition && !isRound ? form.outletWidth : undefined,
      outletHeight: isTransition && !isRound ? form.outletHeight : undefined,
      outletDiameter: isTransition && isRound ? form.outletDiameter : undefined,
      length: form.length,
      neckLength: form.neckLength,
      connectionType: form.connectionType,
      wallType: form.wallType,
      wallGauge: form.gauge,
      insulation: isDoubleWall ? form.insulation : undefined,
      linerPerforation: form.useLiner ? { holeDiameter: form.holeDiameter, spacing: form.spacing } : undefined,
      dimensionMode: dimensionMode,
      alignment: form.alignment,
      notes: form.notes || undefined,
    });
    setTimeout(() => buildGeometry(), 50);
  };

  const label = 'text-xs text-gray-400 mb-0.5 block';
  const input = 'w-full px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none';
  const select = 'w-full px-2 py-1.5 text-xs bg-gray-800 border border-gray-700 rounded text-white focus:border-blue-500 focus:outline-none';

  return (
    <div className="p-3 space-y-3 text-sm">
      <div className="text-xs font-semibold text-blue-400 uppercase tracking-wide">Manual Parametric Builder</div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label}>Shape Type</label>
          <select className={select} value={form.shapeType} onChange={(e) => set('shapeType', e.target.value)}>
            <option value={ShapeType.RECTANGULAR}>Rectangular</option>
            <option value={ShapeType.ROUND}>Round</option>
            <option value={ShapeType.OVAL}>Oval</option>
          </select>
        </div>
        <div>
          <label className={label}>Fitting Type</label>
          <select className={select} value={form.fittingType} onChange={(e) => set('fittingType', e.target.value)}>
            {Object.values(FittingType).map((ft) => (
              <option key={ft} value={ft}>{ft.replace(/_/g, ' ')}</option>
            ))}
          </select>
        </div>
      </div>

      {!isRound ? (
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={label}>Inlet Width (")</label>
            <input type="number" className={input} value={form.inletWidth} onChange={(e) => set('inletWidth', Number(e.target.value))} />
          </div>
          <div>
            <label className={label}>Inlet Height (")</label>
            <input type="number" className={input} value={form.inletHeight} onChange={(e) => set('inletHeight', Number(e.target.value))} />
          </div>
        </div>
      ) : (
        <div>
          <label className={label}>Inlet Diameter (")</label>
          <input type="number" className={input} value={form.inletDiameter} onChange={(e) => set('inletDiameter', Number(e.target.value))} />
        </div>
      )}

      {isTransition && (
        !isRound ? (
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className={label}>Outlet Width (")</label>
              <input type="number" className={input} value={form.outletWidth} onChange={(e) => set('outletWidth', Number(e.target.value))} />
            </div>
            <div>
              <label className={label}>Outlet Height (")</label>
              <input type="number" className={input} value={form.outletHeight} onChange={(e) => set('outletHeight', Number(e.target.value))} />
            </div>
          </div>
        ) : (
          <div>
            <label className={label}>Outlet Diameter (")</label>
            <input type="number" className={input} value={form.outletDiameter} onChange={(e) => set('outletDiameter', Number(e.target.value))} />
          </div>
        )
      )}

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label}>Length (")</label>
          <input type="number" className={input} value={form.length} onChange={(e) => set('length', Number(e.target.value))} />
        </div>
        <div>
          <label className={label}>Neck Length (")</label>
          <input type="number" className={input} value={form.neckLength} onChange={(e) => set('neckLength', Number(e.target.value))} />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label}>Connection</label>
          <select className={select} value={form.connectionType} onChange={(e) => set('connectionType', e.target.value)}>
            <option value={ConnectionType.TDC}>TDC</option>
            <option value={ConnectionType.DUCTMATE}>Ductmate</option>
            <option value={ConnectionType.SLIP_AND_DRIVE}>Slip & Drive</option>
          </select>
        </div>
        <div>
          <label className={label}>Wall Type</label>
          <select className={select} value={form.wallType} onChange={(e) => set('wallType', e.target.value)}>
            <option value={WallType.SINGLE_WALL}>Single Wall</option>
            <option value={WallType.DOUBLE_WALL}>Double Wall</option>
          </select>
        </div>
      </div>

      {isDoubleWall && (
        <div>
          <label className={label}>Insulation Thickness (")</label>
          <input type="number" step="0.25" className={input} value={form.insulation} onChange={(e) => set('insulation', Number(e.target.value))} />
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label}>Gauge (WG)</label>
          <input type="number" className={input} value={form.gauge} min={14} max={28} step={2} onChange={(e) => set('gauge', Number(e.target.value))} />
        </div>
        <div>
          <label className={label}>Alignment</label>
          <select className={select} value={form.alignment} onChange={(e) => set('alignment', e.target.value)}>
            <option value="CENTERED">Centered</option>
            <option value="CENTERLINE">Centerline</option>
            <option value="LEFT">Left</option>
            <option value="RIGHT">Right</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="liner"
          checked={form.useLiner}
          onChange={(e) => set('useLiner', e.target.checked)}
          className="accent-blue-500"
        />
        <label htmlFor="liner" className="text-xs text-gray-400">Liner Perforation</label>
      </div>

      {form.useLiner && (
        <div className="grid grid-cols-2 gap-2 pl-4">
          <div>
            <label className={label}>Hole Dia (")</label>
            <input type="number" step="0.01" className={input} value={form.holeDiameter} onChange={(e) => set('holeDiameter', Number(e.target.value))} />
          </div>
          <div>
            <label className={label}>Spacing (")</label>
            <input type="number" step="0.1" className={input} value={form.spacing} onChange={(e) => set('spacing', Number(e.target.value))} />
          </div>
        </div>
      )}

      <div>
        <label className={label}>Notes</label>
        <input type="text" className={input} value={form.notes} onChange={(e) => set('notes', e.target.value)} placeholder="Optional notes..." />
      </div>

      <button
        onClick={handleBuild}
        className="w-full px-3 py-2 text-sm font-semibold bg-blue-600 hover:bg-blue-500 text-white rounded transition-all"
      >
        🔧 Build Fitting
      </button>
    </div>
  );
};
