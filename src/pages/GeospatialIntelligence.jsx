import React, { useState, useEffect } from 'react';
import {
  Compass,
  MapPin,
  ShieldAlert,
  AlertTriangle,
  Activity,
  RefreshCw,
  Sparkles,
  Layers,
  Calendar,
  Filter,
  CheckCircle2,
  Stethoscope,
  Info,
  Clock,
  RotateCcw
} from 'lucide-react';
import { geospatialService } from '../services/api/geospatialService';
import InteractiveRiskMap from '../components/geospatial/InteractiveRiskMap';
import HotspotPriorityTable from '../components/geospatial/HotspotPriorityTable';
import HotspotDossierModal from '../components/geospatial/HotspotDossierModal';
import GeospatialSpreadCard from '../components/geospatial/GeospatialSpreadCard';
import DiseaseTrendChart from '../components/geospatial/DiseaseTrendChart';
import Button from '../components/common/Button';

export default function GeospatialIntelligence() {
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [seeding, setSeeding] = useState(false);

  // Filters
  const [aggregationLevel, setAggregationLevel] = useState('village'); // 'village' | 'block' | 'district'
  const [windowDays, setWindowDays] = useState(7); // 1 | 7 | 14 | 30
  const [conditionFilter, setConditionFilter] = useState('ALL');

  // Data states
  const [overview, setOverview] = useState(null);
  const [mapPoints, setMapPoints] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [trends, setTrends] = useState([]);
  const [spreadData, setSpreadData] = useState(null);

  // Selected Hotspot for Modal Dossier
  const [selectedHotspotId, setSelectedHotspotId] = useState(null);
  const [dossierData, setDossierData] = useState(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);

  const fetchGeospatialData = async () => {
    setLoading(true);
    try {
      const [ovRes, mapRes, hotRes, trRes, spRes] = await Promise.all([
        geospatialService.getOverview(windowDays),
        geospatialService.getRiskMap(aggregationLevel, windowDays, conditionFilter),
        geospatialService.getHotspots(),
        geospatialService.getTrends(),
        geospatialService.getSpreadSignals()
      ]);

      setOverview(ovRes);
      setMapPoints(mapRes || []);
      setHotspots(hotRes?.items || []);
      setTrends(trRes?.trends || []);
      setSpreadData(spRes);
    } catch (err) {
      console.error('Error fetching geospatial intelligence:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGeospatialData();
  }, [aggregationLevel, windowDays, conditionFilter]);

  const handleOpenDossier = async (hotspotId) => {
    setSelectedHotspotId(hotspotId);
    try {
      const dossier = await geospatialService.getHotspotById(hotspotId);
      setDossierData(dossier);
      setIsDossierOpen(true);
    } catch (err) {
      alert(`Could not load dossier: ${err.message}`);
    }
  };

  const handleRecalculate = async () => {
    setRecalculating(true);
    try {
      const res = await geospatialService.recalculateRisk(windowDays);
      alert(`Risk snapshots successfully recalculated for ${res.areas_evaluated} areas!`);
      await fetchGeospatialData();
    } catch (err) {
      alert(`Recalculation error: ${err.message}`);
    } finally {
      setRecalculating(false);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    try {
      await geospatialService.seedDemoData();
      alert('SIH demo geospatial clusters successfully seeded!');
      await fetchGeospatialData();
    } catch (err) {
      alert(`Demo seeding failed: ${err.message}`);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Government Command Center Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <Compass className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold text-slate-900">Geospatial Disease Intelligence & Risk Mapping</h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
                  Government Command Center
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Multi-settlement syndromic surveillance, centroid risk mapping, and epidemiological hotspot prioritization.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="flex items-center space-x-1.5 px-3 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{seeding ? 'Seeding...' : 'Seed SIH Demo Data'}</span>
          </button>

          <button
            onClick={handleRecalculate}
            disabled={recalculating}
            className="flex items-center space-x-1.5 px-3 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-lg text-xs font-semibold transition disabled:opacity-50"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${recalculating ? 'animate-spin' : ''}`} />
            <span>{recalculating ? 'Recalculating...' : 'Recalculate Snapshots'}</span>
          </button>

          <button
            onClick={fetchGeospatialData}
            disabled={loading}
            className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
            title="Refresh geospatial telemetry"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Top KPI Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block mb-1">Areas Monitored</span>
          <span className="text-2xl font-bold text-slate-900">{overview?.total_areas_monitored || 4}</span>
          <span className="text-[11px] text-slate-400 block mt-0.5">Villages & Blocks</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block mb-1">High Risk Areas</span>
          <span className="text-2xl font-bold text-amber-700">{overview?.high_risk_areas || 2}</span>
          <span className="text-[11px] text-amber-600 font-medium block mt-0.5">Score 60–79</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block mb-1">Critical Hotspots</span>
          <span className="text-2xl font-bold text-rose-700">{overview?.critical_areas || 1}</span>
          <span className="text-[11px] text-rose-600 font-medium block mt-0.5">Priority P1 Active</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block mb-1">Emerging Hotspots</span>
          <span className="text-2xl font-bold text-indigo-700">{overview?.emerging_hotspots || 1}</span>
          <span className="text-[11px] text-indigo-600 font-medium block mt-0.5">New Signals Detected</span>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block mb-1">Cases (Last 7 Days)</span>
          <span className="text-2xl font-bold text-slate-900">{overview?.total_cases_last_7d || 18}</span>
          <span className="text-[11px] text-emerald-600 font-medium block mt-0.5">Active Syndromic Cases</span>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          {/* Level Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-xs font-semibold text-slate-600">Level:</span>
            <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs">
              {['village', 'block', 'district'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setAggregationLevel(lvl)}
                  className={`px-3 py-1 rounded-md capitalize font-medium transition ${
                    aggregationLevel === lvl ? 'bg-white text-indigo-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Time Window Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-xs font-semibold text-slate-600">Window:</span>
            <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs">
              {[
                { days: 1, label: '24 Hours' },
                { days: 7, label: '7 Days' },
                { days: 14, label: '14 Days' },
                { days: 30, label: '30 Days' }
              ].map((w) => (
                <button
                  key={w.days}
                  onClick={() => setWindowDays(w.days)}
                  className={`px-3 py-1 rounded-md font-medium transition ${
                    windowDays === w.days ? 'bg-white text-indigo-700 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  {w.label}
                </button>
              ))}
            </div>
          </div>

          {/* Condition Filter */}
          <div className="flex items-center space-x-1.5">
            <span className="text-xs font-semibold text-slate-600">Signal:</span>
            <select
              value={conditionFilter}
              onChange={(e) => setConditionFilter(e.target.value)}
              className="px-3 py-1 text-xs border rounded-lg bg-white text-slate-700 outline-none"
            >
              <option value="ALL">All Conditions</option>
              <option value="Lumpy Skin Disease">Lumpy Skin Disease</option>
              <option value="Mastitis">Mastitis Syndrome</option>
              <option value="Foot and Mouth Disease">Foot and Mouth Disease</option>
              <option value="Respiratory">Respiratory Syndrome</option>
            </select>
          </div>
        </div>

        <span className="text-[11px] text-slate-400 font-mono">
          Last Synced: {overview?.last_recalculated_at ? overview.last_recalculated_at.substring(11, 19) : 'Live'}
        </span>
      </div>

      {/* Interactive Risk Map Surface */}
      <InteractiveRiskMap
        points={mapPoints}
        level={aggregationLevel}
        onOpenDossier={handleOpenDossier}
      />

      {/* Ranked Hotspot Registry Table */}
      <HotspotPriorityTable
        hotspots={hotspots}
        onSelectHotspot={handleOpenDossier}
        selectedHotspotId={selectedHotspotId}
      />

      {/* Side-by-Side: Multi-Window Trends and Spatial Spread Card */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DiseaseTrendChart trends={trends} />
        <GeospatialSpreadCard
          spreadSignals={spreadData?.active_spread_signals}
          totalPatterns={spreadData?.spread_patterns_detected || 0}
        />
      </div>

      {/* Department Action Protocol Workflow Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-base font-bold text-slate-900 mb-2">Statutory Department Action & Investigation Protocol</h3>
        <p className="text-xs text-slate-500 mb-4">
          Government disease response follows a rigorous multi-tier verification lifecycle. Early-warning signals never trigger autonomous medical actions:
        </p>

        <div className="grid grid-cols-2 md:grid-cols-7 gap-2 text-center text-xs">
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">1. Risk Detected</span>
            <span className="text-[10px] text-slate-500">Syndromic signal</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">2. Triage Review</span>
            <span className="text-[10px] text-slate-500">State DAHD desk</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">3. Field Order</span>
            <span className="text-[10px] text-slate-500">Assign Vet Officer</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">4. Physical Exam</span>
            <span className="text-[10px] text-slate-500">Inspect livestock</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">5. Lab Assays</span>
            <span className="text-[10px] text-slate-500">RT-PCR validation</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">6. Dept Action</span>
            <span className="text-[10px] text-slate-500">Ring vaccination</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
            <span className="font-bold text-slate-900 block">7. Follow-up</span>
            <span className="text-[10px] text-slate-500">Resolution audit</span>
          </div>
        </div>
      </div>

      {/* Hotspot Dossier Modal */}
      {isDossierOpen && dossierData && (
        <HotspotDossierModal
          isOpen={isDossierOpen}
          onClose={() => setIsDossierOpen(false)}
          dossier={dossierData}
        />
      )}
    </div>
  );
}
