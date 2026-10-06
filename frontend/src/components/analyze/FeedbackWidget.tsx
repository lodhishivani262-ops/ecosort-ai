/**
 * EcoSort AI - User Feedback Widget Component (Stage 6).
 * Captures helpfulness rating and optional issue tags for Stage 5 API.
 */

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle2, MessageSquare } from 'lucide-react';
import { submitFeedback } from '../../api/feedback';
import type { FeedbackType } from '../../types/api';
import { Button } from '../common/Button';

interface FeedbackWidgetProps {
  requestId: string;
}

const ISSUE_OPTIONS: { type: FeedbackType; label: string }[] = [
  { type: 'INCORRECT_CATEGORY', label: 'Wrong Category' },
  { type: 'INCORRECT_IDENTIFICATION', label: 'Item misidentified' },
  { type: 'UNCLEAR_GUIDANCE', label: 'Unclear guidance' },
  { type: 'OTHER', label: 'Other' },
];

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ requestId }) => {
  const [selectedSentiment, setSelectedSentiment] = useState<'yes' | 'no' | null>(null);
  const [issueType, setIssueType] = useState<FeedbackType>('NOT_HELPFUL');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePositiveFeedback = async () => {
    setSelectedSentiment('yes');
    setIsSubmitting(true);
    setError(null);
    try {
      await submitFeedback({
        request_id: requestId,
        rating: 5,
        feedback_type: 'HELPFUL',
        comment: null,
      });
      setIsSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNegativeFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await submitFeedback({
        request_id: requestId,
        rating: 2,
        feedback_type: issueType,
        comment: comment.trim() || null,
      });
      setIsSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div
        style={{
          padding: '14px 18px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          color: 'var(--brand-green)',
          fontSize: '0.875rem',
          fontWeight: 500,
        }}
      >
        <CheckCircle2 size={18} />
        <span>Thank you for your feedback! It helps improve EcoSort AI.</span>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: '16px 20px',
        borderRadius: 'var(--radius-lg)',
        backgroundColor: 'var(--bg-surface-secondary)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <MessageSquare size={16} color="var(--brand-green)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Was this disposal recommendation helpful?
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Button
            variant={selectedSentiment === 'yes' ? 'primary' : 'outline'}
            size="sm"
            icon={<ThumbsUp size={14} />}
            disabled={isSubmitting}
            onClick={handlePositiveFeedback}
          >
            Yes
          </Button>
          <Button
            variant={selectedSentiment === 'no' ? 'danger' : 'outline'}
            size="sm"
            icon={<ThumbsDown size={14} />}
            disabled={isSubmitting}
            onClick={() => setSelectedSentiment('no')}
          >
            No
          </Button>
        </div>
      </div>

      {/* Negative Feedback Options Expansion */}
      {selectedSentiment === 'no' && (
        <form onSubmit={handleNegativeFeedbackSubmit} style={{ marginTop: '16px' }}>
          <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
            What was the issue?
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' }}>
            {ISSUE_OPTIONS.map((opt) => (
              <button
                key={opt.type}
                type="button"
                onClick={() => setIssueType(opt.type)}
                style={{
                  padding: '6px 12px',
                  borderRadius: '999px',
                  fontSize: '0.75rem',
                  fontWeight: 500,
                  backgroundColor: issueType === opt.type ? 'var(--brand-green)' : 'var(--bg-surface)',
                  color: issueType === opt.type ? '#ffffff' : 'var(--text-secondary)',
                  border: `1px solid ${issueType === opt.type ? 'var(--brand-green)' : 'var(--border-default)'}`,
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                }}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Optional comment: What was the item or what should be changed? (max 500 characters)"
            maxLength={500}
            rows={2}
            style={{
              width: '100%',
              padding: '10px 12px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-default)',
              backgroundColor: 'var(--bg-input)',
              color: 'var(--text-primary)',
              fontSize: '0.8125rem',
              outline: 'none',
              resize: 'none',
              marginBottom: '10px',
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setSelectedSentiment(null)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Submit Feedback
            </Button>
          </div>
        </form>
      )}

      {error && (
        <div style={{ color: 'var(--status-danger)', fontSize: '0.75rem', marginTop: '8px' }}>
          {error}
        </div>
      )}
    </div>
  );
};
