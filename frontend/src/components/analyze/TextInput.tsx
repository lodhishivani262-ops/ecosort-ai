/**
 * EcoSort AI - Text Description Input Component (Stage 6).
 */

import React from 'react';

interface TextInputProps {
  value: string;
  onChange: (val: string) => void;
  disabled?: boolean;
}

const SAMPLE_PROMPTS = [
  'Used clean plastic water bottle',
  'Greasy takeaway cardboard pizza box',
  'Rechargeable lithium-ion battery',
  'Broken glass bottle shards',
  'Used disposable baby diaper',
  'Empty aluminum soda can',
];

export const TextInput: React.FC<TextInputProps> = ({ value, onChange, disabled = false }) => {
  return (
    <div>
      <label
        htmlFor="waste-text-input"
        style={{
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: 600,
          color: 'var(--text-primary)',
          marginBottom: '8px',
        }}
      >
        Describe the household item
      </label>

      <textarea
        id="waste-text-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="e.g., Used plastic food container with sauce residue..."
        rows={3}
        maxLength={500}
        style={{
          width: '100%',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-default)',
          backgroundColor: 'var(--bg-input)',
          color: 'var(--text-primary)',
          fontSize: '0.875rem',
          outline: 'none',
          resize: 'vertical',
          transition: 'border-color var(--transition-fast)',
        }}
        className="ecosort-textarea"
      />

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginTop: '6px',
        }}
      >
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Quick suggestions:
        </span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {value.length}/500
        </span>
      </div>

      {/* Suggestion Pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '6px' }}>
        {SAMPLE_PROMPTS.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onChange(sample)}
            style={{
              padding: '4px 10px',
              borderRadius: '999px',
              fontSize: '0.75rem',
              backgroundColor: 'var(--bg-surface-secondary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all var(--transition-fast)',
            }}
            className="suggestion-pill"
          >
            {sample}
          </button>
        ))}
      </div>
    </div>
  );
};
