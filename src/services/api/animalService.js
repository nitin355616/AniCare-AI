import apiClient from './client';
import { MOCK_ANIMALS } from '../../data/mockData';

export const animalService = {
  /**
   * Retrieves animals registry from backend API with fallback to demo dataset.
   */
  async getAnimals(params = {}) {
    try {
      const response = await apiClient.get('/animals', params);
      return {
        data: response.items || response,
        total: response.total ?? (response.items ? response.items.length : response.length),
        source: 'api',
      };
    } catch (error) {
      console.warn('Backend unavailable, falling back to local demo animals data:', error.message);
      // Fallback filtering
      let filtered = [...MOCK_ANIMALS];
      if (params.species && params.species !== 'All') {
        filtered = filtered.filter((a) => a.species.toLowerCase() === params.species.toLowerCase());
      }
      if (params.health_status && params.health_status !== 'All') {
        filtered = filtered.filter((a) => a.healthStatus.toLowerCase() === params.health_status.toLowerCase());
      }
      if (params.search) {
        const q = params.search.toLowerCase();
        filtered = filtered.filter(
          (a) =>
            a.name.toLowerCase().includes(q) ||
            a.tag.toLowerCase().includes(q) ||
            a.breed.toLowerCase().includes(q)
        );
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
   * Fetches single animal by identifier with fallback.
   */
  async getAnimalById(animalId) {
    try {
      const animal = await apiClient.get(`/animals/${animalId}`);
      return { data: animal, source: 'api' };
    } catch (error) {
      console.warn(`Backend fetch failed for ${animalId}, falling back:`, error.message);
      const found = MOCK_ANIMALS.find((a) => a.id === animalId || a.tag === animalId);
      if (!found) {
        throw new Error(`Animal ${animalId} not found`);
      }
      return { data: found, source: 'mock_fallback', isOfflineFallback: true };
    }
  },

  /**
   * Registers a new livestock profile.
   */
  async createAnimal(animalData) {
    return await apiClient.post('/animals', animalData);
  },

  /**
   * Updates clinical or demographic data for an animal.
   */
  async updateAnimal(animalId, updateData) {
    return await apiClient.put(`/animals/${animalId}`, updateData);
  },

  /**
   * Deletes an animal from the registry.
   */
  async deleteAnimal(animalId) {
    return await apiClient.delete(`/animals/${animalId}`);
  },

  /**
   * Fetches historical clinical health records for an animal.
   */
  async getHealthRecords(animalId) {
    try {
      return await apiClient.get(`/animals/${animalId}/health-records`);
    } catch (error) {
      console.warn(`Health records API failed for ${animalId}:`, error.message);
      return { animal_id: animalId, total: 0, records: [] };
    }
  },

  /**
   * Submits a new clinical telemetry record.
   */
  async addHealthRecord(recordData) {
    return await apiClient.post('/health-records', recordData);
  },

  /**
   * Fetches official vaccination records for an animal.
   */
  async getVaccinations(animalId) {
    try {
      return await apiClient.get(`/animals/${animalId}/vaccinations`);
    } catch (error) {
      console.warn(`Vaccinations API failed for ${animalId}:`, error.message);
      return [];
    }
  },

  /**
   * Records an authorized veterinary vaccine administration.
   */
  async addVaccination(animalId, vaccinationData) {
    return await apiClient.post(`/animals/${animalId}/vaccinations`, vaccinationData);
  },

  /**
   * Updates vaccination booster date or notes.
   */
  async updateVaccination(animalId, vaccinationId, vaccinationData) {
    return await apiClient.put(`/animals/${animalId}/vaccinations/${vaccinationId}`, vaccinationData);
  },

  /**
   * Retrieves full chronological treatment history for an animal.
   */
  async getTreatmentHistory(animalId) {
    try {
      return await apiClient.get(`/animals/${animalId}/treatment-history`);
    } catch (error) {
      console.warn(`Treatment history API failed for ${animalId}:`, error.message);
      return { animal_id: animalId, total_cases: 0, active_treatments: 0, cases: [] };
    }
  },
};

export default animalService;
