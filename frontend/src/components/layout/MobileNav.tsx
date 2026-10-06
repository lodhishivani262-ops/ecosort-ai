/**
 * EcoSort AI - Responsive Mobile Bottom Navigation Bar (Stage 6).
 */

import React from 'react';
import { LayoutDashboard, Scan, History, BarChart3, Settings } from 'lucide-react';
import type { NavigationTab } from '../../types/navigation';

interface MobileNavProps {
  activeTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ activeTab, onSelectTab }) => {
  const items: { id: NavigationTab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Overview', icon: <LayoutDashboard size={20} /> },
    { id: 'analyze', label: 'Analyze', icon: <Scan size={20} /> },
    { id: 'history', label: 'History', icon: <History size={20} /> },
    { id: 'insights', label: 'Insights', icon: <BarChart3 size={20} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={20} /> },
  ];

  return (
    <nav
      className="mobile-bottom-nav"
      style={{
        display: 'none',
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: '60px',
        backgroundColor: 'var(--header-bg)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid var(--border-default)',
        zIndex: 40,
        justifyContent: 'space-around',
        alignItems: 'center',
        padding: '0 8px',
      }}
    >
      {items.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '3px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              color: isActive ? 'var(--brand-green)' : 'var(--text-secondary)',
              fontSize: '0.6875rem',
              fontWeight: isActive ? 600 : 500,
              flex: 1,
            }}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
};
