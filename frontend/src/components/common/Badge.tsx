/**
 * EcoSort AI - Reusable Badge Component (Stage 6).
 */

import React from 'react';
import type { ConfidenceLevel, ContaminationLevel } from '../../types/api';
import { getCategoryStyle } from '../../utils/formatters';

interface CategoryBadgeProps {
  category: string;
  size?: 'sm' | 'md' | 'lg';
}

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category, size = 'md' }) => {
  const style = getCategoryStyle(category);

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-semibold rounded-full uppercase tracking-wider ${
        size === 'sm' ? 'px-2.5 py-0.5 text-xs' : size === 'lg' ? 'px-4 py-1.5 text-sm' : 'px-3 py-1 text-xs'
      }`}
      style={{
        backgroundColor: 'var(--cat-bg, ' + style.bgDark + ')',
        color: 'var(--cat-text, ' + style.textDark + ')',
        border: '1px solid var(--cat-border, ' + style.borderDark + ')',
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: 'currentColor',
          display: 'inline-block',
        }}
      />
      {category}
    </span>
  );
};

interface ConfidenceBadgeProps {
  confidence: ConfidenceLevel;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  let color = '#10b981';
  let label = 'High Confidence';

  if (confidence === 'MEDIUM') {
    color = '#f59e0b';
    label = 'Medium Confidence';
  } else if (confidence === 'LOW') {
    color = '#ef4444';
    label = 'Low Confidence';
  }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        fontSize: '0.8125rem',
        fontWeight: 500,
        color: 'var(--text-secondary)',
      }}
    >
      <span
        style={{
          display: 'inline-block',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: color,
        }}
      />
      {label} ({confidence})
    </span>
  );
};

interface ContaminationBadgeProps {
  level: ContaminationLevel;
}

export const ContaminationBadge: React.FC<ContaminationBadgeProps> = ({ level }) => {
  let color = 'var(--text-secondary)';
  let bg = 'var(--badge-bg)';

  if (level === 'HIGH') {
    color = 'var(--status-danger)';
    bg = 'rgba(239, 68, 68, 0.12)';
  } else if (level === 'MEDIUM') {
    color = 'var(--status-warning)';
    bg = 'rgba(245, 158, 11, 0.12)';
  } else if (level === 'NONE' || level === 'LOW') {
    color = 'var(--status-success)';
    bg = 'rgba(16, 185, 129, 0.12)';
  }

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '3px 8px',
        borderRadius: '6px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: bg,
        color: color,
      }}
    >
      Contamination: {level}
    </span>
  );
};
