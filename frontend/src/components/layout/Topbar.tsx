/**
 * EcoSort AI - Top Navigation Bar (Redesign).
 * Modern, minimal top bar matching the reference image:
 * includes search input, Dark/Light pill toggle, notifications, and profile avatar.
 */

import React, { useEffect, useState } from 'react';
import {
  Moon,
  Sun,
  Menu,
  Search,
  Bell,
  User,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { fetchHealth } from '../../api/health';

interface TopbarProps {
  currentTheme: 'dark' | 'light';
  onToggleTheme: () => void;
  onToggleMobileMenu: () => void;
  activeTab: string;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentTheme,
  onToggleTheme,
  onToggleMobileMenu,
}) => {
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchHealth()
      .then((res) => setIsBackendHealthy(res.status === 'healthy'))
      .catch(() => setIsBackendHealthy(false));
  }, []);

  return (
    <header
      style={{
        height: '66px',
        borderBottom: '1px solid var(--border-default)',
        backgroundColor: 'var(--header-bg)',
        backdropFilter: 'blur(12px)',
        position: 'sticky',
        top: 0,
        zIndex: 40,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        transition: 'background-color var(--transition-normal), border-color var(--transition-normal)',
      }}
    >
      {/* Left: Mobile Menu & Search Input */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flex: 1, maxWidth: '420px' }}>
        <button
          onClick={onToggleMobileMenu}
          className="mobile-menu-btn"
          aria-label="Toggle navigation menu"
          style={{
            padding: '8px',
            borderRadius: 'var(--radius-sm)',
            color: 'var(--text-primary)',
            display: 'none',
            cursor: 'pointer',
          }}
        >
          <Menu size={22} />
        </button>

        {/* Global Search Pill */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            backgroundColor: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-full)',
            padding: '7px 16px',
            width: '100%',
            maxWidth: '320px',
            transition: 'border-color var(--transition-fast)',
          }}
          className="search-pill-container"
        >
          <Search size={16} color="var(--text-muted)" style={{ flexShrink: 0 }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search anything..."
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--text-primary)',
              fontSize: '0.8125rem',
              width: '100%',
            }}
          />
        </div>
      </div>

      {/* Right Controls: Health Badge, Dark/Light Toggle, Notifications, Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* API Health Pill */}
        <div
          title={isBackendHealthy ? 'EcoSort Core Engine Connected' : 'Checking Core Engine...'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 12px',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.75rem',
            fontWeight: 550,
            backgroundColor: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-secondary)',
          }}
        >
          {isBackendHealthy === true ? (
            <>
              <CheckCircle2 size={13} color="var(--brand-green)" />
              <span className="hide-on-mobile">API Online</span>
            </>
          ) : isBackendHealthy === false ? (
            <>
              <AlertCircle size={13} color="var(--status-danger)" />
              <span className="hide-on-mobile">API Offline</span>
            </>
          ) : (
            <span style={{ color: 'var(--text-muted)' }}>Connecting...</span>
          )}
        </div>

        {/* Dark/Light Pill Switcher */}
        <button
          onClick={onToggleTheme}
          aria-label={`Switch to ${currentTheme === 'dark' ? 'Light' : 'Dark'} mode`}
          title={`Switch to ${currentTheme === 'dark' ? 'Light' : 'Dark'} mode`}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '5px 8px 5px 12px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)',
            fontSize: '0.8125rem',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all var(--transition-fast)',
          }}
        >
          {currentTheme === 'dark' ? (
            <>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} className="hide-on-mobile">
                Dark
              </span>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--brand-green)',
                  color: '#ffffff',
                }}
              >
                <Moon size={13} />
              </span>
            </>
          ) : (
            <>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }} className="hide-on-mobile">
                Light
              </span>
              <span
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--brand-green)',
                  color: '#ffffff',
                }}
              >
                <Sun size={13} />
              </span>
            </>
          )}
        </button>

        {/* Notifications Icon Button */}
        <button
          aria-label="Notifications"
          title="Notifications"
          style={{
            position: 'relative',
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'var(--bg-surface-secondary)',
            border: '1px solid var(--border-default)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            transition: 'all var(--transition-fast)',
          }}
        >
          <Bell size={16} />
          {/* Notification Indicator Dot */}
          <span
            style={{
              position: 'absolute',
              top: '7px',
              right: '8px',
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: 'var(--brand-green)',
              boxShadow: '0 0 6px var(--brand-green)',
            }}
          />
        </button>

        {/* User Profile Avatar */}
        <button
          aria-label="User Profile"
          title="EcoSort Profile"
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: 'var(--brand-green-muted)',
            border: '1px solid var(--brand-green-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--brand-green)',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '0.8125rem',
            transition: 'all var(--transition-fast)',
          }}
        >
          <User size={17} />
        </button>
      </div>
    </header>
  );
};
