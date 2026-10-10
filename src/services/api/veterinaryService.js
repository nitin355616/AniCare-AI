import apiClient from './client';
import { MOCK_VET_CASES } from '../../data/mockData';

export const veterinaryService = {
  /**
   * Fetches real-time aggregated case statistics.
   */
  async getStats() {
    try {
      return await apiClient.get('/veterinary/stats');
    } catch (error) {
      console.warn('Backend stats unavailable, calculating from mock data:', error.message);
      const pending = MOCK_VET_CASES.filter((c) =>
        ['pending_review', 'pending review', 'pending'].includes(c.status?.toLowerCase())
      ).length;
      const highCritical = MOCK_VET_CASES.filter((c) =>
        ['high', 'critical'].includes(c.riskLevel?.toLowerCase())
      ).length;
      const treatments = MOCK_VET_CASES.filter((c) =>
        ['treatment_active', 'under treatment', 'active'].includes(c.status?.toLowerCase())
      ).length;
      const followUps = MOCK_VET_CASES.filter((c) =>
        ['follow_up', 'follow up'].includes(c.status?.toLowerCase())
      ).length;
      const closed = MOCK_VET_CASES.filter((c) =>
        ['closed', 'resolved'].includes(c.status?.toLowerCase())
      ).length;
      return {
        pending_reviews: pending,
        high_critical_cases: highCritical,
        active_treatments: treatments,
        follow_ups_due: followUps,
        closed_cases: closed,
        total_cases: MOCK_VET_CASES.length,
        vaccinations_due: 0,
        withdrawal_restrictions: 0,
      };
    }
  },

  /**
   * Fetches pending and treated veterinary clinical cases with fallback.
   */
  async getCases(params = {}) {
    try {
      const response = await apiClient.get('/veterinary/cases', params);
      return {
        data: response,
        total: response.length,
        source: 'api',
      };
    } catch (error) {
      console.warn('Backend unavailable, falling back to local demo veterinary cases:', error.message);
      let filtered = [...MOCK_VET_CASES];
      if (params.status && params.status !== 'all') {
        filtered = filtered.filter((c) => c.status?.toLowerCase() === params.status.toLowerCase());
      }
      if (params.risk && params.risk !== 'all') {
        filtered = filtered.filter((c) => c.riskLevel?.toLowerCase() === params.risk.toLowerCase());
      }
      return {
        data: filtered,
        total: filtered.length,
        source: 'mock_fallback',
        isOfflineFallback: true,
      };
    }
  },

  /**
   * Fetches single veterinary case details.
   */
  async getCaseById(caseId) {
    try {
      return await apiClient.get(`/veterinary/cases/${caseId}`);
    } catch (error) {
      console.warn(`Backend fetch failed for case ${caseId}, falling back:`, error.message);
      const found = MOCK_VET_CASES.find((c) => c.caseId === caseId || c.id === caseId);
      if (!found) {
        throw new Error(`Veterinary case ${caseId} not found`);
      }
      return found;
    }
  },

  /**
   * Creates a new veterinary case from AI triage or clinician referral.
   */
  async createCase(caseData) {
    return await apiClient.post('/veterinary/cases', caseData);
  },

  /**
   * Submits certified veterinary review notes and clinical decision.
   */
  async reviewCase(caseId, reviewData) {
    return await apiClient.put(`/veterinary/cases/${caseId}/review`, reviewData);
  },

  /**
   * Adds an approved medication treatment plan to a case.
   * Requires certified veterinary medical license number.
   */
  async prescribeTreatment(caseId, treatmentData) {
    return await apiClient.post(`/veterinary/cases/${caseId}/treatment`, treatmentData);
  },

  /**
   * Updates biosecurity quarantine, vector control, hygiene, and farmer instructions for a case.
   */
  async updatePrevention(caseId, preventionData) {
    return await apiClient.put(`/veterinary/cases/${caseId}/prevention`, preventionData);
  },

  /**
   * Updates statutory food-safety withdrawal restrictions (milk and meat withholding periods).
   */
  async updateWithdrawal(caseId, withdrawalData) {
    return await apiClient.put(`/veterinary/cases/${caseId}/withdrawal`, withdrawalData);
  },

  /**
   * Schedules a follow-up examination date for a case.
   */
  async scheduleFollowUp(caseId, followUpData) {
    return await apiClient.post(`/veterinary/cases/${caseId}/follow-up`, followUpData);
  },

  /**
   * Formally closes an active veterinary case after clinical resolution.
   */
  async closeCase(caseId, closeData) {
    return await apiClient.put(`/veterinary/cases/${caseId}/close`, closeData);
  },
};

export default veterinaryService;
