/**
 * EcoSort AI - Hero Section Vector Artwork.
 * Responsive, scalable SVG illustration featuring eco-friendly leaf,
 * recycling arrows motif, and organic circular ambient glows.
 */

import React from 'react';

export const HeroIllustration: React.FC<{ className?: string; style?: React.CSSProperties }> = ({
  className = '',
  style,
}) => {
  return (
    <div
      className={className}
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '240px',
        aspectRatio: '1 / 1',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        ...style,
      }}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 240 240"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: '100%', height: '100%', overflow: 'visible' }}
      >
        <defs>
          {/* Ambient Glow Gradient */}
          <radialGradient id="heroGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--brand-green)" stopOpacity="0.32" />
            <stop offset="60%" stopColor="var(--brand-green)" stopOpacity="0.12" />
            <stop offset="100%" stopColor="var(--brand-green)" stopOpacity="0" />
          </radialGradient>

          {/* Leaf Gradients */}
          <linearGradient id="primaryLeafGrad" x1="40" y1="20" x2="200" y2="220" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#34d399" />
            <stop offset="50%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#047857" />
          </linearGradient>

          <linearGradient id="secondaryLeafGrad" x1="160" y1="50" x2="60" y2="180" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#6ee7b7" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>

          <linearGradient id="stemGrad" x1="120" y1="50" x2="120" y2="200" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#a7f3d0" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#047857" stopOpacity="0.4" />
          </linearGradient>

          {/* Soft Shadow */}
          <filter id="leafShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="8" stdDeviation="12" floodColor="rgba(16, 185, 129, 0.28)" />
          </filter>
        </defs>

        {/* Ambient Backlight Aura */}
        <circle cx="120" cy="120" r="100" fill="url(#heroGlow)" />

        {/* Orbital Concentric Ring */}
        <circle
          cx="120"
          cy="120"
          r="86"
          stroke="var(--brand-green)"
          strokeOpacity="0.18"
          strokeWidth="1.5"
          strokeDasharray="4 6"
        />

        {/* Decorative Floating Dots */}
        <circle cx="56" cy="74" r="3.5" fill="var(--brand-green)" opacity="0.6" />
        <circle cx="188" cy="68" r="4.5" fill="#34d399" opacity="0.7" />
        <circle cx="196" cy="164" r="3" fill="var(--brand-green)" opacity="0.5" />
        <circle cx="48" cy="160" r="2.5" fill="#34d399" opacity="0.4" />

        {/* Outer Secondary Foliage / Echo Leaf */}
        <path
          d="M130 52 C170 65 195 110 185 152 C177 186 148 206 120 206 C100 206 75 195 62 172 C90 178 126 160 142 130 C154 107 148 76 130 52 Z"
          fill="url(#secondaryLeafGrad)"
          opacity="0.25"
        />

        {/* Main Hero Leaf Shape with Filter */}
        <g filter="url(#leafShadow)">
          <path
            d="M120 32 C168 48 198 94 186 146 C176 186 142 208 116 208 C90 208 56 186 46 146 C34 94 72 48 120 32 Z"
            fill="url(#primaryLeafGrad)"
          />

          {/* Central Stem & Leaf Veins */}
          <path
            d="M120 42 C120 90 120 150 116 198"
            stroke="url(#stemGrad)"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <path
            d="M120 86 C136 78 152 82 162 92"
            stroke="url(#stemGrad)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M120 114 C104 106 88 110 78 120"
            stroke="url(#stemGrad)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M120 138 C136 132 150 138 158 148"
            stroke="url(#stemGrad)"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M118 162 C106 156 94 160 86 168"
            stroke="url(#stemGrad)"
            strokeWidth="1.8"
            strokeLinecap="round"
          />

          {/* Universal Recycling Symbol Emblem Centered in Leaf */}
          <g transform="translate(100, 100) scale(0.85)">
            <circle cx="24" cy="24" r="22" fill="#0d281a" fillOpacity="0.45" />
            {/* 3 Recycling Mobius Arrows */}
            {/* Arrow 1: Top Right */}
            <path
              d="M24 10 L31 16 L25 16 C25 21 28 25 33 27 L31 30 C24 28 22 22 22 16 L17 16 Z"
              fill="#ffffff"
            />
            {/* Arrow 2: Bottom Right */}
            <path
              d="M36 28 L35 37 L30 33 C26 36 22 36 17 33 L15 36 C22 40 28 39 33 35 L31 40 Z"
              fill="#ffffff"
              opacity="0.95"
            />
            {/* Arrow 3: Left */}
            <path
              d="M12 28 L14 19 L18 23 C22 20 27 21 30 25 L32 22 C28 17 21 16 16 21 L17 16 Z"
              fill="#ffffff"
              opacity="0.9"
            />
          </g>
        </g>
      </svg>
    </div>
  );
};
