import React from 'react';
import { useHVACStore } from '../../store';
import { useTranslation } from '../../i18n/useTranslation';
import { DockablePanel } from './DockablePanel';
import { processPSD } from '../../engine';

export const OrderPanel: React.FC = () => {
  const { currentOrder, orders, newOrder, builtGeometry, currentPSD, addItemToOrder } = useHVACStore();
  const t = useTranslation();

  const handleAddToOrder = () => {
    if (currentPSD && builtGeometry) {
      const result = processPSD(currentPSD);
      if (result.validation.valid) {
        addItemToOrder(result.psd);
      }
    }
  };

  return (
    <DockablePanel title={t.orderPanelTitle} defaultDocked="right" className="w-64">
      <div className="p-3 space-y-3">
        <div className="bg-gray-800 rounded p-2">
          <div className="text-xs text-gray-400 mb-1">{t.currentOrder}</div>
          {currentOrder ? (
            <>
              <div className="text-blue-400 font-mono font-bold text-sm">{currentOrder.orderId}</div>
              <div className="text-xs text-gray-500">{new Date(currentOrder.timestamp).toLocaleDateString()}</div>
              <div className="text-xs text-gray-400 mt-1">
                {currentOrder.items.length} {t.itemsHeader.toLowerCase()}
              </div>
            </>
          ) : (
            <div className="text-xs text-gray-500">{t.noActiveOrder}</div>
          )}
        </div>

        <button
          onClick={handleAddToOrder}
          disabled={!builtGeometry}
          className="w-full px-3 py-2 text-xs font-semibold bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded transition-all"
        >
          {t.addToOrder}
        </button>

        <button
          onClick={newOrder}
          className="w-full px-3 py-2 text-xs font-semibold bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-all"
        >
          {t.newOrder}
        </button>

        {currentOrder && currentOrder.items.length > 0 && (
          <div className="space-y-1">
            <div className="text-xs font-semibold text-gray-400 uppercase">{t.itemsHeader}</div>
            {currentOrder.items.map((item, i) => (
              <div key={i} className="bg-gray-800 rounded p-2 text-xs">
                <div className="text-white font-medium">{item.psd.fittingType.replace(/_/g, ' ')}</div>
                <div className="text-gray-400">
                  {item.psd.shapeType} | {item.psd.inletWidth ?? item.psd.inletDiameter}"
                  {' '}× {item.psd.length}"
                </div>
                <div className="text-gray-500">{t.gaugeShort} {item.psd.wallGauge}</div>
              </div>
            ))}
          </div>
        )}

        {orders.length > 0 && (
          <div className="space-y-1">
            <div className="text-xs font-semibold text-gray-400 uppercase">{t.allOrders}</div>
            {orders.map((order) => (
              <div key={order.orderId} className="flex items-center justify-between text-xs text-gray-400 py-1 border-b border-gray-800">
                <span className="text-blue-400 font-mono">{order.orderId}</span>
                <span>{order.items.length} {t.itemsHeader.toLowerCase()}</span>
                <span className="text-green-500">{order.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </DockablePanel>
  );
};
