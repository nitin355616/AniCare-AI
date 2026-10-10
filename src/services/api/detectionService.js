import apiClient from './client';

export const detectionService = {
  /**
   * Uploads an animal photograph for computer vision screening.
   * Returns unique image ID and secure storage URL.
   */
  async uploadPhoto(file) {
    const formData = new FormData();
    formData.append('file', file);
    return await apiClient.upload('/detection/upload', formData);
  },

  /**
   * Runs disease assessment on multivariable symptoms and telemetry.
   * Supports live FastAPI demo engine with fallback to local simulation.
   */
  async analyzeDisease(payload) {
    try {
      const response = await apiClient.post('/detection/analyze', payload);
      return {
        ...response,
        source: 'api',
      };
    } catch (error) {
      console.warn('Backend inference unavailable, using local simulated assessment:', error.message);
      // Fallback structured simulation matching the exact contract
      return {
        assessment_id: `ASM-${Date.now().toString(36).toUpperCase()}`,
        is_demo_inference: true,
        model_version: 'AniCare-Net v1.2-DemoEngine (Client Fallback)',
        possible_condition: 'Respiratory Infection',
        risk_level: 'HIGH',
        confidence: 87.0,
        symptoms_detected: payload.symptoms && payload.symptoms.length > 0 ? payload.symptoms : [
          'Rapid, shallow dyspneic breathing',
          'Serous nasal discharge',
          'Core pyrexia'
        ],
        explanation: 'Syndromic signs indicate acute Bovine Respiratory Disease Complex (BRDC) requiring immediate clinical stabilization.',
        recommended_immediate_actions: [
          'Isolate affected animal in a dry, well-ventilated recovery stall.',
          'Conduct thoracic auscultation and evaluate lung sound rales.',
          'Separate cohort animals sharing common water troughs.'
        ],
        veterinary_review_required: true,
        preventive_actions: [
          'Enhance cross-ventilation rate in housing shed to lower aerosol bacterial load.',
          'Administer multivalent BRD vaccine to young stock under 12 months.'
        ],
        differential_diagnoses: [
          { disease: 'Bovine Respiratory Disease Complex', probability: 87.0, rationale: 'Tachypnea, fever, and purulent nasal discharge.' },
          { disease: 'Infectious Bovine Rhinotracheitis (IBR)', probability: 8.8, rationale: 'Lower necrotic diphtheritic plaque density.' },
          { disease: 'Aspiration Pneumonia', probability: 4.2, rationale: 'No prior forced drenching history.' }
        ],
        disclaimer: 'DEMO AI ASSESSMENT: Prototype inference simulation for SIH 2026. This assist tool does NOT issue medical prescriptions.',
        created_at: new Date().toISOString(),
        source: 'mock_fallback',
        isOfflineFallback: true,
      };
    }
  },

  /**
   * Retrieves past disease assessments history.
   */
  async getHistory(params = {}) {
    try {
      return await apiClient.get('/history', params);
    } catch (error) {
      console.warn('Backend history unavailable, using fallback:', error.message);
      return {
        total: 1,
        items: [
          {
            assessment_id: 'ASM-8821-RESP',
            animal_id: 'TAG-8821',
            species: 'Cattle (Bovine)',
            possible_condition: 'Bovine Respiratory Disease Complex',
            risk_level: 'HIGH',
            confidence: 87.4,
            explanation: 'Syndromic signs indicate acute Bovine Respiratory Disease Complex (BRDC).',
            symptoms_detected: ['Rapid, shallow dyspneic breathing', 'Serous nasal discharge', 'Core pyrexia'],
            recommended_immediate_actions: ['Isolate affected animal in a dry recovery stall.'],
            created_at: new Date(Date.now() - 86400000).toISOString()
          }
        ]
      };
    }
  },

  /**
   * Runs genuine neural network inference on an uploaded or dataset image.
   * Calls trained PyTorch MobileNetV2 Task A classifier.
   */
  async predictReal(imageId) {
    return await apiClient.post('/detection/predict-real', { image_id: imageId });
  },

  /**
   * Runs Task B Species Guard classifier on image.
   */
  async validateSpecies(imageId) {
    return await apiClient.post('/detection/validate-species', { image_id: imageId });
  },

  /**
   * Retrieves Task C Biometric Muzzle Registry.
   */
  async getMuzzleRegistry() {
    return await apiClient.get('/detection/muzzle-registry');
  },
};

export default detectionService;

