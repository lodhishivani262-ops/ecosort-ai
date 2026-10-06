/**
 * EcoSort AI - Central API Client (Stage 6).
 * Injects anonymous X-Session-ID header and normalizes backend error responses.
 */

import type { ApiErrorResponse } from '../types/api';
import { getOrCreateSessionId } from '../utils/session';

// Base URL: Vite proxy handles '/api' and '/health' in dev; configurable in prod
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string = 'API_ERROR', status: number = 500) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const sessionId = getOrCreateSessionId();

  const headers = new Headers(options.headers || {});
  headers.set('X-Session-ID', sessionId);

  // If payload is not FormData, default Content-Type to application/json
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorCode = `HTTP_${response.status}`;
      let errorMessage = `Server returned status ${response.status}`;

      try {
        const errorJson = (await response.json()) as ApiErrorResponse | { detail?: string };
        if ('error' in errorJson && errorJson.error) {
          errorCode = errorJson.error.code || errorCode;
          errorMessage = errorJson.error.message || errorMessage;
        } else if ('detail' in errorJson && typeof errorJson.detail === 'string') {
          errorMessage = errorJson.detail;
        }
      } catch {
        // Fallback to text status
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiError(errorMessage, errorCode, response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // Network / offline error
    throw new ApiError(
      'Unable to connect to EcoSort AI backend. Please verify the server is running.',
      'NETWORK_ERROR',
      0
    );
  }
}
