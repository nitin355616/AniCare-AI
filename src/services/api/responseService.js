import apiClient from './client';

export const responseService = {
  /**
   * Fetches real-time operational response KPIs.
   */
  async getStats() {
    try {
      return await apiClient.get('/response/stats');
    } catch (error) {
      console.warn('Backend response stats unavailable, fallback:', error.message);
      return {
        active_alerts: 4,
        p1_cases: 2,
        pending_investigations: 3,
        field_visits_today: 5,
        samples_awaiting_lab: 2,
        department_reviews: 1,
        overdue_actions: 0,
        resolved_cases: 8,
        disclaimer: 'AI-generated risk signals support prioritization. Field investigation and authorized veterinary/department decisions remain human-controlled.'
      };
    }
  },

  /**
   * Lists prioritized response alerts with deduplication.
   */
  async getAlerts(priority = null, status = null) {
    const params = new URLSearchParams();
    if (priority && priority !== 'ALL') params.append('priority', priority);
    if (status && status !== 'ALL') params.append('status', status);

    try {
      return await apiClient.get(`/response/alerts?${params.toString()}`);
    } catch (error) {
      console.warn('Backend response alerts unavailable, fallback:', error.message);
      return [
        {
          alert_id: 'ALT-DEMO-001',
          response_case_id: 'RESP-DEMO-001',
          source_type: 'GEOSPATIAL_HOTSPOT',
          source_id: 'GEO-DEMO-001',
          alert_type: 'P1_OPERATIONAL_ALERT',
          priority: 'P1',
          severity: 'CRITICAL',
          status: 'ACTIVE',
          title: 'P1 Critical Health Alert — Suspected LSD',
          message: 'Operational P1 alert generated for Demo Village A, Demo Block A. Risk score: 86.0. Urgent field verification recommended.',
          location: { state: 'Gujarat', district: 'Anand', block: 'Anand Rural', village: 'Demo Village A', latitude: 22.5800, longitude: 72.9500 },
          condition_signal: 'SUSPECTED_LSD',
          risk_score: 86.0,
          created_at: new Date(Date.now() - 3600000).toISOString(),
          escalation_history: [],
          is_demo: true
        },
        {
          alert_id: 'ALT-DEMO-002',
          response_case_id: 'RESP-DEMO-002',
          source_type: 'GEOSPATIAL_HOTSPOT',
          source_id: 'GEO-DEMO-002',
          alert_type: 'P2_OPERATIONAL_ALERT',
          priority: 'P2',
          severity: 'HIGH',
          status: 'ACKNOWLEDGED',
          title: 'P2 High Priority Alert — Suspected FMD',
          message: 'Operational P2 alert generated for Demo Village B. Risk score: 68.0.',
          location: { state: 'Gujarat', district: 'Anand', block: 'Anand Rural', village: 'Demo Village B', latitude: 22.5950, longitude: 72.9650 },
          condition_signal: 'SUSPECTED_FMD',
          risk_score: 68.0,
          created_at: new Date(Date.now() - 7200000).toISOString(),
          acknowledged_at: new Date(Date.now() - 5400000).toISOString(),
          acknowledged_by: 'Dr. V. Sharma (DVO)',
          escalation_history: [],
          is_demo: true
        }
      ];
    }
  },

  /**
   * Acknowledges an active operational alert.
   */
  async acknowledgeAlert(alertId, comment = 'Alert acknowledged by field authority') {
    return await apiClient.post(`/response/alerts/${alertId}/acknowledge`, { comment });
  },

  /**
   * Escalates an alert priority (e.g. P3 -> P1).
   */
  async escalateAlert(alertId, toPriority, reason) {
    return await apiClient.post(`/response/alerts/${alertId}/escalate`, {
      to_priority: toPriority,
      reason
    });
  },

  /**
   * Lists operational response cases.
   */
  async getCases(priority = null, status = null, district = null) {
    const params = new URLSearchParams();
    if (priority && priority !== 'ALL') params.append('priority', priority);
    if (status && status !== 'ALL') params.append('status', status);
    if (district && district !== 'ALL') params.append('district', district);

    try {
      const res = await apiClient.get(`/response/cases?${params.toString()}`);
      return res.items || res;
    } catch (error) {
      console.warn('Backend cases unavailable, fallback:', error.message);
      return [
        {
          response_case_id: 'RESP-DEMO-001',
          source_type: 'GEOSPATIAL_HOTSPOT',
          source_id: 'GEO-DEMO-001',
          risk_score: 86.0,
          priority: 'P1',
          severity: 'CRITICAL',
          status: 'FIELD_INVESTIGATION',
          location: { state: 'Gujarat', district: 'Anand', block: 'Anand Rural', village: 'Demo Village A', latitude: 22.5800, longitude: 72.9500 },
          condition_signal: 'SUSPECTED_LSD',
          created_at: new Date(Date.now() - 7200000).toISOString(),
          updated_at: new Date(Date.now() - 1800000).toISOString(),
          assigned_to: 'VET-OFFICER-01',
          assigned_officer_name: 'Dr. R. K. Patel (Field Officer)',
          is_demo: true,
          disclaimer: 'AI-generated risk signals support prioritization. Field investigation and authorized veterinary/department decisions remain human-controlled.',
          alerts: [],
          investigations: [
            {
              investigation_id: 'INV-DEMO-01',
              response_case_id: 'RESP-DEMO-001',
              visit_date: new Date(Date.now() - 3600000).toISOString(),
              officer_id: 'VET-OFFICER-01',
              officer_name: 'Dr. R. K. Patel',
              animals_observed: 18,
              symptoms_observed: ['Circumscribed nodular cutaneous lesions', 'Pyrexia 40.8C'],
              affected_animals: 3,
              herds_observed: 2,
              biosecurity_observations: 'Open paddock, isolation recommended immediately.',
              mortality: 0,
              photos: [],
              evidence: [],
              created_at: new Date(Date.now() - 3600000).toISOString()
            }
          ],
          samples: [
            {
              sample_id: 'SMP-DEMO-01',
              response_case_id: 'RESP-DEMO-001',
              sample_type: 'SWAB',
              collected_at: new Date(Date.now() - 3000000).toISOString(),
              collected_by: 'VET-OFFICER-01',
              collected_by_name: 'Dr. R. K. Patel',
              purpose: 'Real-time RT-PCR diagnostic verification',
              status: 'LAB_PENDING',
              created_at: new Date(Date.now() - 3000000).toISOString()
            }
          ],
          department_reviews: [],
          actions: [],
          follow_ups: [],
          timeline: [
            { event_id: 'EVT-01', response_case_id: 'RESP-DEMO-001', event_type: 'RISK_DETECTED', timestamp: new Date(Date.now() - 7200000).toISOString(), actor: 'Geospatial Radar', role: 'system', description: 'Hotspot detected in Demo Village A' },
            { event_id: 'EVT-02', response_case_id: 'RESP-DEMO-001', event_type: 'ALERT_CREATED', timestamp: new Date(Date.now() - 7100000).toISOString(), actor: 'Alert Engine', role: 'system', description: 'P1 Critical operational alert generated' },
            { event_id: 'EVT-03', response_case_id: 'RESP-DEMO-001', event_type: 'ALERT_ACKNOWLEDGED', timestamp: new Date(Date.now() - 6500000).toISOString(), actor: 'Dr. V. Sharma', role: 'veterinarian', description: 'Alert acknowledged' },
            { event_id: 'EVT-04', response_case_id: 'RESP-DEMO-001', event_type: 'INVESTIGATION_ASSIGNED', timestamp: new Date(Date.now() - 6000000).toISOString(), actor: 'Dr. V. Sharma', role: 'veterinarian', description: 'Assigned to Dr. R. K. Patel' },
            { event_id: 'EVT-05', response_case_id: 'RESP-DEMO-001', event_type: 'FIELD_INVESTIGATION', timestamp: new Date(Date.now() - 3600000).toISOString(), actor: 'Dr. R. K. Patel', role: 'field_officer', description: 'Field visit recorded: 18 animals examined, 3 affected.' }
          ],
          sla_metrics: {
            time_to_acknowledge_minutes: 10.0,
            time_to_assign_minutes: 8.3,
            time_to_field_visit_minutes: 40.0,
            time_to_sample_minutes: 50.0,
            time_to_lab_result_minutes: null,
            time_to_resolution_minutes: null,
            is_p1_ack_overdue: false,
            is_p1_investigation_overdue: false
          }
        }
      ];
    }
  },

  /**
   * Fetches single response case dossier.
   */
  async getCase(caseId) {
    try {
      return await apiClient.get(`/response/cases/${caseId}`);
    } catch (error) {
      console.warn('Backend case dossier unavailable, fallback:', error.message);
      const cases = await this.getCases();
      return cases.find(c => c.response_case_id === caseId) || cases[0];
    }
  },

  /**
   * Creates or links a response case from upstream hotspot or outbreak.
   */
  async createCase(caseData) {
    return await apiClient.post('/response/cases', caseData);
  },

  /**
   * Assigns an authorized field officer to conduct on-site investigation.
   */
  async assignInvestigation(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/assign`, data);
  },

  /**
   * Records on-site physical investigation findings.
   */
  async recordInvestigation(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/investigation`, data);
  },

  /**
   * Collects biological specimen for laboratory testing.
   */
  async createSample(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/samples`, data);
  },

  /**
   * Records diagnostic laboratory assay result (POSITIVE, NEGATIVE, INCONCLUSIVE, INVALID).
   */
  async recordLabResult(sampleId, data) {
    return await apiClient.post(`/response/samples/${sampleId}/result`, data);
  },

  /**
   * Records departmental review and strategic directive.
   */
  async recordDepartmentReview(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/department-review`, data);
  },

  /**
   * Authorizes containment or biosecurity intervention.
   */
  async authorizeAction(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/authorize-action`, data);
  },

  /**
   * Records veterinary follow-up inspection.
   */
  async recordFollowUp(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/follow-up`, data);
  },

  /**
   * Closes response case with official remarks.
   */
  async closeCase(caseId, data) {
    return await apiClient.post(`/response/cases/${caseId}/close`, data);
  },

  /**
   * Lists notification outbox messages.
   */
  async getNotifications(channel = null) {
    const params = new URLSearchParams();
    if (channel) params.append('channel', channel);
    try {
      return await apiClient.get(`/response/notifications?${params.toString()}`);
    } catch (error) {
      console.warn('Backend notifications unavailable, fallback:', error.message);
      return [
        {
          notification_id: 'NTF-001',
          channel: 'IN_APP',
          recipient_type: 'AUTHORIZED_OFFICER',
          recipient_target: 'district_command_center',
          template: 'CRITICAL_ALERT',
          title: 'P1 Livestock Health Alert — Suspected LSD',
          message: 'Operational P1 alert generated for Demo Village A.',
          status: 'DELIVERED',
          provider: 'AniCare Realtime Event Bus',
          created_at: new Date(Date.now() - 3600000).toISOString()
        },
        {
          notification_id: 'NTF-002',
          channel: 'SMS',
          recipient_type: 'OFFICER',
          recipient_target: '+919876543210',
          template: 'ALERT_SMS',
          title: 'SMS Alert Notice',
          message: 'AniCare AI Alert: High-priority signal detected in Demo Village A.',
          status: 'NOT_CONFIGURED',
          provider: null,
          created_at: new Date(Date.now() - 3600000).toISOString()
        }
      ];
    }
  },

  /**
   * Queues an operational notification.
   */
  async queueNotification(data) {
    return await apiClient.post('/response/notifications', data);
  },

  /**
   * Seeds demo data.
   */
  async seedDemoData() {
    return await apiClient.post('/response/seed-demo');
  },

  /**
   * Executes the 14-step SIH Hackathon Field Response workflow scenario.
   */
  async runDemoScenario() {
    return await apiClient.post('/response/demo/run-scenario');
  }
};

export default responseService;
