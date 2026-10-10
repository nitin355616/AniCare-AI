/**
 * AniCare AI — Offline Sync Action Queue
 * Milestone 10: Persistent Pending Action Queue with Idempotency Keys
 */

import { offlineStore } from './offlineStore';
import { STORES, ACTION_STATUSES } from './syncTypes';

export function generateUUID() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

class SyncQueue {
  async enqueueAction({ actionType, entityType, entityId = null, payload = {} }) {
    const localActionId = generateUUID();
    const idempotencyKey = `IDEMP-${generateUUID()}`;
    const nowIso = new Date().toISOString();

    const actionItem = {
      local_action_id: localActionId,
      idempotency_key: idempotencyKey,
      action_type: actionType,
      entity_type: entityType,
      entity_id: entityId,
      payload,
      client_timestamp: nowIso,
      client_version: 1,
      status: ACTION_STATUSES.PENDING,
      retry_count: 0,
      last_error: null,
      created_at: nowIso,
    };

    await offlineStore.put(STORES.PENDING_ACTIONS, actionItem);
    return actionItem;
  }

  async getPendingActions() {
    const all = await offlineStore.getAll(STORES.PENDING_ACTIONS);
    return all.filter((a) => a.status === ACTION_STATUSES.PENDING || a.status === ACTION_STATUSES.FAILED);
  }

  async getAllActions() {
    return await offlineStore.getAll(STORES.PENDING_ACTIONS);
  }

  async updateActionStatus(localActionId, status, error = null, extra = {}) {
    const item = await offlineStore.get(STORES.PENDING_ACTIONS, localActionId);
    if (!item) return null;

    item.status = status;
    if (error) {
      item.last_error = error;
      item.retry_count = (item.retry_count || 0) + 1;
    }
    Object.assign(item, extra);

    await offlineStore.put(STORES.PENDING_ACTIONS, item);
    return item;
  }

  async removeAction(localActionId) {
    await offlineStore.delete(STORES.PENDING_ACTIONS, localActionId);
  }

  async clearQueue() {
    await offlineStore.clear(STORES.PENDING_ACTIONS);
  }

  async getQueueStats() {
    const all = await offlineStore.getAll(STORES.PENDING_ACTIONS);
    const pending = all.filter((a) => a.status === ACTION_STATUSES.PENDING).length;
    const failed = all.filter((a) => a.status === ACTION_STATUSES.FAILED).length;
    const conflicts = all.filter((a) => a.status === ACTION_STATUSES.CONFLICT).length;
    const synced = all.filter((a) => a.status === ACTION_STATUSES.SYNCED || a.status === ACTION_STATUSES.ACCEPTED).length;

    return {
      total: all.length,
      pending,
      failed,
      conflicts,
      synced,
    };
  }
}

export const syncQueue = new SyncQueue();
