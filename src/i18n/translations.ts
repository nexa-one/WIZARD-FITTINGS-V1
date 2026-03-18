export interface Translations {
  // App / toolbar
  appTitle: string;
  gaugeLabel: string;
  orderLabel: string;
  itemsCount: (n: number) => string;
  themeToggleDark: string;
  themeToggleLight: string;

  // Module tab labels
  tabAI: string;
  tabParametric: string;
  tabWizard: string;

  // View mode labels
  view3D: string;
  viewCNC: string;
  viewXRay: string;

  // AI Generator
  aiTitle: string;
  aiDescribeLabel: string;
  aiDescribePlaceholder: string;
  aiAnalyzing: string;
  aiGenerate: string;
  aiUpload: string;
  aiInterpretation: string;
  aiConfidence: (pct: number) => string;
  aiFittingType: string;
  aiShape: string;
  aiWidth: string;
  aiHeight: string;
  aiDiameter: string;
  aiLength: string;
  aiAcceptBuild: string;

  // Parametric Builder
  parametricTitle: string;
  shapeType: string;
  fittingType: string;
  shapeRectangular: string;
  shapeRound: string;
  shapeOval: string;
  inletWidth: string;
  inletHeight: string;
  inletDiameter: string;
  outletWidth: string;
  outletHeight: string;
  outletDiameter: string;
  length: string;
  neckLength: string;
  connection: string;
  wallType: string;
  singleWall: string;
  doubleWall: string;
  insulationThickness: string;
  gauge: string;
  alignment: string;
  alignCentered: string;
  alignCenterline: string;
  alignLeft: string;
  alignRight: string;
  linerPerforation: string;
  holeDia: string;
  spacing: string;
  notes: string;
  notesPlaceholder: string;
  buildFitting: string;

  // Wizard
  wizardTitle: string;
  wizardSteps: string[];
  wizardBack: string;
  wizardNext: string;

  // SelectGeometry
  selectGeometryPrompt: string;
  fittingStraightDuct: string;
  fittingElbow90: string;
  fittingElbow45: string;
  fittingTransition: string;
  fittingReducer: string;
  fittingOffset: string;
  fittingTee: string;
  fittingCross: string;
  fittingCap: string;
  fittingRegisterBox: string;

  // SelectElevationCode
  selectElevationPrompt: string;
  elevLevel1: string;
  elevLevel2: string;
  elevLevel3: string;
  elevLevel4: string;
  elevLevel5: string;
  elevUpward: string;
  elevDownward: string;
  elevLevelFlat: string;
  elevDropDown: string;
  elevRiseUp: string;

  // SelectPlanCode
  selectPlanPrompt: string;
  planLeftTurn: string;
  planRightTurn: string;
  planStraight: string;
  planTee: string;
  planCross: string;
  planLeftUp: string;
  planLeftDown: string;
  planRightUp: string;
  planRightDown: string;

  // EnterDimensions
  inletDimensions: string;
  outletDimensions: string;
  dimensionWidth: string;
  dimensionHeight: string;
  outletDiameterLabel: string;

  // SelectWallConstruction
  wallSingleLabel: string;
  wallDoubleLabel: string;
  wallSingleDesc: string;
  wallDoubleDesc: string;

  // PreviewConfirm
  previewPrompt: string;
  previewFittingType: string;
  previewShape: string;
  previewElevationCode: string;
  previewPlanCode: string;
  previewInletDiameter: string;
  previewInletSize: string;
  previewLength: string;
  previewNeckLength: string;
  previewWallType: string;
  previewGauge: string;
  previewInsulation: string;
  buildFittingBtn: string;

  // Order Panel
  orderPanelTitle: string;
  currentOrder: string;
  noActiveOrder: string;
  addToOrder: string;
  newOrder: string;
  itemsHeader: string;
  allOrders: string;
  gaugeShort: string;

  // Viewport
  noGeometry: string;
}

export const en: Translations = {
  appTitle: 'HVAC Parametric Engine v7.0',
  gaugeLabel: 'Gauge (WG):',
  orderLabel: 'Order:',
  itemsCount: (n) => `(${n} item${n !== 1 ? 's' : ''})`,
  themeToggleDark: '🌙 Dark',
  themeToggleLight: '☀️ Light',

  tabAI: '🤖 AI',
  tabParametric: '⚙️ Build',
  tabWizard: '🧙 Wizard',

  view3D: '3D',
  viewCNC: 'CNC',
  viewXRay: 'X-RAY',

  aiTitle: 'AI Smart Generator',
  aiDescribeLabel: 'Describe your fitting...',
  aiDescribePlaceholder: 'e.g. 90 degree elbow 12x8 rectangular, or 6 inch round transition to 4 inch...',
  aiAnalyzing: '⏳ Analyzing...',
  aiGenerate: '🤖 Generate',
  aiUpload: '📷 Upload',
  aiInterpretation: 'AI Interpretation',
  aiConfidence: (pct) => `${pct}% confidence`,
  aiFittingType: 'Fitting Type:',
  aiShape: 'Shape:',
  aiWidth: 'Width:',
  aiHeight: 'Height:',
  aiDiameter: 'Diameter:',
  aiLength: 'Length:',
  aiAcceptBuild: '✅ Accept & Build',

  parametricTitle: 'Manual Parametric Builder',
  shapeType: 'Shape Type',
  fittingType: 'Fitting Type',
  shapeRectangular: 'Rectangular',
  shapeRound: 'Round',
  shapeOval: 'Oval',
  inletWidth: 'Inlet Width (")',
  inletHeight: 'Inlet Height (")',
  inletDiameter: 'Inlet Diameter (")',
  outletWidth: 'Outlet Width (")',
  outletHeight: 'Outlet Height (")',
  outletDiameter: 'Outlet Diameter (")',
  length: 'Length (")',
  neckLength: 'Neck Length (")',
  connection: 'Connection',
  wallType: 'Wall Type',
  singleWall: 'Single Wall',
  doubleWall: 'Double Wall',
  insulationThickness: 'Insulation Thickness (")',
  gauge: 'Gauge (WG)',
  alignment: 'Alignment',
  alignCentered: 'Centered',
  alignCenterline: 'Centerline',
  alignLeft: 'Left',
  alignRight: 'Right',
  linerPerforation: 'Liner Perforation',
  holeDia: 'Hole Dia (")',
  spacing: 'Spacing (")',
  notes: 'Notes',
  notesPlaceholder: 'Optional notes...',
  buildFitting: '🔧 Build Fitting',

  wizardTitle: 'Wizard Fittings',
  wizardSteps: ['Geometry', 'Elevation', 'Plan', 'Dimensions', 'Wall', 'Confirm'],
  wizardBack: '← Back',
  wizardNext: 'Next →',

  selectGeometryPrompt: 'Select fitting geometry type:',
  fittingStraightDuct: 'Straight Duct',
  fittingElbow90: 'Elbow 90°',
  fittingElbow45: 'Elbow 45°',
  fittingTransition: 'Transition',
  fittingReducer: 'Reducer',
  fittingOffset: 'Offset',
  fittingTee: 'Tee',
  fittingCross: 'Cross',
  fittingCap: 'Cap',
  fittingRegisterBox: 'Register Box',

  selectElevationPrompt: 'Select elevation code:',
  elevLevel1: 'Level 1',
  elevLevel2: 'Level 2',
  elevLevel3: 'Level 3',
  elevLevel4: 'Level 4',
  elevLevel5: 'Level 5',
  elevUpward: 'Upward',
  elevDownward: 'Downward',
  elevLevelFlat: 'Level/Flat',
  elevDropDown: 'Drop Down',
  elevRiseUp: 'Rise Up',

  selectPlanPrompt: 'Select plan code:',
  planLeftTurn: 'Left Turn',
  planRightTurn: 'Right Turn',
  planStraight: 'Straight',
  planTee: 'Tee',
  planCross: 'Cross',
  planLeftUp: 'Left-Up',
  planLeftDown: 'Left-Down',
  planRightUp: 'Right-Up',
  planRightDown: 'Right-Down',

  inletDimensions: 'Inlet Dimensions',
  outletDimensions: 'Outlet Dimensions',
  dimensionWidth: 'Width (")',
  dimensionHeight: 'Height (")',
  outletDiameterLabel: 'Outlet Diameter (")',

  wallSingleLabel: 'Single Wall',
  wallDoubleLabel: 'Double Wall',
  wallSingleDesc: 'Standard',
  wallDoubleDesc: 'Insulated',

  previewPrompt: 'Review your fitting configuration:',
  previewFittingType: 'Fitting Type',
  previewShape: 'Shape',
  previewElevationCode: 'Elevation Code',
  previewPlanCode: 'Plan Code',
  previewInletDiameter: 'Inlet Diameter',
  previewInletSize: 'Inlet Size',
  previewLength: 'Length',
  previewNeckLength: 'Neck Length',
  previewWallType: 'Wall Type',
  previewGauge: 'Gauge',
  previewInsulation: 'Insulation',
  buildFittingBtn: '🔧 Build Fitting',

  orderPanelTitle: 'Order Panel',
  currentOrder: 'Current Order',
  noActiveOrder: 'No active order',
  addToOrder: '+ Add to Order',
  newOrder: 'New Order',
  itemsHeader: 'Items',
  allOrders: 'All Orders',
  gaugeShort: 'Gauge:',

  noGeometry: 'No geometry built yet',
};

export const es: Translations = {
  appTitle: 'Motor Paramétrico HVAC v7.0',
  gaugeLabel: 'Calibre (WG):',
  orderLabel: 'Pedido:',
  itemsCount: (n) => `(${n} artículo${n !== 1 ? 's' : ''})`,
  themeToggleDark: '🌙 Oscuro',
  themeToggleLight: '☀️ Claro',

  tabAI: '🤖 IA',
  tabParametric: '⚙️ Construir',
  tabWizard: '🧙 Asistente',

  view3D: '3D',
  viewCNC: 'CNC',
  viewXRay: 'RX',

  aiTitle: 'Generador IA Inteligente',
  aiDescribeLabel: 'Describe tu fitting...',
  aiDescribePlaceholder: 'Ej. codo 90° rectangular 12x8, o transición redonda de 6 pulgadas a 4 pulgadas...',
  aiAnalyzing: '⏳ Analizando...',
  aiGenerate: '🤖 Generar',
  aiUpload: '📷 Subir',
  aiInterpretation: 'Interpretación IA',
  aiConfidence: (pct) => `${pct}% confianza`,
  aiFittingType: 'Tipo de Fitting:',
  aiShape: 'Forma:',
  aiWidth: 'Ancho:',
  aiHeight: 'Alto:',
  aiDiameter: 'Diámetro:',
  aiLength: 'Longitud:',
  aiAcceptBuild: '✅ Aceptar y Construir',

  parametricTitle: 'Constructor Paramétrico Manual',
  shapeType: 'Tipo de Forma',
  fittingType: 'Tipo de Fitting',
  shapeRectangular: 'Rectangular',
  shapeRound: 'Redondo',
  shapeOval: 'Oval',
  inletWidth: 'Ancho de Entrada (")',
  inletHeight: 'Alto de Entrada (")',
  inletDiameter: 'Diámetro de Entrada (")',
  outletWidth: 'Ancho de Salida (")',
  outletHeight: 'Alto de Salida (")',
  outletDiameter: 'Diámetro de Salida (")',
  length: 'Longitud (")',
  neckLength: 'Long. de Cuello (")',
  connection: 'Conexión',
  wallType: 'Tipo de Pared',
  singleWall: 'Pared Simple',
  doubleWall: 'Pared Doble',
  insulationThickness: 'Espesor de Aislamiento (")',
  gauge: 'Calibre (WG)',
  alignment: 'Alineación',
  alignCentered: 'Centrado',
  alignCenterline: 'Línea Central',
  alignLeft: 'Izquierda',
  alignRight: 'Derecha',
  linerPerforation: 'Perforación de Forro',
  holeDia: 'Diám. Agujero (")',
  spacing: 'Espaciado (")',
  notes: 'Notas',
  notesPlaceholder: 'Notas opcionales...',
  buildFitting: '🔧 Construir Fitting',

  wizardTitle: 'Asistente de Fittings',
  wizardSteps: ['Geometría', 'Elevación', 'Plano', 'Dimensiones', 'Pared', 'Confirmar'],
  wizardBack: '← Atrás',
  wizardNext: 'Siguiente →',

  selectGeometryPrompt: 'Selecciona el tipo de geometría:',
  fittingStraightDuct: 'Ducto Recto',
  fittingElbow90: 'Codo 90°',
  fittingElbow45: 'Codo 45°',
  fittingTransition: 'Transición',
  fittingReducer: 'Reductor',
  fittingOffset: 'Desplazamiento',
  fittingTee: 'Te',
  fittingCross: 'Cruz',
  fittingCap: 'Tapa',
  fittingRegisterBox: 'Caja de Registro',

  selectElevationPrompt: 'Selecciona el código de elevación:',
  elevLevel1: 'Nivel 1',
  elevLevel2: 'Nivel 2',
  elevLevel3: 'Nivel 3',
  elevLevel4: 'Nivel 4',
  elevLevel5: 'Nivel 5',
  elevUpward: 'Hacia Arriba',
  elevDownward: 'Hacia Abajo',
  elevLevelFlat: 'Horizontal/Plano',
  elevDropDown: 'Bajada',
  elevRiseUp: 'Subida',

  selectPlanPrompt: 'Selecciona el código de plano:',
  planLeftTurn: 'Giro Izq.',
  planRightTurn: 'Giro Der.',
  planStraight: 'Recto',
  planTee: 'Te',
  planCross: 'Cruz',
  planLeftUp: 'Izq.-Arriba',
  planLeftDown: 'Izq.-Abajo',
  planRightUp: 'Der.-Arriba',
  planRightDown: 'Der.-Abajo',

  inletDimensions: 'Dimensiones de Entrada',
  outletDimensions: 'Dimensiones de Salida',
  dimensionWidth: 'Ancho (")',
  dimensionHeight: 'Alto (")',
  outletDiameterLabel: 'Diámetro de Salida (")',

  wallSingleLabel: 'Pared Simple',
  wallDoubleLabel: 'Pared Doble',
  wallSingleDesc: 'Estándar',
  wallDoubleDesc: 'Aislada',

  previewPrompt: 'Revisa tu configuración de fitting:',
  previewFittingType: 'Tipo de Fitting',
  previewShape: 'Forma',
  previewElevationCode: 'Código de Elevación',
  previewPlanCode: 'Código de Plano',
  previewInletDiameter: 'Diámetro de Entrada',
  previewInletSize: 'Tamaño de Entrada',
  previewLength: 'Longitud',
  previewNeckLength: 'Long. de Cuello',
  previewWallType: 'Tipo de Pared',
  previewGauge: 'Calibre',
  previewInsulation: 'Aislamiento',
  buildFittingBtn: '🔧 Construir Fitting',

  orderPanelTitle: 'Panel de Pedido',
  currentOrder: 'Pedido Actual',
  noActiveOrder: 'Sin pedido activo',
  addToOrder: '+ Agregar al Pedido',
  newOrder: 'Nuevo Pedido',
  itemsHeader: 'Artículos',
  allOrders: 'Todos los Pedidos',
  gaugeShort: 'Calibre:',

  noGeometry: 'Aún no se construyó geometría',
};
