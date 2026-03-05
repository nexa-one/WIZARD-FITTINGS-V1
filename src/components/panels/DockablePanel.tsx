import React, { useState } from 'react';
import clsx from 'clsx';

interface DockablePanelProps {
  title: string;
  children: React.ReactNode;
  defaultDocked?: 'left' | 'right';
  className?: string;
  onClose?: () => void;
}

export const DockablePanel: React.FC<DockablePanelProps> = ({
  title,
  children,
  defaultDocked = 'left',
  className,
  onClose,
}) => {
  const [isPinned] = useState(true);
  const [docked] = useState(defaultDocked);

  return (
    <div
      className={clsx(
        'flex flex-col bg-gray-900 border-gray-700 h-full',
        docked === 'left' ? 'border-r' : 'border-l',
        className
      )}
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700 bg-gray-800">
        <span className="text-xs font-semibold text-gray-300 uppercase tracking-wide">{title}</span>
        <div className="flex items-center gap-1">
          <button className="text-gray-500 hover:text-gray-300 text-xs px-1">
            {isPinned ? '📌' : '📍'}
          </button>
          {onClose && (
            <button onClick={onClose} className="text-gray-500 hover:text-red-400 text-xs px-1">
              ✕
            </button>
          )}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        {children}
      </div>
    </div>
  );
};
