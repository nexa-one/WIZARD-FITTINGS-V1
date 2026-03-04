import React, { useState } from 'react';
import { FittingType, ShapeType, WallType, ConnectionType, DimensionMode } from '../../types/hvac';
import { SelectGeometry } from './steps/SelectGeometry';
import { SelectElevationCode } from './steps/SelectElevationCode';
import { SelectPlanCode } from './steps/SelectPlanCode';
import { EnterDimensions } from './steps/EnterDimensions';
import { SelectWallConstruction } from './steps/SelectWallConstruction';
import { PreviewConfirm } from './steps/PreviewConfirm';
import { useHVACStore } from '../../store';
import clsx from 'clsx';

const STEPS = ['Geometry', 'Elevation', 'Plan', 'Dimensions', 'Wall', 'Confirm'];

export const WizardFittings: React.FC = () => {
  const [step, setStep] = useState(0);
  const { setCurrentPSD, buildGeometry, waterGauge } = useHVACStore();

  const [selectedFitting, setSelectedFitting] = useState<FittingType | null>(null);
  const [elevationCode, setElevationCode] = useState<string | null>(null);
  const [planCode, setPlanCode] = useState<string | null>(null);
  const [dims, setDims] = useState({
    shapeType: ShapeType.RECTANGULAR,
    inletWidth: 12,
    inletHeight: 12,
    inletDiameter: 12,
    outletWidth: 8,
    outletHeight: 8,
    outletDiameter: 8,
    length: 56,
    neckLength: 6,
  });
  const [wall, setWall] = useState({
    wallType: WallType.SINGLE_WALL,
    gauge: waterGauge,
    insulation: 1.0,
    useLiner: false,
    holeDiameter: 0.25,
    spacing: 0.5,
  });

  const canNext = [
    !!selectedFitting,
    !!elevationCode,
    !!planCode,
    true,
    true,
    true,
  ][step];

  const handleBuild = () => {
    if (!selectedFitting) return;
    const isRound = dims.shapeType === ShapeType.ROUND;
    setCurrentPSD({
      fittingType: selectedFitting,
      shapeType: dims.shapeType,
      inletWidth: isRound ? undefined : dims.inletWidth,
      inletHeight: isRound ? undefined : dims.inletHeight,
      inletDiameter: isRound ? dims.inletDiameter : undefined,
      outletWidth: isRound ? undefined : dims.outletWidth,
      outletHeight: isRound ? undefined : dims.outletHeight,
      outletDiameter: isRound ? dims.outletDiameter : undefined,
      length: dims.length,
      neckLength: dims.neckLength,
      wallType: wall.wallType,
      wallGauge: wall.gauge,
      insulation: wall.wallType === WallType.DOUBLE_WALL ? wall.insulation : undefined,
      linerPerforation: wall.useLiner ? { holeDiameter: wall.holeDiameter, spacing: wall.spacing } : undefined,
      connectionType: ConnectionType.TDC,
      dimensionMode: DimensionMode.EXTERNAL_OD,
      elevationCode: elevationCode ?? undefined,
      planCode: planCode ?? undefined,
    });
    setTimeout(() => buildGeometry(), 50);
  };

  return (
    <div className="p-3 space-y-3">
      <div className="text-xs font-semibold text-blue-400 uppercase tracking-wide">Wizard Fittings</div>

      <div className="flex items-center gap-1 mb-2">
        {STEPS.map((s, i) => (
          <React.Fragment key={s}>
            <button
              onClick={() => i < step && setStep(i)}
              className={clsx(
                'flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold transition-all',
                i === step ? 'bg-blue-600 text-white' :
                i < step ? 'bg-green-700 text-white cursor-pointer hover:bg-green-600' :
                'bg-gray-700 text-gray-500'
              )}
              title={s}
            >
              {i < step ? '✓' : i + 1}
            </button>
            {i < STEPS.length - 1 && (
              <div className={clsx('flex-1 h-0.5', i < step ? 'bg-green-700' : 'bg-gray-700')} />
            )}
          </React.Fragment>
        ))}
      </div>

      <div className="text-xs text-gray-300 font-medium">{STEPS[step]}</div>

      <div className="min-h-[200px]">
        {step === 0 && <SelectGeometry selected={selectedFitting} onSelect={setSelectedFitting} />}
        {step === 1 && <SelectElevationCode selected={elevationCode} onSelect={setElevationCode} />}
        {step === 2 && <SelectPlanCode selected={planCode} onSelect={setPlanCode} />}
        {step === 3 && selectedFitting && (
          <EnterDimensions fittingType={selectedFitting} values={dims} onChange={setDims} />
        )}
        {step === 4 && <SelectWallConstruction values={wall} onChange={setWall} />}
        {step === 5 && selectedFitting && (
          <PreviewConfirm
            data={{
              fittingType: selectedFitting,
              elevationCode: elevationCode ?? '',
              planCode: planCode ?? '',
              ...dims,
              wallType: wall.wallType,
              gauge: wall.gauge,
              insulation: wall.insulation,
            }}
            onBuild={handleBuild}
          />
        )}
      </div>

      <div className="flex gap-2 pt-1">
        <button
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="flex-1 px-3 py-1.5 text-xs bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-white rounded transition-all"
        >
          ← Back
        </button>
        {step < STEPS.length - 1 && (
          <button
            onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}
            disabled={!canNext}
            className="flex-1 px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded transition-all"
          >
            Next →
          </button>
        )}
      </div>
    </div>
  );
};
