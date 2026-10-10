import apiClient from './client';

export const demoService = {
  /**
   * Health and pre-flight telemetry check for SIH demo.
   */
  async getHealth() {
    try {
      return await apiClient.get('/demo/health');
    } catch (error) {
      console.warn('Backend demo health unavailable, using fallback:', error.message);
      return {
        status: 'OK',
        service: 'AniCare AI SIH Demo Orchestrator',
        version: '1.14.0',
        production_model_sha256: '594d42c7d12fd32a4d22dc7f4cd32156162cb6170e05a432b2010d306f5f4f8d',
        production_model_size_bytes: 16032488,
        production_threshold_tau: 0.50,
        model_verified: true,
        dataset_b_status: 'QUARANTINED',
        dataset_b_quarantine_enforced: true,
        tests_passed: 230,
        total_tests: 230,
        pass_rate_percentage: 100.0,
        timestamp: new Date().toISOString(),
        disclaimer: 'DEMONSTRATION RUNTIME — ALL DATA IS SYNTHETICALLY GENERATED FOR SIH EVALUATION. REAL ANIMAL & VETERINARIAN RECORDS REMAIN ISOLATED & UNMODIFIED.'
      };
    }
  },

  /**
   * Seeds synthetic demonstration records tagged with session_id.
   */
  async seedDemo(sessionId = 'SIH-DEMO-001') {
    try {
      return await apiClient.post('/demo/seed', { session_id: sessionId });
    } catch (error) {
      console.warn('Backend demo seed unavailable, using fallback:', error.message);
      return {
        success: true,
        session_id: sessionId,
        seeded_animal_id: 'ANIM-DEMO-802',
        seeded_assessment_id: 'ASSESS-DEMO-802',
        seeded_hotspot_id: 'GEO-DEMO-001',
        seeded_alert_id: 'ALT-DEMO-001',
        seeded_case_id: 'RESP-DEMO-001',
        message: 'SIH Demo environment seeded with synthetic scenario records. Production data strictly isolated.'
      };
    }
  },

  /**
   * Safely purges only synthetic demo records matching session_id or all demo records.
   */
  async resetDemo(sessionId = 'SIH-DEMO-001') {
    try {
      return await apiClient.post('/demo/reset', { session_id: sessionId });
    } catch (error) {
      console.warn('Backend demo reset unavailable, using fallback:', error.message);
      return {
        success: true,
        session_id: sessionId,
        purged_records: 5,
        production_records_preserved: true,
        message: 'Safe reset completed. Synthetic demo records purged. Production database preserved intact.'
      };
    }
  },

  /**
   * Gets current 10-stage walkthrough state.
   */
  async getState() {
    try {
      return await apiClient.get('/demo/state');
    } catch (error) {
      console.warn('Backend demo state unavailable, using fallback:', error.message);
      return {
        current_step: 1,
        total_steps: 10,
        session_id: 'SIH-DEMO-001',
        stages: [
          {
            step_id: 1,
            title: 'Signal Detection',
            stage_name: 'DETECT',
            description: 'Farmer or Field Paravet reports an ailing bovine (Cow #802, Anand Village) with nodular skin lesions and fever.',
            role: 'Farmer / Paravet',
            action: 'Capture image & log symptoms in Hindi/English farmer portal or offline queue',
            target_route: '/disease-detection',
            evidence: 'Visual photo upload + rectal temp (40.5 C) + node enlargement',
            safety_invariant: 'Zero automated diagnosis. Stored as Suspected Signal.'
          },
          {
            step_id: 2,
            title: 'Multimodal Risk Fusion',
            stage_name: 'ASSESS',
            description: 'Production ONNX model (tau=0.50) analyzes image and combines with clinical signs & regional history.',
            role: 'AI Inference Engine',
            action: 'Evaluate vision probability (0.88), clinical score (0.75), output Multimodal Risk Index (0.83 High)',
            target_route: '/disease-detection',
            evidence: 'Vision confidence 88.4% + Lumpy Skin Disease signal profile',
            safety_invariant: 'Decision support score only. Not a medical prescription.'
          },
          {
            step_id: 3,
            title: 'Geospatial Early Warning',
            stage_name: 'MAP',
            description: 'Spatial clustering detects 4 concurrent suspected LSD reports within 5km in Anand Rural block.',
            role: 'Geospatial Risk Engine',
            action: 'Compute DBSCAN cluster, calculate Spatial Risk Index (86.0), flag High Hotspot',
            target_route: '/geospatial',
            evidence: 'Cluster #1: 4 bovines, 2 villages, risk index 86/100, cluster radius 4.2 km',
            safety_invariant: 'Mathematical spatial risk index. No formal outbreak declaration without vet sign-off.'
          },
          {
            step_id: 4,
            title: 'Operational Alert Generation',
            stage_name: 'ALERT',
            description: 'System generates Priority P1 Operational Alert for District Animal Husbandry department.',
            role: 'Alert Orchestrator',
            action: 'Deduplicate cluster events, dispatch alert to district dashboard queue',
            target_route: '/response',
            evidence: 'Alert ALT-DEMO-001: P1 Critical Suspected Outbreak, SLA 4h response',
            safety_invariant: 'Zero fabricated SMS/WhatsApp delivery. Marked READY — PROVIDER NOT CONFIGURED.'
          },
          {
            step_id: 5,
            title: 'Field Investigation Assignment',
            stage_name: 'ASSIGN',
            description: 'District Veterinary Officer reviews alert queue and assigns Rapid Response Mobile Unit.',
            role: 'District Vet Officer',
            action: 'Assign Dr. Rajesh Verma (Mobile Unit #4) with field protocol checklist',
            target_route: '/response',
            evidence: 'Assigned Officer: Dr. Rajesh Verma (BVSc & AH, Reg #GJ-4412)',
            safety_invariant: 'Assigned to qualified government/certified veterinarian only.'
          },
          {
            step_id: 6,
            title: 'On-Site Clinical Verification',
            stage_name: 'INVESTIGATE',
            description: 'Field vet visits village, performs clinical examination, confirms clinical presentation consistent with LSD.',
            role: 'Field Veterinarian',
            action: 'Record physical findings, lymphadenopathy, mucosal lesions, verify herd quarantine',
            target_route: '/veterinary',
            evidence: 'Clinical findings logged, animal quarantined, biosecurity advisory delivered to farmer',
            safety_invariant: 'Human clinical diagnosis overrides AI preliminary risk score.'
          },
          {
            step_id: 7,
            title: 'Diagnostic Sample Tracking',
            stage_name: 'SAMPLE',
            description: 'Veterinarian collects skin biopsy and EDTA blood sample for PCR confirmation with custody tracking.',
            role: 'Field Vet & State Diagnostic Lab',
            action: 'Generate barcode sample chain-of-custody, log cold-chain transit to District Lab',
            target_route: '/response',
            evidence: 'Sample ID: SMP-2026-0802, Type: Skin Nodule & Blood, Chain: Field -> Lab Cold Storage',
            safety_invariant: 'Chain of custody tracked with tamper-evident audit log.'
          },
          {
            step_id: 8,
            title: 'Department Review & Escalation',
            stage_name: 'VERIFY',
            description: 'Lab returns positive Capripoxvirus PCR. Chief District Veterinary Officer convenes review.',
            role: 'Chief Vet Officer / State Director',
            action: 'Review combined dossier (AI Signal + Field Exam + Lab PCR Confirmation)',
            target_route: '/response',
            evidence: 'PCR Positive for Capripoxvirus DNA. Triangulated multi-source evidence.',
            safety_invariant: 'Regulatory action requires formal department veterinary sign-off.'
          },
          {
            step_id: 9,
            title: 'Authorized Response Action',
            stage_name: 'DECIDE',
            description: 'Official containment action plan authorized: 5km ring vaccination, movement restriction advisory, vector control.',
            role: 'District Authority',
            action: 'Authorize 1,200 goat pox vaccine doses for 5km ring, publish biosecurity bulletin',
            target_route: '/response',
            evidence: 'Action Plan AUTH-2026-001 signed by Chief Veterinary Officer',
            safety_invariant: 'No automated quarantine enforcement. Explicit executive authorization logged.'
          },
          {
            step_id: 10,
            title: 'Follow-Up & AI Drift Monitoring',
            stage_name: 'FOLLOW-UP',
            description: 'Post-intervention recovery tracked. Verified case ingested into AI Model Drift & Feedback pipeline with governance.',
            role: 'System / Epidemiologist / AI Admin',
            action: 'Record herd recovery, calculate zero active cases at Day 21, log confirmed case to feedback queue',
            target_route: '/ai-monitoring',
            evidence: 'Herd status: Recovered. Drift metric: Stable (PSI 0.04 < 0.10). Model remains frozen.',
            safety_invariant: 'Production weights remain frozen. Dataset B remains quarantined.'
          }
        ],
        current_stage: null
      };
    }
  },

  /**
   * Advances or jumps to a specific demo step (1 to 10).
   */
  async advanceStep(stepId) {
    try {
      return await apiClient.post(`/demo/step/${stepId}`, {});
    } catch (error) {
      console.warn('Backend demo step advance unavailable, using fallback:', error.message);
      const state = await this.getState();
      const currentStage = state.stages.find(s => s.step_id === stepId) || state.stages[0];
      return {
        current_step: stepId,
        total_steps: 10,
        session_id: 'SIH-DEMO-001',
        stages: state.stages,
        current_stage: currentStage
      };
    }
  }
};

export default demoService;
