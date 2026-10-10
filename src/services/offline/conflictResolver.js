/**
 * AniCare AI — Conflict Resolver
 * Milestone 10: Clinical Authority & Client Conflict Resolution Strategy
 */

import { CONFLICT_STRATEGIES } from './syncTypes';

export const conflictResolver = {
  /**
   * Evaluates an entity conflict and returns the authoritative resolution strategy.
   */
  resolveStrategy(entityType, actionType) {
    // Clinical authority is strictly SERVER-authoritative
    if (
      entityType === 'veterinary_case' ||
      entityType === 'treatment' ||
      entityType === 'vaccination' ||
      entityType === 'outbreak' ||
      actionType === 'ACKNOWLEDGE_FOLLOW_UP'
    ) {
      return {
        strategy: CONFLICT_STRATEGIES.SERVER_WINS,
        isClinical: true,
        explanation_en: 'This record was modified by a veterinary officer. The server-approved clinical diagnosis takes precedence.',
        explanation_hi: 'यह विवरण पशु चिकित्सक द्वारा अद्यतित किया गया है। डॉक्टर द्वारा स्वीकृत रिकॉर्ड मान्य रहेगा।',
      };
    }

    // Farmer observations: preserve both
    if (entityType === 'health_record' || actionType === 'CREATE_HEALTH_OBSERVATION') {
      return {
        strategy: CONFLICT_STRATEGIES.KEEP_BOTH,
        isClinical: false,
        explanation_en: 'Both farmer observation and server telemetry are preserved.',
        explanation_hi: 'किसान द्वारा दर्ज अवलोकन और सर्वर विवरण दोनों सुरक्षित रखे गए हैं।',
      };
    }

    // Default to server wins
    return {
      strategy: CONFLICT_STRATEGIES.SERVER_WINS,
      isClinical: false,
      explanation_en: 'Server version retained to preserve data consistency.',
      explanation_hi: 'डेटा निरंतरता बनाए रखने के लिए सर्वर का रिकॉर्ड रखा गया है।',
    };
  },
};
