/**
 * EcoSort AI - Settings & Privacy Information Page (Stage 6).
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Shield,
  Moon,
  Sun,
  Copy,
  Check,
  RefreshCw,
  Server,
} from 'lucide-react';
import { fetchHealth } from '../api/health';
import { getOrCreateSessionId, resetSessionId } from '../utils/session';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';

interface SettingsPageProps {
  currentTheme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ currentTheme, onToggleTheme }) => {
  const [sessionId, setSessionId] = useState<string>(() => getOrCreateSessionId());
  const [copied, setCopied] = useState<boolean>(false);
  const [healthStatus, setHealthStatus] = useState<string>('Testing...');
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  const testBackendConnection = useCallback(() => {
    setHealthStatus('Probing...');
    const start = performance.now();
    fetchHealth()
      .then((res) => {
        const elapsed = Math.round(performance.now() - start);
        setLatencyMs(elapsed);
        setHealthStatus(res.status === 'healthy' ? 'Connected & Healthy' : 'Degraded');
      })
      .catch(() => {
        setHealthStatus('Offline / Unreachable');
        setLatencyMs(null);
      });
  }, []);

  useEffect(() => {
    testBackendConnection();
  }, [testBackendConnection]);

  const handleCopySession = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleResetSession = () => {
    if (window.confirm('Reset anonymous session token? This detaches past scan history.')) {
      const newId = resetSessionId();
      setSessionId(newId);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          Settings & Privacy
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
          Manage your anonymous session token, theme preferences, and review system policies.
        </p>
      </div>

      {/* Theme Preference Card */}
      <Card padding="md">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Appearance Mode
        </h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          EcoSort Green remains the permanent brand accent in both modes. Choose your display preference.
        </p>

        <div style={{ display: 'flex', gap: '12px' }}>
          <Button
            variant={currentTheme === 'dark' ? 'primary' : 'outline'}
            size="md"
            icon={<Moon size={16} />}
            onClick={() => currentTheme !== 'dark' && onToggleTheme()}
          >
            Dark Mode (Default)
          </Button>
          <Button
            variant={currentTheme === 'light' ? 'primary' : 'outline'}
            size="md"
            icon={<Sun size={16} />}
            onClick={() => currentTheme !== 'light' && onToggleTheme()}
          >
            Light Mode
          </Button>
        </div>
      </Card>

      {/* Anonymous Session Token Card */}
      <Card padding="md">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Anonymous Session Token
        </h3>
        <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
          To protect user privacy, EcoSort AI does not require accounts or personal information. Your recent scans
          are keyed to this randomized, non-identifying token in your browser.
        </p>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface-secondary)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8125rem',
            color: 'var(--text-primary)',
            marginBottom: '14px',
            border: '1px solid var(--border-default)',
            overflowX: 'auto',
          }}
        >
          <span style={{ flex: 1 }}>{sessionId}</span>
          <Button variant="ghost" size="sm" icon={copied ? <Check size={14} color="var(--brand-green)" /> : <Copy size={14} />} onClick={handleCopySession}>
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
          <Button variant="danger" size="sm" icon={<RefreshCw size={14} />} onClick={handleResetSession}>
            Generate New Token
          </Button>
        </div>
      </Card>

      {/* Backend Connection Diagnostic Card */}
      <Card padding="md">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Backend API Health Probe
          </h3>
          <Button variant="outline" size="sm" icon={<RefreshCw size={13} />} onClick={testBackendConnection}>
            Re-test
          </Button>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface-secondary)',
            marginTop: '8px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Server size={18} color="var(--brand-green)" />
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {healthStatus}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                FastAPI Gateway • /health
              </div>
            </div>
          </div>

          {latencyMs !== null && (
            <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--brand-green)' }}>
              {latencyMs} ms
            </span>
          )}
        </div>
      </Card>

      {/* Privacy Policy & Architectural Guarantees Card */}
      <Card padding="md" style={{ borderLeft: '4px solid var(--brand-green)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <Shield size={18} color="var(--brand-green)" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Privacy & Architectural Guarantees
          </h3>
        </div>

        <ul style={{ paddingLeft: '20px', fontSize: '0.8125rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <li>
            <strong style={{ color: 'var(--text-primary)' }}>Strict Zero Image Storage: </strong>
            Uploaded photos are processed exclusively in volatile memory for AI perception and immediately garbage-collected. No database table or cloud bucket stores user images.
          </li>
          <li>
            <strong style={{ color: 'var(--text-primary)' }}>Deterministic Decision Engine: </strong>
            AI is used solely for visual perception. All bin assignments, preparation steps, and safety warnings are formulated by deterministic rules.
          </li>
          <li>
            <strong style={{ color: 'var(--text-primary)' }}>General Municipal Guidance: </strong>
            Disposal rules follow international material recycling standards (UN SDG 12). City-specific bin colors and local schedules vary.
          </li>
        </ul>
      </Card>
    </div>
  );
};
