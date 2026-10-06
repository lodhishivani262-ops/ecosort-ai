/**
 * EcoSort AI - Desktop & Mobile Navigation Sidebar (Redesign).
 * Matches the reference aesthetic with EcoSort green accents,
 * clean line icons, "+ New Scan" CTA, and eco-tip card at bottom.
 */

import React from 'react';
import {
  LayoutDashboard,
  Scan,
  History,
  BarChart3,
  Settings,
  Plus,
  Leaf,
  X,
} from 'lucide-react';
import type { NavigationTab, AnalyzeMode } from '../../types/navigation';
import { SidebarTipCard } from './SidebarTipCard';

interface SidebarProps {
  activeTab: NavigationTab;
  onSelectTab: (tab: NavigationTab, mode?: AnalyzeMode) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  isOpenMobile,
  onCloseMobile,
}) => {
  const navItems: { id: NavigationTab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={19} /> },
    { id: 'analyze', label: 'Analyze', icon: <Scan size={19} /> },
    { id: 'history', label: 'History', icon: <History size={19} /> },
    { id: 'insights', label: 'Insights', icon: <BarChart3 size={19} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={19} /> },
  ];

  const handleNavClick = (tab: NavigationTab) => {
    onSelectTab(tab);
    if (isOpenMobile) {
      onCloseMobile();
    }
  };

  const handleNewScan = () => {
    onSelectTab('analyze', 'camera');
    if (isOpenMobile) {
      onCloseMobile();
    }
  };

  return (
    <>
      {/* Mobile Drawer Backdrop */}
      {isOpenMobile && (
        <div
          onClick={onCloseMobile}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.65)',
            backdropFilter: 'blur(4px)',
            zIndex: 49,
          }}
          className="mobile-backdrop"
        />
      )}

      <aside
        className={`ecosort-sidebar ${isOpenMobile ? 'mobile-open' : ''}`}
        style={{
          width: '264px',
          height: '100vh',
          position: 'sticky',
          top: 0,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'var(--bg-surface)',
          borderRight: '1px solid var(--border-default)',
          zIndex: 50,
          transition: 'transform var(--transition-normal)',
          flexShrink: 0,
        }}
      >
        {/* Brand Header */}
        <div
          style={{
            padding: '22px 20px 18px',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            borderBottom: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '11px',
                backgroundColor: 'var(--brand-green)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                boxShadow: 'var(--shadow-accent)',
                flexShrink: 0,
              }}
            >
              <Leaf size={22} />
            </div>
            <div>
              <div
                style={{
                  fontWeight: 800,
                  fontSize: '1.125rem',
                  letterSpacing: '-0.025em',
                  color: 'var(--text-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <span>EcoSort</span>
                <span style={{ color: 'var(--brand-green)' }}>AI</span>
              </div>
              <div
                style={{
                  fontSize: '0.6875rem',
                  color: 'var(--text-muted)',
                  marginTop: '1px',
                  fontWeight: 450,
                  letterSpacing: '-0.01em',
                }}
              >
                Identify it. Sort it. Dispose responsibly.
              </div>
            </div>
          </div>

          {/* Mobile close button */}
          <button
            onClick={onCloseMobile}
            className="mobile-close-btn"
            style={{
              padding: '6px',
              color: 'var(--text-secondary)',
              display: 'none',
              borderRadius: 'var(--radius-sm)',
            }}
            aria-label="Close menu"
          >
            <X size={20} />
          </button>
        </div>

        {/* Primary Action Button: + New Scan */}
        <div style={{ padding: '16px 14px 10px' }}>
          <button
            onClick={handleNewScan}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              padding: '11px 16px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--brand-green)',
              color: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 650,
              boxShadow: '0 4px 14px var(--brand-green-glow)',
              transition: 'all var(--transition-fast)',
              border: 'none',
              cursor: 'pointer',
            }}
            className="ecosort-button"
          >
            <Plus size={18} strokeWidth={2.5} />
            <span>+ New Scan</span>
          </button>
        </div>

        {/* Nav Links */}
        <nav
          style={{
            flex: 1,
            padding: '8px 12px',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
            overflowY: 'auto',
          }}
        >
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.875rem',
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? 'var(--brand-green)' : 'var(--text-secondary)',
                  backgroundColor: isActive ? 'var(--brand-green-muted)' : 'transparent',
                  border: isActive ? '1px solid var(--brand-green-border)' : '1px solid transparent',
                  textAlign: 'left',
                  transition: 'all var(--transition-fast)',
                  cursor: 'pointer',
                }}
                className={`nav-link-btn ${isActive ? 'active' : ''}`}
              >
                <span
                  style={{
                    color: isActive ? 'var(--brand-green)' : 'inherit',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Bottom Eco Tip Card */}
        <SidebarTipCard />
      </aside>
    </>
  );
};
