/**
 * EcoSort AI - UI Formatters and Category Styling Helpers (Stage 6).
 */

import type { ConfidenceLevel, ContaminationLevel } from '../types/api';

export interface CategoryStyle {
  label: string;
  bgLight: string;
  bgDark: string;
  textLight: string;
  textDark: string;
  borderLight: string;
  borderDark: string;
  iconName: string;
}

export function getCategoryStyle(category: string): CategoryStyle {
  const norm = category.toUpperCase();

  if (norm.includes('RECYCLABLE')) {
    return {
      label: 'Recyclable',
      bgLight: '#ecfdf5',
      bgDark: 'rgba(16, 185, 129, 0.15)',
      textLight: '#047857',
      textDark: '#34d399',
      borderLight: '#a7f3d0',
      borderDark: 'rgba(16, 185, 129, 0.3)',
      iconName: 'RefreshCw',
    };
  }
  if (norm.includes('ORGANIC') || norm.includes('WET')) {
    return {
      label: 'Organic / Wet',
      bgLight: '#fef3c7',
      bgDark: 'rgba(245, 158, 11, 0.15)',
      textLight: '#b45309',
      textDark: '#fbbf24',
      borderLight: '#fde68a',
      borderDark: 'rgba(245, 158, 11, 0.3)',
      iconName: 'Leaf',
    };
  }
  if (norm.includes('HAZARDOUS')) {
    return {
      label: 'Hazardous / Special',
      bgLight: '#fef2f2',
      bgDark: 'rgba(239, 68, 68, 0.15)',
      textLight: '#b91c1c',
      textDark: '#f87171',
      borderLight: '#fecaca',
      borderDark: 'rgba(239, 68, 68, 0.3)',
      iconName: 'AlertTriangle',
    };
  }
  if (norm.includes('E-WASTE')) {
    return {
      label: 'E-Waste',
      bgLight: '#eff6ff',
      bgDark: 'rgba(59, 130, 246, 0.15)',
      textLight: '#1d4ed8',
      textDark: '#60a5fa',
      borderLight: '#bfdbfe',
      borderDark: 'rgba(59, 130, 246, 0.3)',
      iconName: 'Cpu',
    };
  }
  if (norm.includes('GLASS')) {
    return {
      label: 'Glass',
      bgLight: '#f5f3ff',
      bgDark: 'rgba(139, 92, 246, 0.15)',
      textLight: '#6d28d9',
      textDark: '#a78bfa',
      borderLight: '#ddd6fe',
      borderDark: 'rgba(139, 92, 246, 0.3)',
      iconName: 'Layers',
    };
  }
  if (norm.includes('SANITARY')) {
    return {
      label: 'Sanitary Waste',
      bgLight: '#fdf2f8',
      bgDark: 'rgba(236, 72, 153, 0.15)',
      textLight: '#be185d',
      textDark: '#f472b6',
      borderLight: '#fbcfe8',
      borderDark: 'rgba(236, 72, 153, 0.3)',
      iconName: 'Shield',
    };
  }
  if (norm.includes('DRY')) {
    return {
      label: 'Dry Waste',
      bgLight: '#f1f5f9',
      bgDark: 'rgba(148, 163, 184, 0.15)',
      textLight: '#334155',
      textDark: '#cbd5e1',
      borderLight: '#cbd5e1',
      borderDark: 'rgba(148, 163, 184, 0.3)',
      iconName: 'Box',
    };
  }
  return {
    label: 'Unclassified',
    bgLight: '#f8fafc',
    bgDark: 'rgba(100, 116, 139, 0.15)',
    textLight: '#475569',
    textDark: '#94a3b8',
    borderLight: '#e2e8f0',
    borderDark: 'rgba(100, 116, 139, 0.3)',
    iconName: 'HelpCircle',
  };
}

export function formatRelativeTime(dateInput: string | Date): string {
  const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;
  const now = new Date();
  const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (isNaN(diffSeconds) || diffSeconds < 0) return 'Just now';
  if (diffSeconds < 60) return 'Just now';
  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

export function getConfidenceBadgeClass(confidence: ConfidenceLevel): string {
  switch (confidence) {
    case 'HIGH':
      return 'badge-confidence-high';
    case 'MEDIUM':
      return 'badge-confidence-medium';
    case 'LOW':
      return 'badge-confidence-low';
    default:
      return '';
  }
}

export function getContaminationBadgeClass(level: ContaminationLevel): string {
  switch (level) {
    case 'NONE':
      return 'badge-contam-none';
    case 'LOW':
      return 'badge-contam-low';
    case 'MEDIUM':
      return 'badge-contam-medium';
    case 'HIGH':
      return 'badge-contam-high';
    default:
      return 'badge-contam-unknown';
  }
}
