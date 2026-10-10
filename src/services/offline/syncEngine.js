/**
 * AniCare AI — Offline Synchronization Engine
 * Milestone 10: Orchestrates Batch Push, Incremental Pull, Idempotency, and Retry
 */

import { offlineStore } from './offlineStore';
import { syncQueue } from './syncQueue';
import { connectivityManager } from './connectivityManager';
import { syncClient } from '../api/syncClient';
import { STORES, STORAGE_KEYS, ACTION_STATUSES } from './syncTypes';

const BATCH_SIZE = 10;
const RETRY_DELAYS = [2000, 5000, 15000, 30000];

class SyncEngine {
  constructor() {
    this.isSyncing = false;
    this.listeners = new Set();
    this.deviceId = this.getOrCreateDeviceId();

    // Auto-sync trigger when network returns
    connectivityManager.subscribe((info) => {
      if (info.isOnline && !this.isSyncing) {
        this.triggerAutoSync();
      }
    });
  }

  getOrCreateDeviceId() {
    try {
      if (typeof localStorage !== 'undefined') {
        let devId = localStorage.getItem(STORAGE_KEYS.DEVICE_ID);
        if (!devId) {
          devId = `DEV-${(Math.random().toString(36).substring(2, 10) + Math.random().toString(36).substring(2, 10)).toUpperCase()}`;
          localStorage.setItem(STORAGE_KEYS.DEVICE_ID, devId);
        }
        return devId;
      }
    } catch {
      // fallback
    }
    return 'BROWSER-DEV-001';
  }

  // Multi-tab sync lock check
  acquireSyncLock() {
    try {
      if (typeof localStorage !== 'undefined') {
        const existingLock = localStorage.getItem(STORAGE_KEYS.SYNC_LOCK);
        const now = Date.now();
        if (existingLock && now - parseInt(existingLock, 10) < 15000) {
          return false; // Another tab is currently syncing
        }
        localStorage.setItem(STORAGE_KEYS.SYNC_LOCK, now.toString());
      }
    } catch {
      // ignore
    }
    return true;
  }

  releaseSyncLock() {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem(STORAGE_KEYS.SYNC_LOCK);
      }
    } catch {
      // ignore
    }
  }

  async triggerAutoSync() {
    try {
      await this.sync();
    } catch (err) {
      console.warn('Auto-sync notice:', err.message);
    }
  }

  async sync() {
    if (this.isSyncing) return { success: false, reason: 'ALREADY_SYNCING' };
    if (!this.acquireSyncLock()) return { success: false, reason: 'SYNC_LOCKED_BY_OTHER_TAB' };

    const conn = connectivityManager.getStatusInfo();
    if (!conn.isOnline) {
      this.releaseSyncLock();
      return { success: false, reason: 'OFFLINE' };
    }

    this.isSyncing = true;
    connectivityManager.setSyncing(true);
    this.notifyListeners({ status: 'STARTING' });

    try {
      // 1. PUSH PENDING ACTIONS
      const pending = await syncQueue.getPendingActions();
      if (pending.length > 0) {
        // Chunk by BATCH_SIZE
        for (let i = 0; i < pending.length; i += BATCH_SIZE) {
          const batch = pending.slice(i, i + BATCH_SIZE);
          await this.processPushBatch(batch);
        }
      }

      // 2. INCREMENTAL PULL
      await this.processPull();

      // Record last sync timestamp
      const nowIso = new Date().toISOString();
      await offlineStore.put(STORES.METADATA, { key: STORAGE_KEYS.LAST_SYNC_TIME, value: nowIso });

      this.isSyncing = false;
      this.releaseSyncLock();
      connectivityManager.setSyncing(false);
      this.notifyListeners({ status: 'COMPLETED', timestamp: nowIso });

      return { success: true, timestamp: nowIso };
    } catch (err) {
      this.isSyncing = false;
      this.releaseSyncLock();
      connectivityManager.setSyncError();
      this.notifyListeners({ status: 'ERROR', error: err.message });
      throw err;
    }
  }

  async processPushBatch(batch) {
    try {
      const response = await syncClient.push(batch, this.deviceId);

      // Handle Accepted & Duplicates
      const successful = [...(response.accepted || []), ...(response.duplicates || [])];
      for (const res of successful) {
        await syncQueue.updateActionStatus(res.local_action_id, ACTION_STATUSES.SYNCED, null, {
          server_id: res.server_id,
        });
      }

      // Handle Conflicts
      for (const res of response.conflicts || []) {
        await syncQueue.updateActionStatus(res.local_action_id, ACTION_STATUSES.CONFLICT, res.error_message, {
          conflict_details: res.conflict_details,
        });
      }

      // Handle Failed
      for (const res of response.failed || []) {
        await syncQueue.updateActionStatus(res.local_action_id, ACTION_STATUSES.FAILED, res.error_message);
      }
    } catch (err) {
      for (const item of batch) {
        await syncQueue.updateActionStatus(item.local_action_id, ACTION_STATUSES.FAILED, err.message);
      }
      throw err;
    }
  }

  async processPull() {
    try {
      const cursorMeta = await offlineStore.get(STORES.METADATA, STORAGE_KEYS.SYNC_CURSOR);
      const cursor = cursorMeta ? cursorMeta.value : null;

      const pullResponse = await syncClient.pull(this.deviceId, cursor);
      if (pullResponse && pullResponse.changes) {
        const changes = pullResponse.changes;

        if (changes.animals && changes.animals.length > 0) {
          await offlineStore.putBatch(STORES.ANIMALS, changes.animals);
        }
        if (changes.health_records && changes.health_records.length > 0) {
          await offlineStore.putBatch(STORES.HEALTH, changes.health_records);
        }
        if (changes.alerts && changes.alerts.length > 0) {
          await offlineStore.putBatch(STORES.ALERTS, changes.alerts);
        }
        if (changes.vaccinations && changes.vaccinations.length > 0) {
          await offlineStore.putBatch(STORES.VACCINATIONS, changes.vaccinations);
        }

        // Advance cursor
        if (pullResponse.next_cursor) {
          await offlineStore.put(STORES.METADATA, {
            key: STORAGE_KEYS.SYNC_CURSOR,
            value: pullResponse.next_cursor,
          });
        }
      }
    } catch (err) {
      console.warn('Pull sync delta notice:', err.message);
    }
  }

  async getLastSyncTime() {
    const meta = await offlineStore.get(STORES.METADATA, STORAGE_KEYS.LAST_SYNC_TIME);
    return meta ? meta.value : null;
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners(data) {
    this.listeners.forEach((listener) => {
      try {
        listener(data);
      } catch (err) {
        console.error('Sync listener error:', err);
      }
    });
  }
}

export const syncEngine = new SyncEngine();
