/**
 * AniCare AI — Sync & Offline Constants & Types
 * Milestone 10: Offline-First Architecture
 */

export const ACTION_TYPES = {
  CREATE_HEALTH_OBSERVATION: 'CREATE_HEALTH_OBSERVATION',
  REQUEST_DOCTOR_VISIT: 'REQUEST_DOCTOR_VISIT',
  UPDATE_ANIMAL_OBSERVATION: 'UPDATE_ANIMAL_OBSERVATION',
  CREATE_SCREENING_REQUEST: 'CREATE_SCREENING_REQUEST',
  ACKNOWLEDGE_FOLLOW_UP: 'ACKNOWLEDGE_FOLLOW_UP',
};

export const ACTION_STATUSES = {
  PENDING: 'PENDING',
  SYNCING: 'SYNCING',
  SYNCED: 'SYNCED',
  ACCEPTED: 'ACCEPTED',
  DUPLICATE: 'DUPLICATE',
  FAILED: 'FAILED',
  CONFLICT: 'CONFLICT',
  CANCELLED: 'CANCELLED',
};

export const CONNECTIVITY_STATES = {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  UNSTABLE: 'UNSTABLE',
  SYNCING: 'SYNCING',
  SYNC_ERROR: 'SYNC_ERROR',
};

export const CONFLICT_STRATEGIES = {
  SERVER_WINS: 'SERVER_WINS',
  CLIENT_WINS: 'CLIENT_WINS',
  KEEP_BOTH: 'KEEP_BOTH',
};

export const STORES = {
  ANIMALS: 'animals_cache',
  HEALTH: 'health_cache',
  ALERTS: 'alerts_cache',
  VACCINATIONS: 'vaccinations_cache',
  PENDING_ACTIONS: 'pending_actions',
  METADATA: 'sync_metadata',
};

export const STORAGE_KEYS = {
  SYNC_CURSOR: 'last_successful_sync_cursor',
  LAST_SYNC_TIME: 'last_sync_timestamp',
  DEVICE_ID: 'anicare_device_id',
  SYNC_LOCK: 'anicare_sync_lock',
};
