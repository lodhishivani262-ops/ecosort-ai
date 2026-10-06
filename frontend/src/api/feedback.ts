/**
 * EcoSort AI - User Feedback API (Stage 6).
 */

import type { FeedbackCreate, FeedbackResponse } from '../types/api';
import { apiClient } from './client';

export async function submitFeedback(payload: FeedbackCreate): Promise<FeedbackResponse> {
  return apiClient<FeedbackResponse>('/api/v1/feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
