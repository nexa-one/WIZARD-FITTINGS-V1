import React from 'react';
import { FittingType, ShapeType, WallType } from '../../../types/hvac';
import { useTranslation } from '../../../i18n/useTranslation';

interface SummaryData {
  fittingType: FittingType;
  shapeType: ShapeType;
  elevationCode: string;
  planCode: string;
  inletWidth: number;
  inletHeight: number;
  inletDiameter: number;
  outletWidth: number;
  outletHeight: number;
  outletDiameter: number;
  length: number;
  neckLength: number;
  wallType: WallType;
  gauge: number;
  insulation: number;
}

interface Props {
  data: SummaryData;
  onBuild: () => void;
}

export const PreviewConfirm: React.FC<Props> = ({ data, onBuild }) => {
  const t = useTranslation();
  const isRound = data.shapeType === ShapeType.ROUND;

  const rows: [string, string][] = [
    [t.previewFittingType, data.fittingType.replace(/_/g, ' ')],
    [t.previewShape, data.shapeType],
    [t.previewElevationCode, data.elevationCode],
    [t.previewPlanCode, data.planCode],
    isRound
      ? [t.previewInletDiameter, `${data.inletDiameter}"`]
      : [t.previewInletSize, `${data.inletWidth}" × ${data.inletHeight}"`],
    [t.previewLength, `${data.length}"`],
    [t.previewNeckLength, `${data.neckLength}"`],
    [t.previewWallType, data.wallType.replace(/_/g, ' ')],
    [t.previewGauge, `${data.gauge} WG`],
    ...(data.wallType === WallType.DOUBLE_WALL ? [[t.previewInsulation, `${data.insulation}"`] as [string, string]] : []),
  ];

  return (
    <div className="space-y-3">
      <div className="text-xs text-gray-400">{t.previewPrompt}</div>
      <div className="bg-gray-800 rounded overflow-hidden">
        {rows.map(([k, v]) => (
          <div key={k} className="flex items-center justify-between px-3 py-1.5 border-b border-gray-700 last:border-0">
            <span className="text-xs text-gray-400">{k}</span>
            <span className="text-xs text-white font-medium">{v}</span>
          </div>
        ))}
      </div>
      <button
        onClick={onBuild}
        className="w-full px-4 py-2.5 text-sm font-bold bg-green-600 hover:bg-green-500 text-white rounded transition-all"
      >
        {t.buildFittingBtn}
      </button>
    </div>
  );
};
