/**
 * EcoSort AI - Analysis Result Card Component (Stage 6).
 * Renders structured AI perception alongside deterministic rule engine recommendations.
 */

import React from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  Info,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import type { ClassificationResultResponse } from '../../types/api';
import { CategoryBadge, ConfidenceBadge, ContaminationBadge } from '../common/Badge';
import { Card } from '../common/Card';
import { FeedbackWidget } from './FeedbackWidget';

interface ResultCardProps {
  result: ClassificationResultResponse;
  onReset?: () => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const { perception, recommendation, request_id } = result;
  const isSafetySensitive = perception.is_safety_sensitive || recommendation.category.includes('HAZARDOUS');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '800px', margin: '0 auto' }}>
      {/* Primary Result Banner */}
      <Card
        padding="lg"
        style={{
          borderLeft: isSafetySensitive
            ? '4px solid var(--status-danger)'
            : '4px solid var(--brand-green)',
        }}
      >
        {/* Header: Item & Category */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
            marginBottom: '16px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--brand-green)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Classification Result
              </span>
              {result.mock && (
                <span style={{ fontSize: '0.6875rem', padding: '1px 6px', borderRadius: '4px', backgroundColor: 'var(--bg-surface-secondary)', color: 'var(--text-muted)' }}>
                  Mock Mode
                </span>
              )}
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              {perception.item_name}
            </h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
            <CategoryBadge category={recommendation.category} size="lg" />
            <ConfidenceBadge confidence={recommendation.confidence} />
          </div>
        </div>

        {/* Physical Characteristics Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '12px',
            padding: '14px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface-secondary)',
            marginBottom: '20px',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Material
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {perception.material}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Condition
            </div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {perception.condition}
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Contamination
            </div>
            <ContaminationBadge level={perception.contamination} />
          </div>
        </div>

        {/* Safety Warning Banner if applicable */}
        {(recommendation.warnings.length > 0 || isSafetySensitive) && (
          <div
            style={{
              padding: '14px 18px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: isSafetySensitive
                ? 'rgba(239, 68, 68, 0.12)'
                : 'rgba(245, 158, 11, 0.12)',
              border: isSafetySensitive
                ? '1px solid rgba(239, 68, 68, 0.3)'
                : '1px solid rgba(245, 158, 11, 0.3)',
              marginBottom: '20px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              {isSafetySensitive ? (
                <ShieldAlert size={18} color="var(--status-danger)" />
              ) : (
                <AlertTriangle size={18} color="var(--status-warning)" />
              )}
              <span
                style={{
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: isSafetySensitive ? 'var(--status-danger)' : 'var(--status-warning)',
                }}
              >
                {isSafetySensitive ? 'Special Handling & Safety Warning' : 'Important Note'}
              </span>
            </div>
            <ul style={{ paddingLeft: '22px', fontSize: '0.8125rem', color: 'var(--text-primary)' }}>
              {recommendation.warnings.map((w, idx) => (
                <li key={idx} style={{ marginBottom: '4px' }}>
                  {w}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actionable Preparation Steps */}
        <div style={{ marginBottom: '20px' }}>
          <h4
            style={{
              fontSize: '0.9375rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <CheckCircle2 size={16} color="var(--brand-green)" />
            Recommended Preparation Steps
          </h4>

          {recommendation.preparation_steps.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {recommendation.preparation_steps.map((step, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface-secondary)',
                    border: '1px solid var(--border-subtle)',
                  }}
                >
                  <span
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      backgroundColor: 'var(--brand-green-muted)',
                      color: 'var(--brand-green)',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      marginTop: '1px',
                    }}
                  >
                    {idx + 1}
                  </span>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              No preparation required. Proceed directly with segregation.
            </p>
          )}
        </div>

        {/* Disposal Guidance Callout Box */}
        <div
          style={{
            padding: '14px 18px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--brand-green-muted)',
            border: '1px solid var(--brand-green-glow)',
            marginBottom: '20px',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              color: 'var(--brand-green)',
              letterSpacing: '0.04em',
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <ArrowRight size={14} />
            Disposal Guidance
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 500 }}>
            {recommendation.disposal_guidance}
          </p>
        </div>

        {/* Explainable Reasoning & Visual Clues */}
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: '16px',
            fontSize: '0.8125rem',
            color: 'var(--text-secondary)',
          }}
        >
          <div style={{ marginBottom: '6px' }}>
            <strong style={{ color: 'var(--text-primary)' }}>Rule Engine Reason: </strong>
            {recommendation.reason}
          </div>

          {recommendation.uncertainty_reason && (
            <div style={{ marginTop: '6px', color: 'var(--status-warning)' }}>
              <Info size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
              <strong>Uncertainty Note: </strong>
              {recommendation.uncertainty_reason}
            </div>
          )}

          {perception.visual_clues.length > 0 && (
            <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
              <span style={{ color: 'var(--text-muted)' }}>Visual Clues:</span>
              {perception.visual_clues.map((clue, idx) => (
                <span
                  key={idx}
                  style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-surface-secondary)',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {clue}
                </span>
              ))}
            </div>
          )}
        </div>
      </Card>

      {/* User Feedback Widget */}
      <FeedbackWidget requestId={request_id} />

      {/* Disclaimers & Tracing */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          padding: '0 4px',
        }}
      >
        <span>
          Municipal rules & bin color standards vary by locality. Follow your local city guidelines.
        </span>
        <span style={{ fontFamily: 'var(--font-mono)' }}>ID: {request_id.substring(0, 8)}...</span>
      </div>
    </div>
  );
};
