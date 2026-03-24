import React from 'react';
import { useHVACStore } from './store';
import { useTranslation } from './i18n/useTranslation';
import { GlobalToolbar } from './components/toolbar/GlobalToolbar';
import { Viewport3D } from './components/Viewport3D';
import { OrderPanel } from './components/panels/OrderPanel';
import { AIGenerator } from './modules/ai/AIGenerator';
import { ParametricBuilder } from './modules/parametric/ParametricBuilder';
import { WizardFittings } from './modules/wizard/WizardFittings';
import clsx from 'clsx';

export default function App() {
  const { activeModule, setActiveModule, theme } = useHVACStore();
  const t = useTranslation();

  return (
    <div className={clsx('flex flex-col h-screen w-screen overflow-hidden', theme === 'dark' ? 'dark bg-gray-950 text-white' : 'bg-gray-100 text-gray-900')}>
      <GlobalToolbar />
      
      <div className="flex flex-1 overflow-hidden">
        <div className="w-72 flex-shrink-0 flex flex-col border-r border-gray-700 bg-gray-900 overflow-hidden">
          <div className="flex border-b border-gray-700">
            {(['ai', 'parametric', 'wizard'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setActiveModule(m)}
                className={clsx(
                  'flex-1 py-2 text-xs font-semibold uppercase tracking-wide transition-all',
                  activeModule === m
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                )}
              >
                {m === 'ai' ? t.tabAI : m === 'parametric' ? t.tabParametric : t.tabWizard}
              </button>
            ))}
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {activeModule === 'ai' && <AIGenerator />}
            {activeModule === 'parametric' && <ParametricBuilder />}
            {activeModule === 'wizard' && <WizardFittings />}
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <Viewport3D />
        </div>

        <div className="w-64 flex-shrink-0">
          <OrderPanel />
        </div>
      </div>
    </div>
  );
}
