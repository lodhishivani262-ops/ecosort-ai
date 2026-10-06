/**
 * EcoSort AI - Multi-step Analysis Loading Component (Stage 6).
 */

import React, { useEffect, useState } from 'react';
import { Sparkles, CheckCircle2, Circle } from 'lucide-react';
import { Card } from '../common/Card';

const STEPS = [
  'Inspecting visual and descriptive features...',
  'Recognizing base physical material...',
  'Checking physical condition & food contamination...',
  'Evaluating EcoSort Rule Engine & safety guardrails...',
];

export const LoadingState: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 600);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card padding="lg" style={{ textAlign: 'center', maxWidth: '500px', margin: '20px auto' }}>
      <div
        style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          backgroundColor: 'var(--brand-green-muted)',
          color: 'var(--brand-green)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          boxShadow: 'var(--shadow-accent)',
          animation: 'pulseGlow 2s infinite',
        }}
      >
        <Sparkles size={28} />
      </div>

      <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
        Analyzing Waste Item...
      </h3>
      <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
        Synthesizing AI perception with deterministic waste segregation logic
      </p>

      {/* Step Progress Checklist */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left', padding: '0 8px' }}>
        {STEPS.map((step, idx) => {
          const isDone = idx < currentStepIndex;
          const isCurrent = idx === currentStepIndex;

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                opacity: idx <= currentStepIndex ? 1 : 0.4,
                transition: 'opacity var(--transition-normal)',
              }}
            >
              {isDone ? (
                <CheckCircle2 size={18} color="var(--brand-green)" />
              ) : isCurrent ? (
                <span
                  style={{
                    width: '18px',
                    height: '18px',
                    borderRadius: '50%',
                    border: '2px solid var(--brand-green)',
                    borderTopColor: 'transparent',
                    animation: 'spin 0.8s linear infinite',
                    display: 'inline-block',
                  }}
                />
              ) : (
                <Circle size={18} color="var(--text-muted)" />
              )}
              <span
                style={{
                  fontSize: '0.875rem',
                  fontWeight: isCurrent ? 600 : 400,
                  color: isCurrent ? 'var(--text-primary)' : 'var(--text-secondary)',
                }}
              >
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
