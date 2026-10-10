/**
 * AniCare AI — Sync API HTTP Client
 * Milestone 10: Network Communications for Synchronization Layer
 */

import apiClient from './client';

export const syncClient = {
  /**
   * Pushes a batch of offline actions to the backend.
   */
  async push(actions, deviceId = 'BROWSER-DEV-001') {
    return await apiClient.post('/sync/push', {
      device_id: deviceId,
      actions,
    });
  },

  /**
   * Incrementally pulls changes since the given cursor.
   */
  async pull(deviceId = 'BROWSER-DEV-001', sinceCursor = null, limit = 100) {
    return await apiClient.post('/sync/pull', {
      device_id: deviceId,
      since_cursor: sinceCursor,
      limit,
    });
  },

  /**
   * Checks server sync status, reachability, and monotonic sync version.
   */
  async getStatus(deviceId = 'BROWSER-DEV-001') {
    return await apiClient.get(`/sync/status?device_id=${encodeURIComponent(deviceId)}`);
  },

  /**
   * Resolves a conflict on the server.
   */
  async resolve(conflictId, strategy = 'SERVER_WINS', resolvedPayload = null) {
    return await apiClient.post('/sync/resolve', {
      conflict_id: conflictId,
      resolution_strategy: strategy,
      resolved_payload: resolvedPayload,
    });
  },
};
