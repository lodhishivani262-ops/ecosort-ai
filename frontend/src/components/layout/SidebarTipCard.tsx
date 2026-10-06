/**
 * EcoSort AI - Sidebar Eco Tip Card.
 * Compact sustainability card placed at the bottom of the sidebar navigation.
 */

import React from 'react';
import { Sparkles, Leaf } from 'lucide-react';

export const SidebarTipCard: React.FC = () => {
  return (
    <div
      style={{
        margin: '0 12px 14px',
        padding: '12px 14px',
        borderRadius: 'var(--radius-md)',
        background: 'var(--sidebar-tip-bg)',
        border: '1px solid var(--border-default)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Decorative leaf watermark in the background */}
      <div
        style={{
          position: 'absolute',
          right: '-8px',
          bottom: '-10px',
          opacity: 0.12,
          color: 'var(--brand-green)',
          pointerEvents: 'none',
        }}
        aria-hidden="true"
      >
        <Leaf size={56} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '18px',
            height: '18px',
            borderRadius: '50%',
            backgroundColor: 'var(--brand-green-muted)',
            color: 'var(--brand-green)',
          }}
        >
          <Sparkles size={11} />
        </span>
        <span
          style={{
            fontSize: '0.6875rem',
            fontWeight: 700,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            color: 'var(--brand-green)',
          }}
        >
          Eco Tip
        </span>
      </div>

      <p
        style={{
          fontSize: '0.75rem',
          lineHeight: 1.45,
          color: 'var(--text-secondary)',
          margin: 0,
          fontWeight: 450,
          position: 'relative',
          zIndex: 1,
        }}
      >
        "Small actions create a cleaner, greener tomorrow."
      </p>
    </div>
  );
};
