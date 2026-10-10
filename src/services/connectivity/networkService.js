/**
 * AniCare AI — Network & Connectivity Service (Milestone 10 Upgraded)
 *
 * Facade linking existing components to ConnectivityManager and OfflineStore.
 */

import { connectivityManager } from '../offline/connectivityManager';
import { offlineStore } from '../offline/offlineStore';
import { STORES } from '../offline/syncTypes';

const CACHE_KEYS = {
  FARMER_DASHBOARD: 'anicare_farmer_dashboard_cache',
  PENDING_REVIEWS: 'anicare_farmer_pending_reviews',
};

class NetworkService {
  get isOnline() {
    return connectivityManager.getStatusInfo().isOnline;
  }

  subscribe(listener) {
    return connectivityManager.subscribe((info) => {
      listener(info.isOnline);
    });
  }

  getOnlineStatus() {
    return connectivityManager.getStatusInfo().isOnline;
  }

  getStatusInfo() {
    return connectivityManager.getStatusInfo();
  }

  // Save to both IndexedDB and localStorage fallback
  async saveDashboardCache(data) {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(
          CACHE_KEYS.FARMER_DASHBOARD,
          JSON.stringify({
            data,
            cachedAt: new Date().toISOString(),
          })
        );
      }
      if (data && data.animals) {
        await offlineStore.putBatch(STORES.ANIMALS, data.animals);
      }
    } catch (e) {
      console.warn('Failed to cache farmer dashboard:', e);
    }
  }

  getDashboardCache() {
    try {
      if (typeof localStorage !== 'undefined') {
        const item = localStorage.getItem(CACHE_KEYS.FARMER_DASHBOARD);
        if (item) {
          return JSON.parse(item);
        }
      }
    } catch (e) {
      console.warn('Failed to read farmer dashboard cache:', e);
    }
    return null;
  }
}

export const networkService = new NetworkService();
