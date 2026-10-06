/**
 * EcoSort AI - Reusable Card Component (Stage 6).
 */

import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'surface' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  isHoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'md',
  isHoverable = false,
  className = '',
  style,
  ...props
}) => {
  const getPaddingStyle = () => {
    switch (padding) {
      case 'none':
        return 0;
      case 'sm':
        return '14px';
      case 'lg':
        return '28px';
      default:
        return '20px';
    }
  };

  const getBackgroundStyle = () => {
    switch (variant) {
      case 'surface':
        return 'var(--bg-surface-secondary)';
      case 'glass':
        return 'var(--bg-surface)';
      default:
        return 'var(--bg-surface)';
    }
  };

  return (
    <div
      style={{
        backgroundColor: getBackgroundStyle(),
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-default)',
        padding: getPaddingStyle(),
        boxShadow: 'var(--shadow-sm)',
        transition: 'border-color var(--transition-fast), transform var(--transition-fast), box-shadow var(--transition-fast)',
        ...style,
      }}
      className={`ecosort-card ${isHoverable ? 'hoverable-card' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
