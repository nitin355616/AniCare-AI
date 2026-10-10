import React, { useState, useEffect } from 'react';
import {
  Radio,
  ShieldAlert,
  AlertTriangle,
  Activity,
  MapPin,
  Clock,
  CheckCircle2,
  UserCheck,
  RefreshCw,
  Search,
  Filter,
  Eye,
  FileText,
  Calendar,
  TrendingUp,
  Compass,
  ChevronRight,
  Info,
  Shield,
  Layers,
  Sparkles,
  X,
  Stethoscope,
  Send,
  Building
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import OutbreakGeoMap from '../components/charts/OutbreakGeoMap';
import { outbreakService } from '../services/api/outbreakService';
import { CURRENT_USER } from '../data/mockData';

export default function OutbreakIntelligence() {
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [stats, setStats] = useState({
    active_clusters: 0,
    surveillance_alerts: 0,
    red_alerts: 0,
    routine_events: 0,
    resolved_events: 0,
    false_alerts: 0,
    total_events: 0,
    affected_animals_count: 0,
    affected_villages_count: 0,
    affected_districts_count: 0
  });
  const [trends, setTrends] = useState([]);
  const [selectedTrendPeriod, setSelectedTrendPeriod] = useState(7);
  const [hotspots, setHotspots] = useState([]);
  const [outbreaks, setOutbreaks] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [tierFilter, setTierFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('events'); // 'events' | 'hotspots' | 'geomap'

  // Modal State
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [modalTab, setModalTab] = useState('overview'); // 'overview' | 'animals' | 'timeline' | 'investigation' | 'audit'

  // Investigation & Assignment Form State
  const [assigneeName, setAssigneeName] = useState('');
  const [assignNotes, setAssignNotes] = useState('');
  const [statusActionNotes, setStatusActionNotes] = useState('');
  const [investigationForm, setInvestigationForm] = useState({
    field_visit_date: new Date().toISOString().split('T')[0],
    animals_examined: 5,
    clinical_observations: '',
    suspected_condition: 'Suspected Lumpy Skin Disease',
    laboratory_test_required: true,
    laboratory_test_status: 'SAMPLES_SENT',
    preventive_actions: ['Isolate cohort cattle in recovery pens', 'Restrict inter-village grazing'],
    biosecurity_actions: ['Daily 2% sodium hypochlorite spraying', 'Vector repellent application'],
    farmer_guidance: 'Avoid communal water troughs and immediately notify veterinary post if fever exceeds 104°F.',
    follow_up_date: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
    investigation_notes: 'Initial on-site clinical assessment confirms cutaneous nodules matching early stage.',
    investigating_officer: CURRENT_USER.name || 'Dr. Rajesh Patel',
    officer_license: 'VET-GJ-REG-2024-88402'
  });

  const [notification, setNotification] = useState(null);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 5000);
  };

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [statsRes, trendsRes, hotspotsRes, listRes] = await Promise.all([
        outbreakService.getStats(),
        outbreakService.getTrends(),
        outbreakService.getHotspots(),
        outbreakService.getOutbreaks({
          status: statusFilter !== 'ALL' ? statusFilter : undefined,
          risk_tier: tierFilter !== 'ALL' ? tierFilter : undefined
        })
      ]);

      setStats(statsRes || {});
      setTrends(trendsRes.windows || []);
      setHotspots(hotspotsRes.hotspots || []);
      setOutbreaks(listRes.data || []);
    } catch (err) {
      console.error('Failed to load outbreak intelligence data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [statusFilter, tierFilter]);

  const handleScanNow = async () => {
    setScanning(true);
    try {
      const res = await outbreakService.scanClusters({ window_days: selectedTrendPeriod });
      showNotification(`Scan complete: ${res.new_clusters_detected || 0} new clusters detected, ${res.existing_clusters_updated || 0} updated.`, 'success');
      await loadAllData();
    } catch (err) {
      showNotification(`Scan failed: ${err.message}`, 'error');
    } finally {
      setScanning(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    try {
      const demoRes = await outbreakService.seedDemoOutbreak();
      showNotification(`SIH 2026 Demo Cluster seeded successfully in Village Demo-A (${demoRes.event_id}).`, 'success');
      await loadAllData();
    } catch (err) {
      showNotification(`Seeding error: ${err.message}`, 'error');
    } finally {
      setSeeding(false);
    }
  };

  const handleSelectEvent = async (eventId) => {
    try {
      const full = await outbreakService.getOutbreak(eventId);
      setSelectedEvent(full);
      setModalTab('overview');
      setAssigneeName(full.assigned_veterinary_officer || '');
    } catch (err) {
      showNotification(`Failed to load event dossier: ${err.message}`, 'error');
    }
  };

  const handleAssignOfficer = async () => {
    if (!assigneeName.trim()) {
      showNotification('Please enter a Veterinary Officer name.', 'error');
      return;
    }
    try {
      const updated = await outbreakService.assignOfficer(selectedEvent.event_id, {
        officer_name: assigneeName,
        notes: assignNotes
      });
      setSelectedEvent(updated);
      showNotification(`Assigned to ${assigneeName}. Status updated to VETERINARY_INVESTIGATION.`, 'success');
      await loadAllData();
    } catch (err) {
      showNotification(`Assignment failed: ${err.message}`, 'error');
    }
  };

  const handleStatusTransition = async (newStatus) => {
    try {
      const updated = await outbreakService.updateStatus(selectedEvent.event_id, {
        new_status: newStatus,
        notes: statusActionNotes
      });
      setSelectedEvent(updated);
      setStatusActionNotes('');
      showNotification(`Outbreak status transitioned to ${newStatus}.`, 'success');
      await loadAllData();
    } catch (err) {
      showNotification(`Status change failed: ${err.message}`, 'error');
    }
  };

  const handleSubmitInvestigation = async () => {
    if (!investigationForm.clinical_observations.trim()) {
      showNotification('Please enter clinical observations.', 'error');
      return;
    }
    try {
      const updated = await outbreakService.submitInvestigation(selectedEvent.event_id, investigationForm);
      setSelectedEvent(updated);
      showNotification('Certified field investigation recorded. Case moved to ACTION_RECOMMENDED.', 'success');
      await loadAllData();
    } catch (err) {
      showNotification(`Investigation submission failed: ${err.message}`, 'error');
    }
  };

  const filteredOutbreaks = outbreaks.filter((o) => {
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchLoc = `${o.location?.village} ${o.location?.district} ${o.location?.block}`.toLowerCase().includes(q);
      const matchCond = (o.condition || '').toLowerCase().includes(q);
      const matchId = (o.event_id || '').toLowerCase().includes(q);
      return matchLoc || matchCond || matchId;
    }
    return true;
  });

  const activeTrendData = trends.find((t) => t.days === selectedTrendPeriod) || trends[0] || {};

  return (
    <div className="space-y-6">
      {/* Statutory Notification Toast */}
      {notification && (
        <div
          className={`p-4 rounded-xl text-sm font-medium flex items-center justify-between border shadow-lg transition-all ${
            notification.type === 'error'
              ? 'bg-rose-50 text-rose-800 border-rose-200'
              : 'bg-emerald-50 text-emerald-800 border-emerald-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === 'error' ? <AlertTriangle className="w-5 h-5 text-rose-600" /> : <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
            <span>{notification.msg}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-slate-700">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 bottom-0 w-96 bg-gradient-to-l from-indigo-900/30 to-transparent pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-rose-500/20 border border-rose-500/40 rounded-xl text-rose-400">
                <Radio className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-2xl font-bold tracking-tight">Outbreak Intelligence & Syndromic Surveillance</h1>
                  <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] font-mono uppercase px-2 py-0.5 rounded-full font-bold">
                    Gov Early-Warning System
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  State Animal Husbandry Department (DAHD) & ICAR-NIVEDI Interoperable Epizootic Radar
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSeedDemo}
              disabled={seeding}
              className="bg-slate-800 text-amber-300 border-amber-500/40 hover:bg-slate-700 text-xs flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              {seeding ? 'Seeding Demo...' : 'Seed SIH Demo Outbreak'}
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={handleScanNow}
              disabled={scanning}
              className="bg-rose-600 hover:bg-rose-700 text-white text-xs flex items-center gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
              {scanning ? 'Analyzing Caseload...' : 'Scan For Clusters Now'}
            </Button>
          </div>
        </div>

        {/* Disclaimer Bar */}
        <div className="mt-5 pt-4 border-t border-slate-800 flex items-start gap-2 text-[11px] text-slate-400 leading-relaxed">
          <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <span>
            <strong className="text-slate-300">STATUTORY VETERINARY NOTICE:</strong> AI clustering provides early-warning decision support and syndromic telemetry tracking. It does not represent an officially confirmed disease outbreak without certified on-site clinical examination and regulatory laboratory confirmation (RT-PCR/ELISA).
          </span>
        </div>
      </div>

      {/* KPI Metrics Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Clusters</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-900">{stats.active_clusters || 0}</span>
            <Badge variant={stats.active_clusters > 0 ? 'warning' : 'neutral'} pulse={stats.active_clusters > 0}>
              Live
            </Badge>
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Under Surveillance</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-sm flex flex-col justify-between bg-gradient-to-br from-rose-50/40 to-white">
          <span className="text-xs font-semibold text-rose-700 uppercase tracking-wider">Red Alerts</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-rose-600">{stats.red_alerts || 0}</span>
            <Badge variant="danger" pulse={stats.red_alerts > 0}>
              Tier 3
            </Badge>
          </div>
          <span className="text-[11px] text-rose-500/80 mt-1">Emergency DVO Action</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-amber-200 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-amber-700 uppercase tracking-wider">Surveillance</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-amber-600">{stats.surveillance_alerts || 0}</span>
            <Badge variant="warning">Tier 2</Badge>
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Priority Monitoring</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Affected Animals</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-800">{stats.affected_animals_count || 0}</span>
            <Activity className="w-4 h-4 text-indigo-500" />
          </div>
          <span className="text-[11px] text-slate-400 mt-1">In Clustered Sectors</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Affected Villages</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-800">{stats.affected_villages_count || 0}</span>
            <MapPin className="w-4 h-4 text-emerald-500" />
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Containment Focus</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Affected Districts</span>
          <div className="flex items-baseline justify-between mt-2">
            <span className="text-2xl font-bold text-slate-800">{stats.affected_districts_count || 0}</span>
            <Building className="w-4 h-4 text-slate-500" />
          </div>
          <span className="text-[11px] text-slate-400 mt-1">Revenue Jurisdictions</span>
        </div>
      </div>

      {/* Main Tabs Navigation */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('events')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'events'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            Active Cluster Events ({outbreaks.length})
          </button>

          <button
            onClick={() => setActiveTab('hotspots')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'hotspots'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <MapPin className="w-4 h-4" />
            Geographic Hotspots ({hotspots.length})
          </button>

          <button
            onClick={() => setActiveTab('geomap')}
            className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
              activeTab === 'geomap'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <Compass className="w-4 h-4" />
            Satellite & Radar Basin
          </button>
        </div>

        {/* Temporal Window Toggle */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <span className="text-[11px] font-semibold text-slate-500 px-2 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" /> Window:
          </span>
          {[7, 14, 30].map((w) => (
            <button
              key={w}
              onClick={() => setSelectedTrendPeriod(w)}
              className={`px-2.5 py-1 text-xs rounded font-bold transition-all ${
                selectedTrendPeriod === w ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {w}D
            </button>
          ))}
        </div>
      </div>

      {/* Temporal Trend Banner */}
      <div className="bg-indigo-50/70 border border-indigo-100 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600 text-white rounded-lg">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-indigo-950">
                Surveillance Trajectory: {activeTrendData.period_label || 'Current Period'}
              </span>
              <span className="text-xs font-bold text-rose-600 bg-rose-100 px-2 py-0.5 rounded-full">
                {activeTrendData.trend_percentage >= 0 ? `+${activeTrendData.trend_percentage}%` : `${activeTrendData.trend_percentage}%`} vs Previous
              </span>
            </div>
            <p className="text-xs text-indigo-700/80">
              Total Caseload: <strong>{activeTrendData.total_cases || 0}</strong> • High-Risk: <strong>{activeTrendData.high_risk_cases || 0}</strong> • Critical: <strong>{activeTrendData.critical_cases || 0}</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <div className="text-right">
            <span className="text-slate-500 block text-[11px]">Possible Clusters</span>
            <span className="font-bold text-slate-800">{activeTrendData.possible_clusters || 0}</span>
          </div>
          <div className="text-right">
            <span className="text-slate-500 block text-[11px]">Suspected Outbreaks</span>
            <span className="font-bold text-rose-600">{activeTrendData.suspected_outbreaks || 0}</span>
          </div>
          <div className="text-right">
            <span className="text-slate-500 block text-[11px]">Resolved</span>
            <span className="font-bold text-emerald-600">{activeTrendData.resolved_events || 0}</span>
          </div>
        </div>
      </div>

      {/* TAB CONTENT 1: OUTBREAK EVENTS LIST */}
      {activeTab === 'events' && (
        <div className="space-y-4">
          {/* Filters Bar */}
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 w-full md:w-auto">
              <div className="relative flex-1 md:w-64">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search village, district, condition..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none"
              >
                <option value="ALL">All Statuses</option>
                <option value="DETECTED">DETECTED</option>
                <option value="UNDER_SURVEILLANCE">UNDER_SURVEILLANCE</option>
                <option value="VETERINARY_INVESTIGATION">VET_INVESTIGATION</option>
                <option value="ACTION_RECOMMENDED">ACTION_RECOMMENDED</option>
                <option value="MONITORING">MONITORING</option>
                <option value="RESOLVED">RESOLVED</option>
                <option value="FALSE_ALERT">FALSE_ALERT</option>
              </select>

              <select
                value={tierFilter}
                onChange={(e) => setTierFilter(e.target.value)}
                className="text-xs border border-slate-300 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 focus:outline-none"
              >
                <option value="ALL">All Risk Tiers</option>
                <option value="TIER_3_RED_ALERT">Tier 3 (Red Alert)</option>
                <option value="TIER_2_SURVEILLANCE">Tier 2 (Surveillance)</option>
                <option value="TIER_1_ROUTINE">Tier 1 (Routine)</option>
              </select>
            </div>

            <div className="text-xs text-slate-500">
              Showing <strong>{filteredOutbreaks.length}</strong> active outbreak dossiers
            </div>
          </div>

          {/* Outbreak Events Table */}
          <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider">
                    <th className="py-3 px-4">Event ID</th>
                    <th className="py-3 px-4">Jurisdiction</th>
                    <th className="py-3 px-4">Suspected Condition</th>
                    <th className="py-3 px-4">Caseload</th>
                    <th className="py-3 px-4">Risk Score</th>
                    <th className="py-3 px-4">Risk Tier</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Assigned Vet</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredOutbreaks.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="py-12 text-center text-slate-400">
                        No active outbreak clusters match the selected criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredOutbreaks.map((ev) => {
                      const isRed = ev.risk_tier === 'TIER_3_RED_ALERT';
                      const isSurv = ev.risk_tier === 'TIER_2_SURVEILLANCE';

                      return (
                        <tr key={ev.event_id} className="hover:bg-slate-50/80 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-slate-900">
                            <div className="flex items-center gap-1.5">
                              {ev.event_id}
                              {ev.is_demo && (
                                <span className="bg-amber-100 text-amber-800 text-[10px] font-sans px-1.5 py-0.2 rounded font-bold">
                                  DEMO
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="font-semibold text-slate-900">{ev.location?.village || 'Unknown Village'}</div>
                            <div className="text-[11px] text-slate-500">
                              {ev.location?.block}, {ev.location?.district}
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <div className="font-medium text-slate-800">{ev.disease_signal}</div>
                            <div className="text-[10px] text-slate-400">Signal: Visual + Syndromic</div>
                          </td>
                          <td className="py-3 px-4 font-bold text-slate-800">
                            {ev.case_count} head
                            {ev.trend_percentage > 0 && (
                              <span className="block text-[10px] text-rose-600">+{ev.trend_percentage}% growth</span>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-1.5">
                              <div className="w-10 bg-slate-100 h-2 rounded-full overflow-hidden">
                                <div
                                  className={`h-full ${
                                    isRed ? 'bg-rose-500' : isSurv ? 'bg-amber-500' : 'bg-emerald-500'
                                  }`}
                                  style={{ width: `${ev.risk_score}%` }}
                                />
                              </div>
                              <span className="font-mono font-bold">{ev.risk_score}/100</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">
                            <Badge
                              variant={isRed ? 'danger' : isSurv ? 'warning' : 'success'}
                              pulse={isRed}
                            >
                              {isRed ? 'Red Alert' : isSurv ? 'Surveillance' : 'Routine'}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-mono text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-semibold border border-slate-200">
                              {ev.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-600">
                            {ev.assigned_veterinary_officer ? (
                              <div className="flex items-center gap-1 text-slate-800 font-medium">
                                <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                                {ev.assigned_veterinary_officer}
                              </div>
                            ) : (
                              <span className="text-slate-400 italic">Unassigned</span>
                            )}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleSelectEvent(ev.event_id)}
                              className="text-xs"
                            >
                              Open Dossier
                            </Button>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: GEOGRAPHIC HOTSPOTS */}
      {activeTab === 'hotspots' && (
        <div className="space-y-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-sm flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Administrative Jurisdictional Hotspots</h3>
              <p className="text-xs text-slate-500">
                Ranked by syndromic caseload density across District &rarr; Block &rarr; Village
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs bg-rose-50 text-rose-700 border border-rose-200 px-2 py-0.5 rounded font-bold">
                High Priority: {hotspots.filter((h) => h.hotspot_level === 'HOTSPOT_HIGH').length}
              </span>
              <span className="text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded font-bold">
                Medium: {hotspots.filter((h) => h.hotspot_level === 'HOTSPOT_MEDIUM').length}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {hotspots.map((h, idx) => {
              const isHigh = h.hotspot_level === 'HOTSPOT_HIGH';
              const isMed = h.hotspot_level === 'HOTSPOT_MEDIUM';

              return (
                <div
                  key={`${h.village}-${idx}`}
                  className={`bg-white rounded-xl p-5 border shadow-sm flex flex-col justify-between ${
                    isHigh ? 'border-rose-300 ring-1 ring-rose-200' : isMed ? 'border-amber-200' : 'border-slate-200'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-mono text-slate-500 uppercase">{h.district} District</span>
                      <Badge variant={isHigh ? 'danger' : isMed ? 'warning' : 'success'} pulse={isHigh}>
                        {isHigh ? 'High Hotspot' : isMed ? 'Medium Hotspot' : 'Low Hotspot'}
                      </Badge>
                    </div>

                    <h4 className="text-base font-bold text-slate-900">{h.village}</h4>
                    <p className="text-xs text-slate-500">{h.block} • {h.state}</p>

                    <div className="mt-4 space-y-2 text-xs">
                      <div className="flex justify-between py-1 border-b border-slate-100">
                        <span className="text-slate-500">Active Caseload:</span>
                        <span className="font-bold text-slate-800">{h.case_count} Animals</span>
                      </div>
                      <div className="flex justify-between py-1 border-b border-slate-100">
                        <span className="text-slate-500">High / Critical Cases:</span>
                        <span className="font-bold text-rose-600">{h.high_critical_count} Animals</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span className="text-slate-500">Dominant Condition:</span>
                        <span className="font-semibold text-slate-700">{h.dominant_condition}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-slate-500">Active Clusters: <strong>{h.active_clusters}</strong></span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSearchQuery(h.village);
                        setActiveTab('events');
                      }}
                      className="text-xs"
                    >
                      Filter Cases &rarr;
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB CONTENT 3: SATELITTE RADAR MAP BASIN */}
      {activeTab === 'geomap' && (
        <div className="space-y-4">
          <OutbreakGeoMap />
        </div>
      )}

      {/* COMPREHENSIVE OUTBREAK DOSSIER MODAL */}
      {selectedEvent && (
        <Modal
          isOpen={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
          title={`Outbreak Intelligence Dossier: ${selectedEvent.event_id}`}
          size="2xl"
        >
          <div className="space-y-5">
            {/* Modal Header Metadata */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold text-slate-900">{selectedEvent.condition}</span>
                  {selectedEvent.is_demo && (
                    <span className="bg-amber-100 text-amber-800 border border-amber-300 text-xs px-2 py-0.5 rounded font-bold">
                      DEMO DATA
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Location: <strong>{selectedEvent.location?.village}</strong>, {selectedEvent.location?.block}, {selectedEvent.location?.district}, {selectedEvent.location?.state}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Badge
                  variant={
                    selectedEvent.risk_tier === 'TIER_3_RED_ALERT'
                      ? 'danger'
                      : selectedEvent.risk_tier === 'TIER_2_SURVEILLANCE'
                      ? 'warning'
                      : 'success'
                  }
                  pulse={selectedEvent.risk_tier === 'TIER_3_RED_ALERT'}
                >
                  {selectedEvent.risk_tier}
                </Badge>
                <span className="text-xs font-mono bg-white text-slate-800 border px-2.5 py-1 rounded-lg font-bold">
                  Status: {selectedEvent.status}
                </span>
              </div>
            </div>

            {/* Modal Sub-Tabs */}
            <div className="flex border-b border-slate-200 space-x-4 text-xs font-semibold">
              <button
                onClick={() => setModalTab('overview')}
                className={`pb-2.5 transition-all ${
                  modalTab === 'overview'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                1. Risk & Breakdown
              </button>
              <button
                onClick={() => setModalTab('animals')}
                className={`pb-2.5 transition-all ${
                  modalTab === 'animals'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                2. Affected Livestock ({selectedEvent.case_count})
              </button>
              <button
                onClick={() => setModalTab('timeline')}
                className={`pb-2.5 transition-all ${
                  modalTab === 'timeline'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                3. Early Warning Timeline
              </button>
              <button
                onClick={() => setModalTab('investigation')}
                className={`pb-2.5 transition-all ${
                  modalTab === 'investigation'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                4. Field Investigation
              </button>
              <button
                onClick={() => setModalTab('audit')}
                className={`pb-2.5 transition-all ${
                  modalTab === 'audit'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                5. Audit Trail ({selectedEvent.audit_trail?.length || 0})
              </button>
            </div>

            {/* SUB-TAB 1: RISK & TRIGGER BREAKDOWN */}
            {modalTab === 'overview' && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-900 text-white p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
                    <div>
                      <span className="text-xs font-semibold text-slate-400 uppercase">Explainable Risk Score</span>
                      <div className="text-3xl font-bold font-mono text-rose-400 mt-2">
                        {selectedEvent.risk_score} / 100
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-400 mt-3">
                      Window: {selectedEvent.window_start} to {selectedEvent.window_end}
                    </span>
                  </div>

                  <div className="md:col-span-2 bg-white p-4 rounded-xl border border-slate-200">
                    <span className="text-xs font-bold text-slate-800 block mb-2">
                      Scoring Signal Triggers:
                    </span>
                    <ul className="space-y-1.5 text-xs text-slate-600">
                      {selectedEvent.trigger_reasons?.map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-rose-500 flex-shrink-0 mt-0.5" />
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Precautionary Recommendations */}
                <div className="bg-amber-50/60 border border-amber-200 p-4 rounded-xl space-y-2">
                  <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
                    <Shield className="w-4 h-4 text-amber-700" />
                    Recommended Biosecurity Containment Protocol:
                  </div>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-amber-800">
                    {selectedEvent.recommended_actions?.map((act, idx) => (
                      <li key={idx} className="flex items-start gap-1.5 bg-white/70 p-2 rounded border border-amber-200/50">
                        <ChevronRight className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* SUB-TAB 2: AFFECTED LIVESTOCK */}
            {modalTab === 'animals' && (
              <div className="space-y-3">
                <p className="text-xs text-slate-500">
                  Individual livestock cohort members tracked within this epidemiological cluster:
                </p>
                <div className="max-h-60 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
                  {selectedEvent.animal_ids?.map((aid, i) => (
                    <div key={aid} className="p-3 flex items-center justify-between text-xs hover:bg-slate-50">
                      <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-full bg-slate-100 flex items-center justify-center font-bold text-slate-700">
                          {i + 1}
                        </div>
                        <div>
                          <span className="font-bold text-slate-900">{aid}</span>
                          <span className="block text-[11px] text-slate-500">Species: Cattle (Bovine)</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="danger">High Risk Signal</Badge>
                        <span className="text-[11px] font-mono text-slate-400">Suspected LSD</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* SUB-TAB 3: EARLY WARNING TIMELINE */}
            {modalTab === 'timeline' && (
              <div className="space-y-4">
                <p className="text-xs text-slate-500">
                  Visual syndromic telemetry escalation progression for SIH 2026 jury verification:
                </p>
                <div className="relative pl-6 border-l-2 border-indigo-200 space-y-6 my-4 text-xs">
                  <div className="relative">
                    <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-indigo-500 ring-4 ring-indigo-100" />
                    <span className="font-mono text-slate-400 block text-[11px]">Day 1 — Sentinel Event</span>
                    <span className="font-bold text-slate-900 block">First animal telemetry abnormality detected</span>
                    <span className="text-slate-500">Visual nodular papules logged on animal in North Shed bay.</span>
                  </div>

                  <div className="relative">
                    <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-indigo-500 ring-4 ring-indigo-100" />
                    <span className="font-mono text-slate-400 block text-[11px]">Day 3 — Cohort Transmission</span>
                    <span className="font-bold text-slate-900 block">Second animal manifests fever spike & rumination drop</span>
                    <span className="text-slate-500">Ruminal IoT bolus reports 104.2°F temperature.</span>
                  </div>

                  <div className="relative">
                    <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-amber-500 ring-4 ring-amber-100" />
                    <span className="font-mono text-slate-400 block text-[11px]">Day 5 — Spatial Cluster Detected</span>
                    <span className="font-bold text-amber-700 block">POSSIBLE_CLUSTER & Tier 2 Surveillance Triggered</span>
                    <span className="text-slate-500">ANI-NET spatial cluster algorithm verifies 3 cases in same village within 7 days.</span>
                  </div>

                  <div className="relative">
                    <span className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-rose-600 ring-4 ring-rose-100" />
                    <span className="font-mono text-slate-400 block text-[11px]">Day 7 — Red Alert Escalation</span>
                    <span className="font-bold text-rose-700 block">SUSPECTED_OUTBREAK & Tier 3 Red Alert Issued</span>
                    <span className="text-slate-500">Caseload reaches 5 head (+250% surge). Emergency DVO containment advisory broadcast.</span>
                  </div>
                </div>
              </div>
            )}

            {/* SUB-TAB 4: FIELD INVESTIGATION & ACTIONS */}
            {modalTab === 'investigation' && (
              <div className="space-y-5">
                {/* Assignment Box */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                      <Stethoscope className="w-4 h-4 text-indigo-600" />
                      Veterinary Officer Assignment
                    </span>
                    {selectedEvent.assigned_veterinary_officer && (
                      <span className="text-xs text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded font-bold">
                        Assigned to {selectedEvent.assigned_veterinary_officer}
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      type="text"
                      placeholder="Doctor Name (e.g. Dr. Rajesh Patel)"
                      value={assigneeName}
                      onChange={(e) => setAssigneeName(e.target.value)}
                      className="text-xs border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <input
                      type="text"
                      placeholder="Assignment memo or instructions..."
                      value={assignNotes}
                      onChange={(e) => setAssignNotes(e.target.value)}
                      className="text-xs border border-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleAssignOfficer}
                      className="text-xs"
                    >
                      Assign Officer & Transition
                    </Button>
                  </div>
                </div>

                {/* Certified Investigation Filing Form */}
                <div className="p-4 bg-white border border-slate-200 rounded-xl space-y-4">
                  <span className="text-xs font-bold text-slate-800 block">
                    Record Certified Clinical Field Inspection:
                  </span>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-500 mb-1">Field Visit Date</label>
                      <input
                        type="date"
                        value={investigationForm.field_visit_date}
                        onChange={(e) => setInvestigationForm({ ...investigationForm, field_visit_date: e.target.value })}
                        className="w-full border rounded-lg p-2 text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-500 mb-1">Livestock Heads Examined</label>
                      <input
                        type="number"
                        min="1"
                        value={investigationForm.animals_examined}
                        onChange={(e) => setInvestigationForm({ ...investigationForm, animals_examined: parseInt(e.target.value) || 1 })}
                        className="w-full border rounded-lg p-2 text-xs"
                      />
                    </div>
                  </div>

                  <div className="text-xs">
                    <label className="block text-slate-500 mb-1">Clinical Observations & Physical Staging</label>
                    <textarea
                      rows="2"
                      placeholder="Describe nodular lesion diameter, mucous ulceration, rectal temperature..."
                      value={investigationForm.clinical_observations}
                      onChange={(e) => setInvestigationForm({ ...investigationForm, clinical_observations: e.target.value })}
                      className="w-full border rounded-lg p-2 text-xs"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-slate-500 mb-1">Laboratory Assay Required?</label>
                      <select
                        value={investigationForm.laboratory_test_required ? 'yes' : 'no'}
                        onChange={(e) => setInvestigationForm({ ...investigationForm, laboratory_test_required: e.target.value === 'yes' })}
                        className="w-full border rounded-lg p-2 text-xs"
                      >
                        <option value="yes">Yes (Mandatory RT-PCR / Serology)</option>
                        <option value="no">No</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-slate-500 mb-1">Laboratory Test Status</label>
                      <select
                        value={investigationForm.laboratory_test_status}
                        onChange={(e) => setInvestigationForm({ ...investigationForm, laboratory_test_status: e.target.value })}
                        className="w-full border rounded-lg p-2 text-xs"
                      >
                        <option value="NOT_REQUIRED">NOT_REQUIRED</option>
                        <option value="SAMPLES_SENT">SAMPLES_SENT (In Transit to State Lab)</option>
                        <option value="AWAITING_RESULTS">AWAITING_RESULTS</option>
                        <option value="CONFIRMED_POSITIVE">CONFIRMED_POSITIVE</option>
                        <option value="CONFIRMED_NEGATIVE">CONFIRMED_NEGATIVE</option>
                      </select>
                    </div>
                  </div>

                  <div className="text-xs">
                    <label className="block text-slate-500 mb-1">Farmer & Herd Owner Guidance</label>
                    <textarea
                      rows="2"
                      value={investigationForm.farmer_guidance}
                      onChange={(e) => setInvestigationForm({ ...investigationForm, farmer_guidance: e.target.value })}
                      className="w-full border rounded-lg p-2 text-xs"
                    />
                  </div>

                  <Button
                    variant="primary"
                    size="sm"
                    onClick={handleSubmitInvestigation}
                    className="w-full text-xs"
                  >
                    Submit Field Investigation & Recommend Action
                  </Button>
                </div>

                {/* Status Transition Bar */}
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <span className="text-xs font-bold text-slate-800 block">Operational Status Action:</span>
                  <div className="flex flex-wrap items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleStatusTransition('MONITORING')}
                      className="text-xs"
                    >
                      Move to MONITORING
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleStatusTransition('RESOLVED')}
                      className="text-xs text-emerald-700 border-emerald-300 hover:bg-emerald-50"
                    >
                      Resolve Cluster (RESOLVED)
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleStatusTransition('FALSE_ALERT')}
                      className="text-xs text-rose-700 border-rose-300 hover:bg-rose-50"
                    >
                      Mark FALSE_ALERT
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* SUB-TAB 5: IMMUTABLE AUDIT TRAIL */}
            {modalTab === 'audit' && (
              <div className="space-y-3">
                <p className="text-xs text-slate-500">
                  Immutable chronological log of all epidemiological and administrative events:
                </p>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {selectedEvent.audit_trail?.map((aud, i) => (
                    <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-indigo-700">{aud.action}</span>
                        <span className="text-[11px] text-slate-400 font-mono">{aud.timestamp?.split('T')[0]}</span>
                      </div>
                      <p className="text-slate-600">{aud.notes}</p>
                      <div className="text-[10px] text-slate-400">
                        Actor: <strong>{aud.actor_id}</strong> ({aud.actor_role})
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-3 border-t border-slate-200 flex justify-end">
              <Button variant="outline" size="sm" onClick={() => setSelectedEvent(null)}>
                Close Dossier
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
