/**
 * EcoSort AI - Dashboard Overview Page (Redesign).
 * Matches visual reference:
 * - Row 1: Hero Card (with eco artwork + "+ Analyze Waste →") + "Make a difference" Card (4 mini educational cards).
 * - Row 2: Quick Actions (3 interactive cards), Recent Scans (with View All →), and Waste Categories (6 categories with real counts).
 */

import React, { useEffect, useState } from 'react';
import {
  ArrowRight,
  Camera,
  UploadCloud,
  Edit3,
  Recycle,
  Droplets,
  Wind,
  Sprout,
  Package,
  FileText,
  Wine,
  Shield,
  Apple,
  Cpu,
  History as HistoryIcon,
  Sparkles,
  ChevronRight,
} from 'lucide-react';
import { fetchAggregatedMetrics } from '../api/metrics';
import { fetchSessionHistory } from '../api/history';
import type { ClassificationHistoryItem, MetricsResponse } from '../types/api';
import type { NavigationTab, AnalyzeMode } from '../types/navigation';
import { CategoryBadge } from '../components/common/Badge';
import { HeroIllustration } from '../components/layout/HeroIllustration';
import { formatRelativeTime } from '../utils/formatters';

interface DashboardPageProps {
  onNavigate: (tab: NavigationTab, mode?: AnalyzeMode) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [recentItems, setRecentItems] = useState<ClassificationHistoryItem[]>([]);

  useEffect(() => {
    Promise.allSettled([fetchAggregatedMetrics(), fetchSessionHistory(5, 0)])
      .then(([metricsRes, historyRes]) => {
        if (metricsRes.status === 'fulfilled') {
          setMetrics(metricsRes.value);
        }
        if (historyRes.status === 'fulfilled') {
          setRecentItems(historyRes.value.items || []);
        }
      });
  }, []);

  // Compute honest category counts from real backend metrics data
  const getCategoryCount = (keywords: string[]): number => {
    if (!metrics || !Array.isArray(metrics.categories)) return 0;
    return metrics.categories
      .filter((cat) =>
        keywords.some((kw) => cat.category.toUpperCase().includes(kw.toUpperCase()))
      )
      .reduce((sum, item) => sum + (item.count || 0), 0);
  };

  const wasteCategories = [
    {
      name: 'Plastic',
      keywords: ['PLASTIC'],
      icon: <Package size={17} />,
      color: '#3b82f6',
      bgMuted: 'rgba(59, 130, 246, 0.12)',
    },
    {
      name: 'Paper',
      keywords: ['PAPER', 'CARDBOARD'],
      icon: <FileText size={17} />,
      color: '#f59e0b',
      bgMuted: 'rgba(245, 158, 11, 0.12)',
    },
    {
      name: 'Glass',
      keywords: ['GLASS'],
      icon: <Wine size={17} />,
      color: '#10b981',
      bgMuted: 'rgba(16, 185, 129, 0.12)',
    },
    {
      name: 'Metal',
      keywords: ['METAL', 'ALUMINUM'],
      icon: <Shield size={17} />,
      color: '#94a3b8',
      bgMuted: 'rgba(148, 163, 184, 0.14)',
    },
    {
      name: 'Organic',
      keywords: ['ORGANIC', 'WET_WASTE', 'FOOD'],
      icon: <Apple size={17} />,
      color: '#ea580c',
      bgMuted: 'rgba(234, 88, 12, 0.12)',
    },
    {
      name: 'E-Waste',
      keywords: ['E_WASTE', 'ELECTRONIC'],
      icon: <Cpu size={17} />,
      color: '#8b5cf6',
      bgMuted: 'rgba(139, 92, 246, 0.12)',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* =========================================================================
       * ROW 1: Hero Welcome Section + "Make a difference" Section
       * ========================================================================= */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '20px',
          alignItems: 'stretch',
        }}
      >
        {/* HERO CARD */}
        <div
          style={{
            gridColumn: 'span 1',
            flex: 1.4,
            background: 'var(--hero-gradient)',
            border: '1px solid var(--hero-border)',
            borderRadius: 'var(--radius-xl)',
            padding: '30px 32px',
            position: 'relative',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '24px',
            boxShadow: 'var(--shadow-md)',
          }}
          className="dashboard-hero-card"
        >
          {/* Hero Left Content */}
          <div style={{ flex: 1, minWidth: '260px', zIndex: 2 }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.8125rem',
                fontWeight: 650,
                color: 'var(--brand-green)',
                letterSpacing: '0.04em',
                marginBottom: '6px',
                textTransform: 'uppercase',
              }}
            >
              <span>Welcome to</span>
            </div>

            <h1
              style={{
                fontSize: '2.25rem',
                fontWeight: 800,
                letterSpacing: '-0.03em',
                color: 'var(--text-primary)',
                lineHeight: 1.15,
                margin: '0 0 8px',
              }}
            >
              EcoSort <span style={{ color: 'var(--brand-green)' }}>AI</span>
            </h1>

            <div
              style={{
                fontSize: '1rem',
                fontWeight: 650,
                color: 'var(--text-primary)',
                marginBottom: '10px',
              }}
            >
              Identify it. Sort it. Dispose responsibly.
            </div>

            <p
              style={{
                fontSize: '0.875rem',
                lineHeight: 1.55,
                color: 'var(--text-secondary)',
                marginBottom: '22px',
                maxWidth: '460px',
              }}
            >
              Turn your waste into a cleaner, greener future. Use the AI-powered waste analyzer to get instant classification and responsible disposal guidance.
            </p>

            <button
              onClick={() => onNavigate('analyze', 'camera')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 22px',
                borderRadius: 'var(--radius-full)',
                backgroundColor: 'var(--brand-green)',
                color: '#ffffff',
                fontSize: '0.9375rem',
                fontWeight: 650,
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 16px var(--brand-green-glow)',
                transition: 'all var(--transition-fast)',
              }}
              className="ecosort-button"
            >
              <span>+ Analyze Waste</span>
              <ArrowRight size={17} />
            </button>
          </div>

          {/* Hero Right Visual Graphic */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1,
            }}
            className="hide-on-narrow"
          >
            <HeroIllustration />
          </div>
        </div>

        {/* MAKE A DIFFERENCE CARD */}
        <div
          style={{
            flex: 1,
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-xl)',
            padding: '28px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <div
                style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '7px',
                  backgroundColor: 'var(--brand-green-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--brand-green)',
                }}
              >
                <Sparkles size={15} />
              </div>
              <h2
                style={{
                  fontSize: '1.1875rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  letterSpacing: '-0.02em',
                  margin: 0,
                }}
              >
                Make a difference
              </h2>
            </div>
            <p
              style={{
                fontSize: '0.8125rem',
                color: 'var(--text-secondary)',
                marginTop: '4px',
                marginBottom: '20px',
                lineHeight: 1.45,
              }}
            >
              Every piece of waste, when sorted correctly, helps our planet.
            </p>
          </div>

          {/* 4 Mini Difference Cards (2x2 Grid) */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '12px',
            }}
          >
            {/* 1. Reduce Waste */}
            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(16, 185, 129, 0.14)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#10b981',
                }}
              >
                <Recycle size={17} />
              </div>
              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                  Reduce Waste
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Minimize household landfill
                </div>
              </div>
            </div>

            {/* 2. Save Resources */}
            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(59, 130, 246, 0.14)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#3b82f6',
                }}
              >
                <Droplets size={17} />
              </div>
              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                  Save Resources
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Preserve raw materials
                </div>
              </div>
            </div>

            {/* 3. Lower Pollution */}
            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(20, 184, 166, 0.14)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#14b8a6',
                }}
              >
                <Wind size={17} />
              </div>
              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                  Lower Pollution
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Prevent toxic leakage
                </div>
              </div>
            </div>

            {/* 4. Build a Greener Future */}
            <div
              style={{
                padding: '14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: 'rgba(34, 197, 94, 0.14)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#22c55e',
                }}
              >
                <Sprout size={17} />
              </div>
              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                  Greener Future
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Support UN SDG 12
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* =========================================================================
       * ROW 2: Quick Actions, Recent Scans, Waste Categories
       * ========================================================================= */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '20px',
        }}
      >
        {/* 1. QUICK ACTIONS CARD */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-xl)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ marginBottom: '18px' }}>
            <h3
              style={{
                fontSize: '1.0625rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                letterSpacing: '-0.015em',
                margin: 0,
              }}
            >
              Quick Actions
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
              Choose your preferred input method
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
            {/* Take a Photo Action */}
            <div
              onClick={() => onNavigate('analyze', 'camera')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'var(--brand-green-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--brand-green)',
                    flexShrink: 0,
                  }}
                >
                  <Camera size={19} />
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                    Take a Photo
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Use your camera to capture waste
                  </div>
                </div>
              </div>
              <ChevronRight size={17} color="var(--text-muted)" />
            </div>

            {/* Upload Image Action */}
            <div
              onClick={() => onNavigate('analyze', 'upload')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#3b82f6',
                    flexShrink: 0,
                  }}
                >
                  <UploadCloud size={19} />
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                    Upload Image
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Select an image from your device
                  </div>
                </div>
              </div>
              <ChevronRight size={17} color="var(--text-muted)" />
            </div>

            {/* Describe Item Action */}
            <div
              onClick={() => onNavigate('analyze', 'text')}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer',
                transition: 'all var(--transition-fast)',
              }}
              className="hoverable-card"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '10px',
                    backgroundColor: 'rgba(168, 85, 247, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#a855f7',
                    flexShrink: 0,
                  }}
                >
                  <Edit3 size={19} />
                </div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                    Describe Item
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Type what you want to analyze
                  </div>
                </div>
              </div>
              <ChevronRight size={17} color="var(--text-muted)" />
            </div>
          </div>
        </div>

        {/* 2. RECENT SCANS CARD */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-xl)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '18px',
            }}
          >
            <div>
              <h3
                style={{
                  fontSize: '1.0625rem',
                  fontWeight: 700,
                  color: 'var(--text-primary)',
                  letterSpacing: '-0.015em',
                  margin: 0,
                }}
              >
                Recent Scans
              </h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                Your analyzed domestic items
              </p>
            </div>
            <button
              onClick={() => onNavigate('history')}
              style={{
                fontSize: '0.8125rem',
                color: 'var(--brand-green)',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                border: 'none',
                background: 'transparent',
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: 'var(--radius-sm)',
              }}
            >
              <span>View All</span>
              <ArrowRight size={14} />
            </button>
          </div>

          {recentItems.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
              {recentItems.slice(0, 4).map((item) => (
                <div
                  key={item.request_id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface-secondary)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <div style={{ minWidth: 0, paddingRight: '8px' }}>
                    <div
                      style={{
                        fontSize: '0.875rem',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {item.item_name}
                    </div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {formatRelativeTime(item.created_at)} • {item.material}
                    </div>
                  </div>
                  <CategoryBadge category={item.category} size="sm" />
                </div>
              ))}
            </div>
          ) : (
            <div
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '24px 16px',
                textAlign: 'center',
                backgroundColor: 'var(--bg-surface-secondary)',
                borderRadius: 'var(--radius-md)',
                border: '1px dashed var(--border-default)',
              }}
            >
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--brand-green-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--brand-green)',
                  marginBottom: '10px',
                }}
              >
                <HistoryIcon size={20} />
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 650, color: 'var(--text-primary)' }}>
                No recent activity yet.
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px', maxWidth: '220px' }}>
                Your scans will appear here after your first analysis.
              </div>
            </div>
          )}
        </div>

        {/* 3. WASTE CATEGORIES CARD */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-xl)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ marginBottom: '18px' }}>
            <h3
              style={{
                fontSize: '1.0625rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                letterSpacing: '-0.015em',
                margin: 0,
              }}
            >
              Waste Categories
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
              Standard segregation streams
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '10px',
              flex: 1,
            }}
          >
            {wasteCategories.map((cat) => {
              const count = getCategoryCount(cat.keywords);
              return (
                <div
                  key={cat.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface-secondary)',
                    border: '1px solid var(--border-subtle)',
                    transition: 'all var(--transition-fast)',
                  }}
                  className="hoverable-card"
                >
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '8px',
                      backgroundColor: cat.bgMuted,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: cat.color,
                      flexShrink: 0,
                    }}
                  >
                    {cat.icon}
                  </div>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div
                      style={{
                        fontSize: '0.8125rem',
                        fontWeight: 650,
                        color: 'var(--text-primary)',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {cat.name}
                    </div>
                    <div
                      style={{
                        fontSize: '0.6875rem',
                        color: 'var(--text-muted)',
                        marginTop: '1px',
                        fontWeight: 500,
                      }}
                    >
                      {count} {count === 1 ? 'item' : 'items'}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
