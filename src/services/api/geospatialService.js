import apiClient from './client';

export const geospatialService = {
  /**
   * Fetches real-time executive geospatial surveillance KPIs.
   */
  async getOverview(days = 7) {
    try {
      return await apiClient.get(`/geospatial/overview?days=${days}`);
    } catch (error) {
      console.warn('Backend geospatial overview unavailable, fallback:', error.message);
      return {
        total_areas_monitored: 4,
        high_risk_areas: 2,
        critical_areas: 1,
        emerging_hotspots: 1,
        escalating_hotspots: 1,
        total_active_signals: 3,
        total_cases_last_7d: 18,
        observation_window_days: days,
        last_recalculated_at: new Date().toISOString(),
        disclaimer: 'Geospatial risk signals are intended for early-warning decision support. Disease outbreaks require field investigation and appropriate confirmatory veterinary/laboratory procedures.'
      };
    }
  },

  /**
   * Fetches privacy-safe map points for visualization.
   */
  async getRiskMap(level = 'village', days = 7, condition = null) {
    const params = new URLSearchParams({ level, days });
    if (condition && condition !== 'ALL') {
      params.append('condition', condition);
    }
    try {
      return await apiClient.get(`/geospatial/risk-map?${params.toString()}`);
    } catch (error) {
      console.warn('Backend risk map unavailable, fallback:', error.message);
      return [
        {
          point_id: 'GEO-DEMO-001',
          level,
          name: 'Demo Village A',
          state: 'Gujarat',
          district: 'Demo District',
          block: 'Demo Block A',
          village: 'Demo Village A',
          latitude: 22.5800,
          longitude: 72.9500,
          risk_score: 86,
          risk_tier: 'CRITICAL',
          priority: 'P1',
          hotspot_status: 'ESCALATING',
          condition_signal: 'Suspected Lumpy Skin Disease',
          active_cases: 12,
          growth_7d_pct: 200.0,
          growth_label: '+200.0%',
          affected_animals: 15,
          affected_herds: 5,
          last_updated: new Date().toISOString(),
          is_demo: true,
          disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
        },
        {
          point_id: 'GEO-DEMO-002',
          level,
          name: 'Demo Village B',
          state: 'Gujarat',
          district: 'Demo District',
          block: 'Demo Block A',
          village: 'Demo Village B',
          latitude: 22.5950,
          longitude: 72.9650,
          risk_score: 65,
          risk_tier: 'HIGH',
          priority: 'P2',
          hotspot_status: 'EMERGING',
          condition_signal: 'Suspected Lumpy Skin Disease',
          active_cases: 4,
          growth_7d_pct: 100.0,
          growth_label: 'NEW_SIGNAL',
          affected_animals: 5,
          affected_herds: 2,
          last_updated: new Date().toISOString(),
          is_demo: true,
          disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
        },
        {
          point_id: 'GEO-DEMO-003',
          level,
          name: 'Demo Village C',
          state: 'Gujarat',
          district: 'Demo District',
          block: 'Demo Block A',
          village: 'Demo Village C',
          latitude: 22.6200,
          longitude: 72.9300,
          risk_score: 42,
          risk_tier: 'MODERATE',
          priority: 'P3',
          hotspot_status: 'ACTIVE',
          condition_signal: 'Suspected Mastitis Syndrome',
          active_cases: 2,
          growth_7d_pct: 0.0,
          growth_label: '+0.0%',
          affected_animals: 2,
          affected_herds: 1,
          last_updated: new Date().toISOString(),
          is_demo: true,
          disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
        }
      ];
    }
  },

  /**
   * Fetches prioritized hotspots list.
   */
  async getHotspots(params = {}) {
    const query = new URLSearchParams(params).toString();
    try {
      return await apiClient.get(`/geospatial/hotspots${query ? `?${query}` : ''}`);
    } catch (error) {
      console.warn('Backend hotspots unavailable, fallback:', error.message);
      return {
        total: 3,
        critical_count: 1,
        high_count: 1,
        moderate_count: 1,
        items: [
          {
            hotspot_id: 'GEO-DEMO-001',
            state: 'Gujarat',
            district: 'Demo District',
            block: 'Demo Block A',
            village: 'Demo Village A',
            condition_signal: 'Suspected Lumpy Skin Disease',
            risk_score: 86,
            risk_tier: 'CRITICAL',
            priority: 'P1',
            hotspot_status: 'ESCALATING',
            cases: 12,
            growth_7d: 200.0,
            growth_label: '+200.0%',
            affected_animals: 15,
            affected_herds: 5,
            recommended_action: 'Veterinary field investigation recommended',
            last_updated: new Date().toISOString(),
            is_demo: true
          },
          {
            hotspot_id: 'GEO-DEMO-002',
            state: 'Gujarat',
            district: 'Demo District',
            block: 'Demo Block A',
            village: 'Demo Village B',
            condition_signal: 'Suspected Lumpy Skin Disease',
            risk_score: 65,
            risk_tier: 'HIGH',
            priority: 'P2',
            hotspot_status: 'EMERGING',
            cases: 4,
            growth_7d: 100.0,
            growth_label: 'NEW_SIGNAL',
            affected_animals: 5,
            affected_herds: 2,
            recommended_action: 'Field verification and vector control check',
            last_updated: new Date().toISOString(),
            is_demo: true
          },
          {
            hotspot_id: 'GEO-DEMO-003',
            state: 'Gujarat',
            district: 'Demo District',
            block: 'Demo Block A',
            village: 'Demo Village C',
            condition_signal: 'Suspected Mastitis Syndrome',
            risk_score: 42,
            risk_tier: 'MODERATE',
            priority: 'P3',
            hotspot_status: 'ACTIVE',
            cases: 2,
            growth_7d: 0.0,
            growth_label: '+0.0%',
            affected_animals: 2,
            affected_herds: 1,
            recommended_action: 'Routine CMT strip cup testing and hygiene review',
            last_updated: new Date().toISOString(),
            is_demo: true
          }
        ],
        disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
      };
    }
  },

  /**
   * Fetches detailed hotspot dossier by ID.
   */
  async getHotspotById(hotspotId) {
    try {
      return await apiClient.get(`/geospatial/hotspots/${hotspotId}`);
    } catch (error) {
      console.warn('Backend hotspot dossier unavailable, fallback:', error.message);
      return {
        hotspot_id: hotspotId,
        state: 'Gujarat',
        district: 'Demo District',
        block: 'Demo Block A',
        village: 'Demo Village A',
        latitude: 22.5800,
        longitude: 72.9500,
        condition_signal: 'Suspected Lumpy Skin Disease',
        risk_score: 86,
        risk_tier: 'CRITICAL',
        priority: 'P1',
        hotspot_status: 'ESCALATING',
        cases: 12,
        affected_animals: 15,
        affected_herds: 5,
        growth_7d: 200.0,
        growth_label: '+200.0%',
        drivers: [
          { factor: 'Case Burden', contribution: 25.0, description: '12 active cases identified in current window.' },
          { factor: 'Recent Growth', contribution: 20.0, description: 'Epidemiological trajectory (+200.0% vs previous period).' },
          { factor: 'Geographic Density', contribution: 20.0, description: 'Spatial concentration of livestock cases in the settlement.' },
          { factor: 'Clinical Severity', contribution: 11.0, description: '4 critical pyrexic cases with diffuse nodules.' },
          { factor: 'Disease Signal Strength', contribution: 9.0, description: 'Syndromic signal certainty (90.0% confidence).' },
          { factor: 'Affected Herds', contribution: 10.0, description: 'Multi-herd spread potential (5 distinct herds involved).' }
        ],
        timeline: [
          { day_label: 'Day -6', date_str: '2026-10-02', case_count: 2, high_risk_count: 1 },
          { day_label: 'Day -5', date_str: '2026-10-03', case_count: 3, high_risk_count: 2 },
          { day_label: 'Day -4', date_str: '2026-10-04', case_count: 5, high_risk_count: 3 },
          { day_label: 'Day -3', date_str: '2026-10-05', case_count: 7, high_risk_count: 4 },
          { day_label: 'Day -2', date_str: '2026-10-06', case_count: 9, high_risk_count: 5 },
          { day_label: 'Day -1', date_str: '2026-10-07', case_count: 11, high_risk_count: 6 },
          { day_label: 'Today', date_str: '2026-10-08', case_count: 12, high_risk_count: 7 }
        ],
        spatial_spread: [
          {
            signal_status: 'SPREAD_SIGNAL_DETECTED',
            confidence: 'MODERATE',
            origin_area: 'Demo Village A',
            destination_area: 'Demo Village B',
            distance_approx_km: 2.4,
            temporal_lag_days: 3,
            description: 'Geographical spread pattern detected between adjacent pastoral corridors; field verification recommended.'
          }
        ],
        recommended_actions: [
          'Mandate veterinary officer physical inspection within 24 hours.',
          'Inspect cattle herd for cutaneous nodular lesions, pyrexia, and lymphadenopathy.',
          'Advise immediate physical vector-control barriers (mosquito netting / fumigation).',
          'Collect EDTA blood and lesion scrapings for laboratory RT-PCR validation if indicated.',
          'Establish 3km syndromic surveillance perimeter around village boundary.'
        ],
        last_updated: new Date().toISOString(),
        is_demo: true,
        disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
      };
    }
  },

  /**
   * Fetches time-series risk trends across 24h, 7d, 14d, 30d.
   */
  async getTrends() {
    try {
      return await apiClient.get('/geospatial/trends');
    } catch (error) {
      console.warn('Backend trends unavailable, fallback:', error.message);
      return {
        trends: [
          { period_label: '24 Hours', days: 1, active_cases: 4, growth_pct: 33.3, critical_hotspots: 1, high_hotspots: 1 },
          { period_label: '7 Days', days: 7, active_cases: 18, growth_pct: 150.0, critical_hotspots: 1, high_hotspots: 1 },
          { period_label: '14 Days', days: 14, active_cases: 26, growth_pct: 85.0, critical_hotspots: 1, high_hotspots: 2 },
          { period_label: '30 Days', days: 30, active_cases: 42, growth_pct: 40.0, critical_hotspots: 1, high_hotspots: 2 }
        ],
        disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
      };
    }
  },

  /**
   * Fetches geographical spread signals across adjacent settlements.
   */
  async getSpreadSignals() {
    try {
      return await apiClient.get('/geospatial/spread');
    } catch (error) {
      console.warn('Backend spread signals unavailable, fallback:', error.message);
      return {
        spread_patterns_detected: 1,
        active_spread_signals: [
          {
            signal_status: 'SPREAD_SIGNAL_DETECTED',
            confidence: 'MODERATE',
            origin_area: 'Demo Village A (Escalating)',
            destination_area: 'Demo Village B (Emerging)',
            distance_approx_km: 2.4,
            temporal_lag_days: 3,
            description: 'Geographical risk pattern detected between adjacent pastoral corridors; field verification recommended.'
          }
        ],
        disclaimer: 'Geospatial risk signals are intended for early-warning decision support.'
      };
    }
  },

  /**
   * Triggers department-level risk recalculation.
   */
  async recalculateRisk(windowDays = 7) {
    return await apiClient.post('/geospatial/recalculate', { window_days: windowDays });
  },

  /**
   * Seeds synthetic SIH demo data clusters.
   */
  async seedDemoData() {
    return await apiClient.post('/geospatial/seed-demo', {});
  }
};
