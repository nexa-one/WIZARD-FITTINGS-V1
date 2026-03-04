export enum FittingType {
  STRAIGHT_DUCT = 'STRAIGHT_DUCT',
  ELBOW_90 = 'ELBOW_90',
  ELBOW_45 = 'ELBOW_45',
  TRANSITION = 'TRANSITION',
  REDUCER = 'REDUCER',
  OFFSET = 'OFFSET',
  TEE = 'TEE',
  CROSS = 'CROSS',
  CAP = 'CAP',
  REGISTER_BOX = 'REGISTER_BOX',
}

export enum ShapeType {
  RECTANGULAR = 'RECTANGULAR',
  ROUND = 'ROUND',
  OVAL = 'OVAL',
}

export enum ConnectionType {
  TDC = 'TDC',
  DUCTMATE = 'DUCTMATE',
  SLIP_AND_DRIVE = 'SLIP_AND_DRIVE',
}

export enum WallType {
  SINGLE_WALL = 'SINGLE_WALL',
  DOUBLE_WALL = 'DOUBLE_WALL',
}

export enum DimensionMode {
  EXTERNAL_OD = 'EXTERNAL_OD',
  INTERNAL_ID = 'INTERNAL_ID',
}

export enum ElevationCode {
  E1 = 'E1',
  E2 = 'E2',
  E3 = 'E3',
  E4 = 'E4',
  E5 = 'E5',
  UP = 'UP',
  DOWN = 'DOWN',
  LEVEL = 'LEVEL',
  DROP = 'DROP',
  RISE = 'RISE',
}

export enum PlanCode {
  L = 'L',
  R = 'R',
  S = 'S',
  T = 'T',
  X = 'X',
  LU = 'LU',
  LD = 'LD',
  RU = 'RU',
  RD = 'RD',
}

export interface ParametricSolidDefinition {
  id: string;
  fittingType: FittingType;
  shapeType: ShapeType;
  inletWidth?: number;
  inletHeight?: number;
  inletDiameter?: number;
  outletWidth?: number;
  outletHeight?: number;
  outletDiameter?: number;
  length: number;
  neckLength: number;
  wallType: WallType;
  wallGauge: number;
  insulation?: number;
  linerPerforation?: { holeDiameter: number; spacing: number };
  connectionType: ConnectionType;
  dimensionMode: DimensionMode;
  alignment: 'CENTERED' | 'CENTERLINE' | 'LEFT' | 'RIGHT';
  orderId?: string;
  notes?: string;
  elevationCode?: string;
  planCode?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface OrderItem {
  psd: ParametricSolidDefinition;
  quantity: number;
  addedAt: string;
}

export interface Order {
  orderId: string;
  timestamp: string;
  items: OrderItem[];
  status: 'DRAFT' | 'SUBMITTED' | 'IN_PRODUCTION' | 'COMPLETE';
}

export interface PanelState {
  id: string;
  title: string;
  visible: boolean;
  docked: 'left' | 'right' | 'floating';
  x: number;
  y: number;
}
