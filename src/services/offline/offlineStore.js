/**
 * AniCare AI — IndexedDB Offline Store
 * Milestone 10: Browser Database Layer for Offline Livestock Data
 */

import { STORES } from './syncTypes';

const DB_NAME = 'anicare_offline_db';
const DB_VERSION = 1;

class OfflineStore {
  constructor() {
    this.db = null;
    this.memoryFallback = new Map();
  }

  isIndexedDBSupported() {
    return typeof window !== 'undefined' && 'indexedDB' in window;
  }

  async open() {
    if (this.db) return this.db;
    if (!this.isIndexedDBSupported()) {
      return null;
    }

    return new Promise((resolve, reject) => {
      const request = window.indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = event.target.result;

        // 1. Animals Cache
        if (!db.objectStoreNames.contains(STORES.ANIMALS)) {
          const s = db.createObjectStore(STORES.ANIMALS, { keyPath: 'animal_id' });
          s.createIndex('owner', 'owner', { unique: false });
          s.createIndex('updated_at', 'updated_at', { unique: false });
        }

        // 2. Health Records Cache
        if (!db.objectStoreNames.contains(STORES.HEALTH)) {
          const s = db.createObjectStore(STORES.HEALTH, { keyPath: 'id' });
          s.createIndex('animal_id', 'animal_id', { unique: false });
          s.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // 3. Alerts Cache
        if (!db.objectStoreNames.contains(STORES.ALERTS)) {
          db.createObjectStore(STORES.ALERTS, { keyPath: 'alert_id' });
        }

        // 4. Vaccinations Cache
        if (!db.objectStoreNames.contains(STORES.VACCINATIONS)) {
          const s = db.createObjectStore(STORES.VACCINATIONS, { keyPath: 'id' });
          s.createIndex('animal_id', 'animal_id', { unique: false });
        }

        // 5. Pending Actions Queue
        if (!db.objectStoreNames.contains(STORES.PENDING_ACTIONS)) {
          const s = db.createObjectStore(STORES.PENDING_ACTIONS, { keyPath: 'local_action_id' });
          s.createIndex('status', 'status', { unique: false });
          s.createIndex('created_at', 'created_at', { unique: false });
        }

        // 6. Sync Metadata
        if (!db.objectStoreNames.contains(STORES.METADATA)) {
          db.createObjectStore(STORES.METADATA, { keyPath: 'key' });
        }
      };

      request.onsuccess = (event) => {
        this.db = event.target.result;
        resolve(this.db);
      };

      request.onerror = (event) => {
        console.warn('IndexedDB failed to open, using memory fallback:', event.target.error);
        resolve(null);
      };
    });
  }

  async put(storeName, item) {
    const db = await this.open();
    if (!db) {
      if (!this.memoryFallback.has(storeName)) {
        this.memoryFallback.set(storeName, new Map());
      }
      const key = item.animal_id || item.id || item.alert_id || item.local_action_id || item.key;
      this.memoryFallback.get(storeName).set(key, item);
      return item;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const req = store.put(item);
      req.onsuccess = () => resolve(item);
      req.onerror = () => reject(req.error);
    });
  }

  async putBatch(storeName, items) {
    if (!items || items.length === 0) return [];
    const db = await this.open();
    if (!db) {
      items.forEach((item) => this.put(storeName, item));
      return items;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      items.forEach((item) => store.put(item));
      tx.oncomplete = () => resolve(items);
      tx.onerror = () => reject(tx.error);
    });
  }

  async get(storeName, key) {
    const db = await this.open();
    if (!db) {
      const store = this.memoryFallback.get(storeName);
      return store ? store.get(key) || null : null;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => reject(req.error);
    });
  }

  async getAll(storeName) {
    const db = await this.open();
    if (!db) {
      const store = this.memoryFallback.get(storeName);
      return store ? Array.from(store.values()) : [];
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async delete(storeName, key) {
    const db = await this.open();
    if (!db) {
      const store = this.memoryFallback.get(storeName);
      if (store) store.delete(key);
      return true;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const req = store.delete(key);
      req.onsuccess = () => resolve(true);
      req.onerror = () => reject(req.error);
    });
  }

  async clear(storeName) {
    const db = await this.open();
    if (!db) {
      if (this.memoryFallback.has(storeName)) {
        this.memoryFallback.get(storeName).clear();
      }
      return true;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      const req = store.clear();
      req.onsuccess = () => resolve(true);
      req.onerror = () => reject(req.error);
    });
  }

  async count(storeName) {
    const db = await this.open();
    if (!db) {
      const store = this.memoryFallback.get(storeName);
      return store ? store.size : 0;
    }

    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const req = store.count();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }
}

export const offlineStore = new OfflineStore();
