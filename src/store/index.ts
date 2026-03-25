import { create } from 'zustand';
import * as THREE from 'three';
import {
  ParametricSolidDefinition,
  ValidationResult,
  Order,
  DimensionMode,
  PanelState,
} from '../types/hvac';
import { processPSD } from '../engine';

interface HVACStore {
  activeModule: 'ai' | 'parametric' | 'wizard' | 'calculator';
  setActiveModule: (m: 'ai' | 'parametric' | 'wizard' | 'calculator') => void;

  currentPSD: Partial<ParametricSolidDefinition> | null;
  setCurrentPSD: (psd: Partial<ParametricSolidDefinition>) => void;

  builtGeometry: THREE.BufferGeometry | null;
  buildGeometry: () => void;

  validationResult: ValidationResult | null;

  theme: 'dark' | 'light';
  toggleTheme: () => void;

  dimensionMode: DimensionMode;
  toggleDimensionMode: () => void;

  viewMode: '3D_VISUAL' | 'CNC_FLAT_PATTERN' | 'X_RAY_TRANSPARENT';
  setViewMode: (m: '3D_VISUAL' | 'CNC_FLAT_PATTERN' | 'X_RAY_TRANSPARENT') => void;

  orders: Order[];
  currentOrder: Order | null;
  addItemToOrder: (psd: ParametricSolidDefinition) => void;
  newOrder: () => void;

  language: 'en' | 'es';
  toggleLanguage: () => void;

  waterGauge: number;
  setWaterGauge: (g: number) => void;

  panels: PanelState[];
}

let orderCounter = 1000;

function generateOrderId(): string {
  return `ORD-${++orderCounter}`;
}

export const useHVACStore = create<HVACStore>((set, get) => ({
  activeModule: 'wizard',
  setActiveModule: (m) => set({ activeModule: m }),

  currentPSD: null,
  setCurrentPSD: (psd) => set({ currentPSD: psd }),

  builtGeometry: null,
  buildGeometry: () => {
    const { currentPSD } = get();
    if (!currentPSD) return;
    const result = processPSD(currentPSD);
    set({
      builtGeometry: result.geometry,
      validationResult: result.validation,
      currentPSD: result.psd,
    });
  },

  validationResult: null,

  theme: 'dark',
  toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),

  dimensionMode: DimensionMode.EXTERNAL_OD,
  toggleDimensionMode: () =>
    set((s) => ({
      dimensionMode:
        s.dimensionMode === DimensionMode.EXTERNAL_OD
          ? DimensionMode.INTERNAL_ID
          : DimensionMode.EXTERNAL_OD,
    })),

  viewMode: '3D_VISUAL',
  setViewMode: (m) => set({ viewMode: m }),

  orders: [],
  currentOrder: null,
  addItemToOrder: (psd) => {
    const { currentOrder, orders } = get();
    const newItem = {
      psd,
      quantity: 1,
      addedAt: new Date().toISOString(),
    };

    if (currentOrder) {
      const updated = {
        ...currentOrder,
        items: [...currentOrder.items, newItem],
      };
      set({
        currentOrder: updated,
        orders: orders.map((o) => (o.orderId === updated.orderId ? updated : o)),
      });
    } else {
      const newOrder: Order = {
        orderId: generateOrderId(),
        timestamp: new Date().toISOString(),
        items: [newItem],
        status: 'DRAFT',
      };
      set({ currentOrder: newOrder, orders: [...orders, newOrder] });
    }
  },
  newOrder: () => {
    const newOrder: Order = {
      orderId: generateOrderId(),
      timestamp: new Date().toISOString(),
      items: [],
      status: 'DRAFT',
    };
    set({ currentOrder: newOrder, orders: [...get().orders, newOrder] });
  },

  language: 'en',
  toggleLanguage: () => set((s) => ({ language: s.language === 'en' ? 'es' : 'en' })),

  waterGauge: 26,
  setWaterGauge: (g) => set({ waterGauge: g }),

  panels: [
    { id: 'order', title: 'Order Panel', visible: true, docked: 'right', x: 0, y: 0 },
    { id: 'module', title: 'Module Panel', visible: true, docked: 'left', x: 0, y: 0 },
  ],
}));
