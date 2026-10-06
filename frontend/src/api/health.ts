/**
 * EcoSort AI - Health Check API (Stage 6).
 */

import { apiClient } from './client';

export interface HealthStatus {
  status: string;
  service: string;
}

export async function fetchHealth(): Promise<HealthStatus> {
  return apiClient<HealthStatus>('/health', {
    method: 'GET',
  });
}
