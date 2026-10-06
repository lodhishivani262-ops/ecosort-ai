/**
 * EcoSort AI - Aggregated Insights & Metrics Page (Stage 6).
 */

import React, { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';
import { fetchAggregatedMetrics } from '../api/metrics';
import type { MetricsResponse } from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export const InsightsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMetrics = () => {
    setIsLoading(true);
    setError(null);
    fetchAggregatedMetrics()
      .then((res) => setMetrics(res))
      .catch((err) => setError(err.message || 'Unable to fetch metrics from backend.'))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header and Refresh */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Analytics & System Insights
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Real-time aggregated classification volume, waste stream distributions, and user ratings.
          </p>
        </div>

        <Button variant="outline" size="sm" icon={<RefreshCw size={14} />} onClick={loadMetrics} isLoading={isLoading}>
          Refresh Metrics
        </Button>
      </div>

      {error && (
        <div
          style={{
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: 'var(--status-danger)',
            fontSize: '0.875rem',
          }}
        >
          {error}
        </div>
      )}

      {/* Metrics High-level KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <Card padding="md">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Total Analyzed
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '6px' }}>
            {metrics ? metrics.total_classifications.toLocaleString() : '0'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--status-success)', marginTop: '4px' }}>
            {metrics ? `${metrics.successful_classifications} successful` : '0 successful'}
          </div>
        </Card>

        <Card padding="md">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Satisfaction Rate
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '6px' }}>
            {metrics && metrics.feedback.total_feedback > 0 ? `${metrics.feedback.helpful_percentage}%` : 'N/A'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {metrics ? `${metrics.feedback.helpful_count} helpful ratings` : '0 ratings'}
          </div>
        </Card>

        <Card padding="md">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Average Latency
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '6px' }}>
            {metrics ? `${metrics.average_processing_time_ms.toFixed(0)} ms` : '0 ms'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            End-to-end execution
          </div>
        </Card>

        <Card padding="md">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Low Confidence Rate
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '6px' }}>
            {metrics ? `${metrics.low_confidence_percentage}%` : '0%'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Safely flagged for manual check
          </div>
        </Card>
      </div>

      {/* Category Breakdown & Feedback Analysis */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {/* Category Distribution Chart / List */}
        <Card padding="md">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
            Waste Category Breakdown
          </h3>

          {metrics && metrics.categories.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {metrics.categories.map((cat, idx) => (
                <div key={idx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{cat.category}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>
                      {cat.count} ({cat.percentage}%)
                    </span>
                  </div>
                  <div
                    style={{
                      height: '8px',
                      borderRadius: '999px',
                      backgroundColor: 'var(--bg-surface-secondary)',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${cat.percentage}%`,
                        backgroundColor: 'var(--brand-green)',
                        borderRadius: '999px',
                        transition: 'width 0.5s ease-out',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No category data recorded yet.
            </div>
          )}
        </Card>

        {/* User Feedback Breakdown */}
        <Card padding="md">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '16px' }}>
            User Feedback & Verification
          </h3>

          {metrics && metrics.feedback.total_feedback > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-surface-secondary)',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Average Rating</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--brand-green)', marginTop: '2px' }}>
                    {metrics.feedback.average_rating ? `${metrics.feedback.average_rating} / 5.0` : 'Not rated'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Submissions</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {metrics.feedback.total_feedback}
                  </div>
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  Issue Type Breakdown
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {Object.entries(metrics.feedback.type_breakdown).map(([type, count]) => (
                    <div
                      key={type}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        fontSize: '0.75rem',
                        padding: '6px 10px',
                        borderRadius: 'var(--radius-sm)',
                        backgroundColor: 'var(--bg-surface-secondary)',
                      }}
                    >
                      <span style={{ color: 'var(--text-primary)' }}>{type}</span>
                      <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No user feedback submitted yet.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
