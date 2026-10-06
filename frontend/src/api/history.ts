/**
 * EcoSort AI - Anonymous Session History API (Stage 6).
 */

import type { HistoryResponse } from '../types/api';
import { getOrCreateSessionId } from '../utils/session';
import { apiClient } from './client';

export async function fetchSessionHistory(
  limit: number = 20,
  offset: number = 0
): Promise<HistoryResponse> {
  const sessionId = getOrCreateSessionId();
  const params = new URLSearchParams({
    session_id: sessionId,
    limit: limit.toString(),
    offset: offset.toString(),
  });

  return apiClient<HistoryResponse>(`/api/v1/history?${params.toString()}`, {
    method: 'GET',
  });
}
