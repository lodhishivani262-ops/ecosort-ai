/**
 * EcoSort AI - Aggregated Metrics API (Stage 6).
 */

import type { MetricsResponse } from '../types/api';
import { apiClient } from './client';

export async function fetchAggregatedMetrics(): Promise<MetricsResponse> {
  return apiClient<MetricsResponse>('/api/v1/metrics', {
    method: 'GET',
  });
}
