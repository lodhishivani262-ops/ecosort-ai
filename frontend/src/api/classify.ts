/**
 * EcoSort AI - Waste Classification API (Stage 6).
 */

import type { ClassificationResultResponse } from '../types/api';
import { apiClient } from './client';

export async function classifyText(text: string): Promise<ClassificationResultResponse> {
  return apiClient<ClassificationResultResponse>('/api/v1/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export async function classifyImage(file: File): Promise<ClassificationResultResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return apiClient<ClassificationResultResponse>('/api/v1/classify', {
    method: 'POST',
    body: formData,
  });
}
