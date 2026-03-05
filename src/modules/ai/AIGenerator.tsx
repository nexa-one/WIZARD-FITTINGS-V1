import React, { useState } from 'react';
import { useHVACStore } from '../../store';
import { useTranslation } from '../../i18n/useTranslation';
import { FittingType, ShapeType } from '../../types/hvac';
import clsx from 'clsx';

interface ParsedFitting {
  fittingType: FittingType;
  shapeType: ShapeType;
  inletWidth?: number;
  inletHeight?: number;
  inletDiameter?: number;
  length?: number;
  confidence: number;
  detectedKeywords: string[];
}

function parsePrompt(text: string): ParsedFitting {
  const lower = text.toLowerCase();
  const detected: string[] = [];

  let fittingType = FittingType.STRAIGHT_DUCT;
  let shapeType = ShapeType.RECTANGULAR;
  let inletWidth: number | undefined;
  let inletHeight: number | undefined;
  let inletDiameter: number | undefined;
  let length: number | undefined;

  if (lower.includes('elbow') || lower.includes('bend') || lower.includes('codo') || lower.includes('curva')) {
    detected.push('elbow/bend');
    if (lower.includes('45')) {
      fittingType = FittingType.ELBOW_45;
      detected.push('45°');
    } else {
      fittingType = FittingType.ELBOW_90;
      detected.push('90°');
    }
  } else if (lower.includes('transition') || lower.includes('transición') || lower.includes('transicion')) {
    fittingType = FittingType.TRANSITION;
    detected.push('transition');
  } else if (lower.includes('reducer') || lower.includes('reducing') || lower.includes('reductor')) {
    fittingType = FittingType.REDUCER;
    detected.push('reducer');
  } else if (lower.includes('tee') || lower.includes(' t ') || lower.includes('branch') || lower.includes(' te ')) {
    fittingType = FittingType.TEE;
    detected.push('tee/branch');
  } else if (lower.includes('cross') || lower.includes('cruz')) {
    fittingType = FittingType.CROSS;
    detected.push('cross');
  } else if (lower.includes('cap') || lower.includes('end cap') || lower.includes('tapa')) {
    fittingType = FittingType.CAP;
    detected.push('cap');
  } else if (lower.includes('register') || lower.includes('boot') || lower.includes('caja de registro')) {
    fittingType = FittingType.REGISTER_BOX;
    detected.push('register box');
  } else if (lower.includes('straight') || lower.includes('duct') || lower.includes('recto') || lower.includes('ducto')) {
    fittingType = FittingType.STRAIGHT_DUCT;
    detected.push('straight duct');
  }

  if (lower.includes('round') || lower.includes('circular') || lower.includes('redondo') || lower.includes('circular')) {
    shapeType = ShapeType.ROUND;
    detected.push('round');
  } else if (lower.includes('oval')) {
    shapeType = ShapeType.OVAL;
    detected.push('oval');
  } else if (lower.includes('rect') || lower.includes('square') || lower.includes('flat') || lower.includes('rectangular')) {
    shapeType = ShapeType.RECTANGULAR;
    detected.push('rectangular');
  }

  const dimPattern = /(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)/i;
  const dimMatch = text.match(dimPattern);
  if (dimMatch) {
    inletWidth = parseFloat(dimMatch[1]);
    inletHeight = parseFloat(dimMatch[2]);
    detected.push(`${inletWidth}x${inletHeight}`);
  }

  const diaPattern = /(\d+(?:\.\d+)?)\s*(?:inch|in|"|''|diameter|dia|pulgada|pulgadas)/i;
  const diaMatch = text.match(diaPattern);
  if (diaMatch && shapeType === ShapeType.ROUND) {
    inletDiameter = parseFloat(diaMatch[1]);
    detected.push(`dia:${inletDiameter}"`);
  } else if (diaMatch && !dimMatch) {
    inletWidth = parseFloat(diaMatch[1]);
    detected.push(`${inletWidth}"`);
  }

  const lenPattern = /(\d+(?:\.\d+)?)\s*(?:long|length|ft|feet|'|largo|longitud)/i;
  const lenMatch = text.match(lenPattern);
  if (lenMatch) {
    length = parseFloat(lenMatch[1]);
    if (lower.includes('ft') || lower.includes('feet') || lower.includes("'")) {
      length = length * 12;
    }
    detected.push(`len:${length}"`);
  }

  const confidence = Math.min(0.95, 0.3 + detected.length * 0.12);

  return { fittingType, shapeType, inletWidth, inletHeight, inletDiameter, length, confidence, detectedKeywords: detected };
}

export const AIGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [parsed, setParsed] = useState<ParsedFitting | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const { setCurrentPSD, buildGeometry: doBuild, waterGauge } = useHVACStore();
  const t = useTranslation();

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setTimeout(() => {
      const result = parsePrompt(prompt);
      setParsed(result);
      setIsGenerating(false);
    }, 800);
  };

  const handleAcceptBuild = () => {
    if (!parsed) return;
    setCurrentPSD({
      fittingType: parsed.fittingType,
      shapeType: parsed.shapeType,
      inletWidth: parsed.inletWidth,
      inletHeight: parsed.inletHeight,
      inletDiameter: parsed.inletDiameter,
      length: parsed.length,
      wallGauge: waterGauge,
    });
    setTimeout(() => doBuild(), 50);
  };

  return (
    <div className="p-3 space-y-3">
      <div className="text-xs font-semibold text-blue-400 uppercase tracking-wide">{t.aiTitle}</div>

      <div>
        <label className="text-xs text-gray-400 mb-1 block">{t.aiDescribeLabel}</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={t.aiDescribePlaceholder}
          className="w-full h-20 px-2 py-2 text-xs bg-gray-800 border border-gray-700 rounded text-white placeholder-gray-600 focus:border-blue-500 focus:outline-none resize-none"
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleGenerate}
          disabled={!prompt.trim() || isGenerating}
          className="flex-1 px-3 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded transition-all"
        >
          {isGenerating ? t.aiAnalyzing : t.aiGenerate}
        </button>
        <label className="px-3 py-2 text-xs font-semibold bg-gray-700 hover:bg-gray-600 text-gray-300 rounded cursor-pointer transition-all">
          {t.aiUpload}
          <input type="file" accept="image/*" className="hidden" />
        </label>
      </div>

      {parsed && (
        <div className="bg-gray-800 rounded p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-green-400">{t.aiInterpretation}</span>
            <span className={clsx(
              'text-xs px-2 py-0.5 rounded-full',
              parsed.confidence > 0.7 ? 'bg-green-900 text-green-400' : 'bg-yellow-900 text-yellow-400'
            )}>
              {t.aiConfidence(Math.round(parsed.confidence * 100))}
            </span>
          </div>

          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">{t.aiFittingType}</span>
              <span className="text-white font-medium">{parsed.fittingType.replace(/_/g, ' ')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">{t.aiShape}</span>
              <span className="text-white">{parsed.shapeType}</span>
            </div>
            {parsed.inletWidth && (
              <div className="flex justify-between">
                <span className="text-gray-400">{t.aiWidth}</span>
                <span className="text-white">{parsed.inletWidth}"</span>
              </div>
            )}
            {parsed.inletHeight && (
              <div className="flex justify-between">
                <span className="text-gray-400">{t.aiHeight}</span>
                <span className="text-white">{parsed.inletHeight}"</span>
              </div>
            )}
            {parsed.inletDiameter && (
              <div className="flex justify-between">
                <span className="text-gray-400">{t.aiDiameter}</span>
                <span className="text-white">{parsed.inletDiameter}"</span>
              </div>
            )}
            {parsed.length && (
              <div className="flex justify-between">
                <span className="text-gray-400">{t.aiLength}</span>
                <span className="text-white">{parsed.length}"</span>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-1">
            {parsed.detectedKeywords.map((kw) => (
              <span key={kw} className="text-xs px-1.5 py-0.5 bg-blue-900/50 text-blue-300 rounded">
                {kw}
              </span>
            ))}
          </div>

          <button
            onClick={handleAcceptBuild}
            className="w-full px-3 py-2 text-xs font-semibold bg-green-600 hover:bg-green-500 text-white rounded transition-all"
          >
            {t.aiAcceptBuild}
          </button>
        </div>
      )}
    </div>
  );
};
