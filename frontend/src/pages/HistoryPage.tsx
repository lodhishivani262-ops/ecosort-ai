/**
 * EcoSort AI - Anonymous Session History Page (Stage 6).
 */

import React, { useEffect, useState } from 'react';
import { History, RefreshCw, Trash2, Eye, Sparkles } from 'lucide-react';
import { fetchSessionHistory } from '../api/history';
import type { ClassificationHistoryItem } from '../types/api';
import { resetSessionId } from '../utils/session';
import { formatRelativeTime } from '../utils/formatters';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { CategoryBadge } from '../components/common/Badge';
import { Modal } from '../components/common/Modal';

export const HistoryPage: React.FC = () => {
  const [items, setItems] = useState<ClassificationHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<ClassificationHistoryItem | null>(null);

  const loadHistory = () => {
    setIsLoading(true);
    fetchSessionHistory(50, 0)
      .then((res) => setItems(res.items || []))
      .catch((err) => console.error('Failed to load history', err))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleResetSession = () => {
    if (window.confirm('Start a new anonymous session? Your previous scan history will be detached.')) {
      resetSessionId();
      setItems([]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header and Controls */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Anonymous Scan History
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Past classifications associated with your private browser session token.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <Button variant="outline" size="sm" icon={<RefreshCw size={14} />} onClick={loadHistory} isLoading={isLoading}>
            Refresh
          </Button>
          <Button variant="danger" size="sm" icon={<Trash2 size={14} />} onClick={handleResetSession}>
            Reset Session
          </Button>
        </div>
      </div>

      {/* History Items List */}
      {items.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {items.map((item) => (
            <Card
              key={item.request_id}
              padding="sm"
              isHoverable
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px',
              }}
              onClick={() => setSelectedItem(item)}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--brand-green)',
                  }}
                >
                  <Sparkles size={18} />
                </div>

                <div>
                  <div style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {item.item_name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', gap: '8px', marginTop: '2px' }}>
                    <span>{formatRelativeTime(item.created_at)}</span>
                    <span>•</span>
                    <span>{item.material}</span>
                    <span>•</span>
                    <span>{item.condition}</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <CategoryBadge category={item.category} size="sm" />
                <Button variant="ghost" size="sm" icon={<Eye size={14} />} onClick={(e) => { e.stopPropagation(); setSelectedItem(item); }}>
                  View
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card padding="lg" style={{ textAlign: 'center', padding: '48px 24px' }}>
          <History size={40} style={{ margin: '0 auto 12px', opacity: 0.3, color: 'var(--text-muted)' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            No History Yet
          </h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
            Items you classify in the Analyzer will appear here under your private anonymous session token.
          </p>
        </Card>
      )}

      {/* Item Detail Modal */}
      {selectedItem && (
        <Modal
          isOpen={!!selectedItem}
          onClose={() => setSelectedItem(null)}
          title={selectedItem.item_name}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <CategoryBadge category={selectedItem.category} size="md" />
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {new Date(selectedItem.created_at).toLocaleString()}
              </span>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '12px',
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--bg-surface-secondary)',
              }}
            >
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Material</span>
                <strong style={{ fontSize: '0.875rem' }}>{selectedItem.material}</strong>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Condition</span>
                <strong style={{ fontSize: '0.875rem' }}>{selectedItem.condition}</strong>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Contamination</span>
                <strong style={{ fontSize: '0.875rem' }}>{selectedItem.contamination}</strong>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Confidence</span>
                <strong style={{ fontSize: '0.875rem' }}>{selectedItem.recommendation_confidence}</strong>
              </div>
            </div>

            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Latency: {selectedItem.processing_time_ms}ms</span>
              <span style={{ fontFamily: 'var(--font-mono)' }}>ID: {selectedItem.request_id}</span>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
