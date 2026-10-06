/**
 * EcoSort AI - Anonymous Session Management (Stage 6).
 * Manages privacy-first, client-generated anonymous session IDs in localStorage.
 */

const SESSION_STORAGE_KEY = 'ecosort_session_id';

export function getOrCreateSessionId(): string {
  try {
    const existing = localStorage.getItem(SESSION_STORAGE_KEY);
    if (existing && existing.trim()) {
      return existing.trim();
    }
  } catch (e) {
    // LocalStorage might be disabled in private mode
    console.warn('LocalStorage unavailable, generating in-memory session ID', e);
  }

  // Generate standard UUIDv4
  const newId =
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `sess-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

  try {
    localStorage.setItem(SESSION_STORAGE_KEY, newId);
  } catch (e) {
    console.warn('Failed to store session ID in localStorage', e);
  }

  return newId;
}

export function resetSessionId(): string {
  const newId =
    typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `sess-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

  try {
    localStorage.setItem(SESSION_STORAGE_KEY, newId);
  } catch (e) {
    console.warn('Failed to reset session ID in localStorage', e);
  }

  return newId;
}
