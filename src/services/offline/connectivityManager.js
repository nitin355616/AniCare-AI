/**
 * AniCare AI — Connectivity Manager
 * Milestone 10: Multi-State Network Reachability & Health Tracking
 */

import { CONNECTIVITY_STATES } from './syncTypes';
import { syncClient } from '../api/syncClient';

class ConnectivityManager {
  constructor() {
    this.state = typeof navigator !== 'undefined' && navigator.onLine
      ? CONNECTIVITY_STATES.ONLINE
      : CONNECTIVITY_STATES.OFFLINE;
    this.serverReachable = true;
    this.latencyMs = 0;
    this.listeners = new Set();
    this.checkInterval = null;

    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => this.handleNetworkEvent(true));
      window.addEventListener('offline', () => this.handleNetworkEvent(false));
      // Periodic reachability check every 30 seconds
      this.checkInterval = setInterval(() => {
        if (navigator.onLine) {
          this.checkReachability();
        }
      }, 30000);
    }
  }

  handleNetworkEvent(isOnline) {
    if (!isOnline) {
      this.serverReachable = false;
      this.setState(CONNECTIVITY_STATES.OFFLINE);
    } else {
      this.checkReachability();
    }
  }

  async checkReachability() {
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      this.serverReachable = false;
      this.setState(CONNECTIVITY_STATES.OFFLINE);
      return false;
    }

    const start = performance.now();
    try {
      const res = await syncClient.getStatus();
      this.latencyMs = Math.round(performance.now() - start);
      this.serverReachable = Boolean(res && res.is_healthy);

      if (this.latencyMs > 2500) {
        this.setState(CONNECTIVITY_STATES.UNSTABLE);
      } else {
        this.setState(CONNECTIVITY_STATES.ONLINE);
      }
      return true;
    } catch {
      this.serverReachable = false;
      this.latencyMs = 0;
      this.setState(CONNECTIVITY_STATES.OFFLINE);
      return false;
    }
  }

  setState(newState) {
    if (this.state !== newState) {
      this.state = newState;
      this.notifyListeners();
    }
  }

  setSyncing(isSyncing) {
    if (isSyncing) {
      this.setState(CONNECTIVITY_STATES.SYNCING);
    } else {
      this.checkReachability();
    }
  }

  setSyncError() {
    this.setState(CONNECTIVITY_STATES.SYNC_ERROR);
  }

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  notifyListeners() {
    const info = this.getStatusInfo();
    this.listeners.forEach((listener) => {
      try {
        listener(info);
      } catch (err) {
        console.error('Connectivity listener error:', err);
      }
    });
  }

  getStatusInfo() {
    return {
      state: this.state,
      isOnline: this.state === CONNECTIVITY_STATES.ONLINE || this.state === CONNECTIVITY_STATES.UNSTABLE || this.state === CONNECTIVITY_STATES.SYNCING,
      serverReachable: this.serverReachable,
      latencyMs: this.latencyMs,
    };
  }
}

export const connectivityManager = new ConnectivityManager();
