import React, { useRef } from 'react';
import { Calculator, RotateCw, Copy, Download, HelpCircle, AlertTriangle } from 'lucide-react';
import { useHVACStore } from '../../store';

// ---------------------------------------------------------------------------
// Types & helpers
// ---------------------------------------------------------------------------

interface Inputs {
  width: string;
  length: string;
  offset: string;
}

function calcOffset(inputs: Inputs) {
  const width = parseFloat(inputs.width) || 0;
  const length = parseFloat(inputs.length) || 0;
  const offset = parseFloat(inputs.offset) || 0;
  if (length === 0) return { amountToTrim: 0, lengthOfDuct: 0, angle: 0 };
  const amountToTrim = (offset * width) / length;
  const lengthOfDuct = length + amountToTrim;
  const angle = Math.atan(offset / length) * (180 / Math.PI);
  return { amountToTrim, lengthOfDuct, angle };
}

function toFraction(decimal: number) {
  const sixteenths = Math.round(decimal * 16);
  let numerator = sixteenths;
  let denominator = 16;
  const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
  const divisor = gcd(Math.abs(numerator), denominator);
  numerator = numerator / divisor;
  denominator = denominator / divisor;
  return { numerator, denominator };
}

function formatMeasurement(value: number): string {
  if (value <= 0) return '0"';
  const inches = Math.floor(value);
  const decimal = value - inches;
  if (decimal < 0.03125) return `${inches}"`;
  const fraction = toFraction(decimal);
  if (fraction.numerator === 0 || fraction.denominator === 1) return `${inches}"`;
  if (inches === 0) return `${fraction.numerator}/${fraction.denominator}"`;
  return `${inches} ${fraction.numerator}/${fraction.denominator}"`;
}

// ---------------------------------------------------------------------------
// Translations (self-contained, synced with store language)
// ---------------------------------------------------------------------------

const translations = {
  en: {
    title: 'Offset Duct Calculator',
    subtitle: 'Professional HVAC Tools',
    inputs: 'Input Parameters',
    width: 'Width (in)',
    widthTooltip: 'Width of the duct cross-section',
    widthPlaceholder: 'e.g. 10',
    length: 'Overall Length (in)',
    lengthTooltip: 'Total horizontal length of the duct',
    lengthPlaceholder: 'e.g. 56',
    offset: 'Offset (in)',
    offsetTooltip: 'Vertical distance to offset the duct',
    offsetPlaceholder: 'e.g. 4',
    reset: 'Reset Fields',
    formula: 'Formula',
    amountToTrim: 'Amount to Trim',
    diagram: 'CUT PATTERN DIAGRAM',
    export: 'Export SVG',
    exportTooltip: 'Export diagram as SVG file',
    copy: 'Copy results',
    lengthOfDuct: 'Length of Duct',
    angle: 'Angle',
    ductNeeded: 'LENGTH OF DUCT NEEDED',
    amountToCut: 'AMOUNT TO CUT',
    angleWarningTitle: 'ANGLE EXCEEDED',
    angleWarning: (angle: string) =>
      `Cut angle of ${angle}° exceeds the recommended 23° maximum. This may cause the duct to expand, alter airflow, and increase static pressure. Reduce offset or increase overall length.`,
    cutPattern: 'CUT PATTERN',
    assembled: 'ASSEMBLED OFFSET',
    keep: 'KEEP',
    trim: 'TRIM',
    widthLabel: 'W',
    lengthLabel: 'L',
    trimLabel: 'A (Trim)',
    totalLabel: 'L + A',
    offsetLabel: 'O (Offset)',
  },
  es: {
    title: 'Calculadora de Offset para Ductos',
    subtitle: 'Herramientas Profesionales HVAC',
    inputs: 'Parámetros de Entrada',
    width: 'Ancho (pulg)',
    widthTooltip: 'Ancho de la sección transversal del ducto',
    widthPlaceholder: 'ej. 10',
    length: 'Longitud Total (pulg)',
    lengthTooltip: 'Longitud horizontal total del ducto',
    lengthPlaceholder: 'ej. 56',
    offset: 'Desplazamiento (pulg)',
    offsetTooltip: 'Distancia vertical del desplazamiento del ducto',
    offsetPlaceholder: 'ej. 4',
    reset: 'Restablecer',
    formula: 'Fórmula',
    amountToTrim: 'Cantidad a Recortar',
    diagram: 'DIAGRAMA DE PATRÓN DE CORTE',
    export: 'Exportar SVG',
    exportTooltip: 'Exportar diagrama como archivo SVG',
    copy: 'Copiar resultados',
    lengthOfDuct: 'Longitud del Ducto',
    angle: 'Ángulo',
    ductNeeded: 'LONGITUD DE DUCTO NECESARIA',
    amountToCut: 'CANTIDAD A CORTAR',
    angleWarningTitle: 'ÁNGULO EXCEDIDO',
    angleWarning: (angle: string) =>
      `El ángulo de corte de ${angle}° excede el máximo recomendado de 23°. Puede causar expansión del ducto, alteración del flujo de aire y mayor presión estática. Reduzca el desplazamiento o aumente la longitud total.`,
    cutPattern: 'PATRÓN DE CORTE',
    assembled: 'OFFSET ENSAMBLADO',
    keep: 'GUARDAR',
    trim: 'CORTAR',
    widthLabel: 'A',
    lengthLabel: 'L',
    trimLabel: 'R (Recorte)',
    totalLabel: 'L + R',
    offsetLabel: 'D (Despl.)',
  },
} as const;

// ---------------------------------------------------------------------------
// SVG Diagram
// ---------------------------------------------------------------------------

interface DiagramProps {
  inputs: Inputs;
  darkMode: boolean;
  language: 'en' | 'es';
}

function OffsetDiagram({ inputs, darkMode, language }: DiagramProps) {
  const t = translations[language];

  // Display values — fall back to representative defaults when inputs are empty
  const dW = parseFloat(inputs.width) || 10;
  const dL = parseFloat(inputs.length) || 56;
  const dO = parseFloat(inputs.offset) || 4;
  const dA = dL > 0 ? (dO * dW) / dL : 0;
  const dTotal = dL + dA;

  // ── Cut Pattern scaling ──────────────────────────────────────────────────
  // Area for cut-pattern: x 30..500, y 70..260  (470 × 190)
  const cpAvailW = 430;
  const cpAvailH = 150;
  const cpScaleX = cpAvailW / dTotal;
  const cpScaleY = cpAvailH / dW;
  const cpScale = Math.min(cpScaleX, cpScaleY) * 0.82;

  const cpW_px = dTotal * cpScale;
  const cpH_px = dW * cpScale;
  const cpL_px = dL * cpScale;
  const cpA_px = dA * cpScale;

  const cpX = 40 + (cpAvailW - cpW_px) / 2;
  const cpY = 110 + (cpAvailH - cpH_px) / 2;

  // Key cut-pattern corners
  const tl = { x: cpX, y: cpY };
  const tr = { x: cpX + cpW_px, y: cpY };
  const bl = { x: cpX, y: cpY + cpH_px };
  const br = { x: cpX + cpW_px, y: cpY + cpH_px };
  const cutTop = { x: cpX + cpL_px, y: cpY };       // cut hits top edge at L
  const cutBot = { x: cpX + cpW_px, y: cpY + cpH_px }; // cut hits bottom-right corner

  const keepPoly = `${tl.x},${tl.y} ${cutTop.x},${cutTop.y} ${cutBot.x},${cutBot.y} ${bl.x},${bl.y}`;
  const trimPoly = `${cutTop.x},${cutTop.y} ${tr.x},${tr.y} ${br.x},${br.y}`;

  // ── Assembled offset scaling ─────────────────────────────────────────────
  // Area: x 530..780, y 60..350  (250 × 290)
  const aoAvailW = 200;
  const aoAvailH = 250;
  const aoScaleX = aoAvailW / (dL * 0.45 + dW * 0.5);
  const aoScaleY = aoAvailH / (dW * 2.5 + dO);
  const aoScale = Math.min(aoScaleX, aoScaleY) * 0.78;

  const aoDuctW = dW * aoScale;   // duct width in px (vertical)
  const aoLen = dL * aoScale * 0.4; // horizontal length of each arm
  const aoOff = dO * aoScale;     // offset in px (vertical)

  // Center the assembled diagram in its area
  const aoStartX = 535 + (aoAvailW - aoLen) / 2;
  const aoStartY = 80 + (aoAvailH - (aoDuctW * 2 + aoOff)) / 2;

  // Piece 1: left arm going right, positioned at top
  const p1x1 = aoStartX;
  const p1y1 = aoStartY;
  const p1x2 = aoStartX + aoLen;
  const p1y2 = aoStartY + aoDuctW;

  // Piece 2: right arm going right, shifted down by aoOff
  const p2x1 = aoStartX;
  const p2y1 = aoStartY + aoDuctW + aoOff;
  const p2x2 = aoStartX + aoLen;
  const p2y2 = aoStartY + aoDuctW * 2 + aoOff;

  // Connector (angled section) — parallelogram linking the two arms
  // Right edge of piece 1 connects diagonally to left edge of piece 2
  const connPoly = `${p1x2},${p1y1} ${p1x2},${p1y2} ${p2x1},${p2y2} ${p2x1},${p2y1}`;

  const textColor = darkMode ? '#e2e8f0' : '#1e293b';
  const dimColor = darkMode ? '#94a3b8' : '#64748b';
  const strokeColor = darkMode ? '#60a5fa' : '#2563eb';
  const bgRect = darkMode ? '#1e293b' : '#f8fafc';
  const sectionBg = darkMode ? '#0f172a' : '#eff6ff';

  return (
    <svg
      viewBox="0 0 800 380"
      className="w-full rounded-lg border"
      style={{
        background: darkMode
          ? 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)'
          : 'linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%)',
        borderColor: darkMode ? '#334155' : '#bfdbfe',
      }}
    >
      <defs>
        {/* Red diagonal hatch for trim region */}
        <pattern id="hatch-trim" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="6" stroke="#ef4444" strokeWidth="1.8" />
        </pattern>
        {/* Blue diagonal hatch for keep region */}
        <pattern id="hatch-keep" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="8" stroke={darkMode ? '#3b82f6' : '#93c5fd'} strokeWidth="1.2" />
        </pattern>
        <marker id="arrow-start" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse">
          <path d="M0,4 L8,0 L8,8 Z" fill={dimColor} />
        </marker>
        <marker id="arrow-end" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill={dimColor} />
        </marker>
      </defs>

      {/* ── Section backgrounds ─────────────────────────────────────────── */}
      <rect x="10" y="10" width="510" height="360" rx="8" fill={sectionBg} opacity="0.6" />
      <rect x="525" y="10" width="265" height="360" rx="8" fill={sectionBg} opacity="0.6" />

      {/* ── Section titles ──────────────────────────────────────────────── */}
      <text x="265" y="36" textAnchor="middle" fontSize="11" fontWeight="700"
        fill={strokeColor} fontFamily="monospace" letterSpacing="2">
        {t.cutPattern}
      </text>
      <text x="657" y="36" textAnchor="middle" fontSize="11" fontWeight="700"
        fill={strokeColor} fontFamily="monospace" letterSpacing="2">
        {t.assembled}
      </text>

      {/* ── CUT PATTERN ─────────────────────────────────────────────────── */}

      {/* Keep region (parallelogram) */}
      <polygon points={keepPoly} fill="url(#hatch-keep)" opacity="0.5" />
      <polygon points={keepPoly} fill="none" stroke={strokeColor} strokeWidth="2" />

      {/* Trim region (triangle) */}
      <polygon points={trimPoly} fill="url(#hatch-trim)" opacity="0.7" />
      <polygon points={trimPoly} fill="none" stroke="#ef4444" strokeWidth="1.5" strokeDasharray="5,3" />

      {/* Cut line (the diagonal cut) */}
      <line
        x1={cutTop.x} y1={cutTop.y}
        x2={cutBot.x} y2={cutBot.y}
        stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round"
      />

      {/* Labels on regions */}
      <text x={cpX + cpL_px * 0.45} y={cpY + cpH_px / 2 + 5}
        textAnchor="middle" fontSize="13" fontWeight="800"
        fill={darkMode ? '#93c5fd' : '#1d4ed8'} fontFamily="sans-serif">
        {t.keep}
      </text>
      {cpA_px > 18 && (
        <text x={cutTop.x + cpA_px * 0.35} y={cpY + cpH_px * 0.38}
          textAnchor="middle" fontSize="11" fontWeight="700"
          fill="#dc2626" fontFamily="sans-serif">
          {t.trim}
        </text>
      )}

      {/* ── Dimension lines (cut pattern) ───────────────────────────────── */}

      {/* Width (W) — left side */}
      <line x1={cpX - 18} y1={cpY} x2={cpX - 18} y2={cpY + cpH_px}
        stroke={dimColor} strokeWidth="1" markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
      <text x={cpX - 28} y={cpY + cpH_px / 2 + 4}
        textAnchor="middle" fontSize="10" fill={dimColor} fontFamily="monospace"
        transform={`rotate(-90, ${cpX - 28}, ${cpY + cpH_px / 2 + 4})`}>
        W = {formatMeasurement(dW)}
      </text>

      {/* L — top edge, left portion */}
      <line x1={cpX} y1={cpY - 18} x2={cutTop.x} y2={cpY - 18}
        stroke={dimColor} strokeWidth="1" markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
      <text x={cpX + cpL_px / 2} y={cpY - 22}
        textAnchor="middle" fontSize="10" fill={dimColor} fontFamily="monospace">
        L = {formatMeasurement(dL)}
      </text>

      {/* A (Trim) — top edge, right portion */}
      {cpA_px > 14 && (
        <>
          <line x1={cutTop.x} y1={cpY - 18} x2={tr.x} y2={cpY - 18}
            stroke="#ef4444" strokeWidth="1" markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
          <text x={cutTop.x + cpA_px / 2} y={cpY - 22}
            textAnchor="middle" fontSize="10" fill="#ef4444" fontFamily="monospace">
            A = {formatMeasurement(dA)}
          </text>
        </>
      )}

      {/* Total length — bottom edge */}
      <line x1={cpX} y1={cpY + cpH_px + 22} x2={cpX + cpW_px} y2={cpY + cpH_px + 22}
        stroke={dimColor} strokeWidth="1" markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
      <text x={cpX + cpW_px / 2} y={cpY + cpH_px + 36}
        textAnchor="middle" fontSize="10" fill={dimColor} fontFamily="monospace">
        {t.totalLabel} = {formatMeasurement(dTotal)}
      </text>

      {/* ── ASSEMBLED OFFSET ────────────────────────────────────────────── */}

      {/* Piece 1 — top arm */}
      <rect x={p1x1} y={p1y1} width={aoLen} height={aoDuctW}
        fill={darkMode ? '#1d4ed8' : '#dbeafe'} stroke={strokeColor} strokeWidth="1.5" rx="1" />

      {/* Connector — angled section */}
      <polygon points={connPoly}
        fill={darkMode ? '#1e40af' : '#bfdbfe'} stroke={strokeColor} strokeWidth="1.5" />

      {/* Piece 2 — bottom arm */}
      <rect x={p2x1} y={p2y1} width={aoLen} height={aoDuctW}
        fill={darkMode ? '#1d4ed8' : '#dbeafe'} stroke={strokeColor} strokeWidth="1.5" rx="1" />

      {/* Offset dimension arrow */}
      {aoOff > 6 && (
        <>
          <line x1={p1x2 + 18} y1={p1y2} x2={p1x2 + 18} y2={p2y1}
            stroke="#f59e0b" strokeWidth="1.2"
            markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
          <text x={p1x2 + 30} y={(p1y2 + p2y1) / 2 + 4}
            textAnchor="start" fontSize="10" fill="#f59e0b" fontFamily="monospace">
            O = {formatMeasurement(dO)}
          </text>
        </>
      )}

      {/* Width annotation on assembled */}
      {aoDuctW > 10 && (
        <>
          <line x1={p1x1 - 14} y1={p1y1} x2={p1x1 - 14} y2={p1y2}
            stroke={dimColor} strokeWidth="1"
            markerStart="url(#arrow-start)" markerEnd="url(#arrow-end)" />
          <text x={p1x1 - 20} y={(p1y1 + p1y2) / 2 + 4}
            textAnchor="middle" fontSize="9" fill={dimColor} fontFamily="monospace"
            transform={`rotate(-90, ${p1x1 - 20}, ${(p1y1 + p1y2) / 2 + 4})`}>
            W
          </text>
        </>
      )}

      {/* ── Legend ──────────────────────────────────────────────────────── */}
      <rect x="20" y="330" width="12" height="12" rx="2"
        fill="url(#hatch-keep)" opacity="0.8" stroke={strokeColor} strokeWidth="1" />
      <text x="36" y="341" fontSize="10" fill={textColor} fontFamily="sans-serif">{t.keep}</text>

      <rect x="90" y="330" width="12" height="12" rx="2"
        fill="url(#hatch-trim)" opacity="0.9" stroke="#ef4444" strokeWidth="1" />
      <text x="106" y="341" fontSize="10" fill={textColor} fontFamily="sans-serif">{t.trim}</text>

      <line x1="160" y1="336" x2="180" y2="336" stroke="#f59e0b" strokeWidth="2.5" strokeLinecap="round" />
      <text x="185" y="341" fontSize="10" fill={textColor} fontFamily="sans-serif">Cut Line</text>

      {/* formula reminder */}
      <text x="265" y="355" textAnchor="middle" fontSize="9" fill={dimColor} fontFamily="monospace">
        A = (O × W) ÷ L
      </text>
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function DuctOffsetCalculator() {
  const { theme, language } = useHVACStore();
  const darkMode = theme === 'dark';
  const t = translations[language as 'en' | 'es'] ?? translations.en;

  const [inputs, setInputs] = React.useState<Inputs>({ width: '', length: '', offset: '' });
  const svgContainerRef = useRef<HTMLDivElement>(null);

  const result = calcOffset(inputs);
  const isAngleExceeded = result.angle > 23 && result.angle > 0;

  const handleInputChange = (field: keyof Inputs, value: string) => {
    setInputs((prev) => ({ ...prev, [field]: value }));
  };

  const resetToDefaults = () => setInputs({ width: '', length: '', offset: '' });

  const copyToClipboard = () => {
    const text = [
      'OFFSET DUCT CALCULATOR',
      '',
      `Width             = ${inputs.width || '0'}"`,
      `Overall Length    = ${inputs.length || '0'}"`,
      `Offset            = ${inputs.offset || '0'}"`,
      `Length of Duct    = ${formatMeasurement(result.lengthOfDuct)}`,
      `Amount to Trim    = ${formatMeasurement(result.amountToTrim)}`,
      `Angle             = ${result.angle.toFixed(2)}°`,
    ].join('\n');
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const exportSVG = () => {
    const svgEl = svgContainerRef.current?.querySelector('svg');
    if (!svgEl) return;
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgEl);
    const blob = new Blob([svgString], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'duct-offset-diagram.svg';
    link.click();
    URL.revokeObjectURL(url);
  };

  const card = darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200';
  const input = darkMode
    ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-500'
    : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400';
  const label = darkMode ? 'text-gray-300' : 'text-gray-600';
  const muted = darkMode ? 'text-gray-400' : 'text-gray-500';

  return (
    <div className={`h-full overflow-y-auto ${darkMode ? 'bg-gray-900 text-white' : 'bg-gradient-to-br from-blue-50 to-indigo-100 text-gray-900'}`}>
      <div className="max-w-6xl mx-auto p-4 lg:p-6 space-y-4">

        {/* Header */}
        <div className={`rounded-xl border shadow-sm p-4 flex items-center justify-between ${card}`}>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Calculator className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                {t.title}
              </h1>
              <p className={`text-xs ${muted}`}>{t.subtitle}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={copyToClipboard} title={t.copy}
              className={`p-2 rounded-lg border transition-all ${darkMode ? 'bg-gray-700 hover:bg-gray-600 border-gray-600' : 'bg-gray-100 hover:bg-gray-200 border-gray-300'}`}>
              <Copy className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Angle warning */}
        {isAngleExceeded && (
          <div className="rounded-xl border-2 border-amber-500 bg-amber-50 dark:bg-amber-900/20 p-4 flex gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-amber-700 dark:text-amber-400 text-sm">{t.angleWarningTitle}</p>
              <p className="text-amber-700 dark:text-amber-300 text-xs mt-1">
                {t.angleWarning(result.angle.toFixed(1))}
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">

          {/* ── Inputs ── */}
          <div className={`rounded-xl border shadow-lg p-5 space-y-4 ${card}`}>
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-500" />
              {t.inputs}
            </h2>

            {(
              [
                { key: 'width', label: t.width, tooltip: t.widthTooltip, placeholder: t.widthPlaceholder },
                { key: 'length', label: t.length, tooltip: t.lengthTooltip, placeholder: t.lengthPlaceholder },
                { key: 'offset', label: t.offset, tooltip: t.offsetTooltip, placeholder: t.offsetPlaceholder },
              ] as const
            ).map(({ key, label: lbl, tooltip, placeholder }) => (
              <div key={key}>
                <label className={`block text-xs font-medium mb-1 ${label} flex items-center gap-1`}>
                  {lbl}
                  <span className="group relative cursor-help">
                    <HelpCircle className="w-3 h-3 opacity-50" />
                    <span className="invisible group-hover:visible absolute left-0 top-5 bg-gray-800 text-white text-xs rounded px-2 py-1 w-40 z-20 shadow-lg">
                      {tooltip}
                    </span>
                  </span>
                </label>
                <input
                  type="number"
                  min="0"
                  value={inputs[key]}
                  onChange={(e) => handleInputChange(key, e.target.value)}
                  placeholder={placeholder}
                  className={`w-full px-3 py-2 border rounded-lg text-base font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${input}`}
                />
              </div>
            ))}

            <button onClick={resetToDefaults}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-all text-sm font-medium">
              <RotateCw className="w-3.5 h-3.5" />
              {t.reset}
            </button>

            {/* Formula box */}
            <div className={`p-4 rounded-xl border-2 ${darkMode ? 'bg-blue-900/30 border-blue-700' : 'bg-blue-50 border-blue-200'}`}>
              <h3 className="text-xs font-bold text-blue-600 mb-2 flex items-center gap-1">
                <span>📐</span> {t.formula}
              </h3>
              <div className={`text-xs font-mono space-y-1 ${muted}`}>
                <p>A = (O × W) ÷ L</p>
                <p className="opacity-70">= ({inputs.offset || '0'} × {inputs.width || '0'}) ÷ {inputs.length || '0'}</p>
                <p className="font-bold text-sm text-blue-600 mt-2">= {formatMeasurement(result.amountToTrim)}</p>
              </div>
            </div>
          </div>

          {/* ── Diagram + Results ── */}
          <div className="xl:col-span-3 space-y-4">

            {/* Result cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Width', value: formatMeasurement(parseFloat(inputs.width) || 0), color: 'blue' },
                { label: t.lengthOfDuct, value: formatMeasurement(result.lengthOfDuct), color: 'indigo' },
                { label: t.amountToTrim, value: formatMeasurement(result.amountToTrim), color: 'amber' },
                {
                  label: t.angle,
                  value: `${result.angle.toFixed(2)}°`,
                  color: isAngleExceeded ? 'red' : 'green',
                },
              ].map(({ label: lbl, value, color }) => (
                <div key={lbl}
                  className={`rounded-xl border p-3 text-center shadow-sm ${card}`}
                  style={{ borderTopWidth: 3, borderTopColor: colorMap[color] }}>
                  <p className={`text-xs font-medium ${muted} mb-1`}>{lbl}</p>
                  <p className="text-xl font-bold" style={{ color: colorMap[color] }}>{value}</p>
                </div>
              ))}
            </div>

            {/* Diagram card */}
            <div className={`rounded-xl border-2 shadow-lg p-4 ${darkMode ? 'border-blue-700 bg-gray-800' : 'border-blue-200 bg-white'}`}>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent tracking-widest">
                  {t.diagram}
                </h2>
                <button onClick={exportSVG} title={t.exportTooltip}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow">
                  <Download className="w-3.5 h-3.5" />
                  {t.export}
                </button>
              </div>
              <div ref={svgContainerRef}>
                <OffsetDiagram inputs={inputs} darkMode={darkMode} language={language as 'en' | 'es'} />
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

// Color helper
const colorMap: Record<string, string> = {
  blue: '#2563eb',
  indigo: '#4f46e5',
  amber: '#d97706',
  green: '#16a34a',
  red: '#dc2626',
};
