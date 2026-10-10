/**
 * AniCare AI — Dataset Intelligence & AI Models Service
 * Interacts with /api/datasets and /api/models endpoints.
 */

import apiClient from './client';

class DatasetService {
  /**
   * Retrieves summary of all configured datasets, file counts, and audit statistics.
   */
  async getDatasetsInfo() {
    return apiClient.get('/datasets/info');
  }

  /**
   * Fetches paginated gallery images with optional filters.
   */
  async getDatasetGallery(params = {}) {
    const query = new URLSearchParams();
    if (params.dataset_key) query.append('dataset_key', params.dataset_key);
    if (params.task_type) query.append('task_type', params.task_type);
    if (params.class_label) query.append('class_label', params.class_label);
    if (params.split) query.append('split', params.split);
    if (params.page) query.append('page', params.page);
    if (params.page_size) query.append('page_size', params.page_size);

    const queryString = query.toString();
    const endpoint = `/datasets/gallery${queryString ? `?${queryString}` : ''}`;
    return apiClient.get(endpoint);
  }

  /**
   * Returns live status of trained models (Task A, B, C, baseline).
   */
  async getModelsStatus() {
    return apiClient.get('/models/status');
  }

  /**
   * Returns evaluation reports, confusion matrices, and training histories.
   */
  async getModelsMetrics() {
    return apiClient.get('/models/metrics');
  }

  /**
   * Runs genuine neural network prediction on an uploaded image.
   */
  async predictRealDisease(imageId) {
    return apiClient.post(`/detection/predict-real?image_id=${imageId}`);
  }

  /**
   * Validates animal species (Cattle vs Pet/Bird).
   */
  async validateSpecies(imageId) {
    return apiClient.post(`/detection/validate-species?image_id=${imageId}`);
  }

  /**
   * Retrieves muzzle biometric registration profiles.
   */
  async getMuzzleRegistry() {
    return apiClient.get('/detection/muzzle-registry');
  }

  /**
   * Resolves full streaming URL for an image.
   */
  getImageUrl(imageId) {
    const base = apiClient.baseUrl.replace(/\/api$/, '');
    return `${base}/api/datasets/image/${imageId}`;
  }
}

export const datasetService = new DatasetService();
export default datasetService;
