import apiClient from './client';
import { MOCK_ALERTS } from '../../data/mockData';

export const alertService = {
  /**
   * Fetches active and historical biosecurity alerts with mock fallback.
   */
  async getAlerts(params = {}) {
    try {
      const response = await apiClient.get('/alerts', params);
      return {
        data: response.items || response,
        total: response.total ?? (response.items ? response.items.length : response.length),
        unacknowledged: response.unacknowledged ?? 0,
        source: 'api',
      };
    } catch (error) {
      console.warn('Backend unavailable, falling back to local demo alerts:', error.message);
      let filtered = [...MOCK_ALERTS];
      if (params.alert_type && params.alert_type !== 'all') {
        filtered = filtered.filter(
          (a) => a.type?.toLowerCase() === params.alert_type.toLowerCase() ||
                 a.alert_type?.toLowerCase() === params.alert_type.toLowerCase()
        );
      }
      if (params.severity && params.severity !== 'all') {
        filtered = filtered.filter((a) => a.severity?.toLowerCase() === params.severity.toLowerCase());
      }
      return {
        data: filtered,
        total: filtered.length,
        unacknowledged: filtered.filter((a) => a.status === 'Active').length,
        source: 'mock_fallback',
        isOfflineFallback: true,
      };
    }
  },

  /**
   * Dispatches a new biosecurity alert.
   */
  async createAlert(alertData) {
    return await apiClient.post('/alerts', alertData);
  },

  /**
   * Acknowledges an existing alert.
   */
  async acknowledgeAlert(alertId, acknowledgeData) {
    return await apiClient.put(`/alerts/${alertId}/acknowledge`, acknowledgeData);
  },
};

export default alertService;
