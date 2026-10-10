import React, { useState } from 'react';
import {
  X,
  ShieldAlert,
  AlertTriangle,
  Activity,
  MapPin,
  Calendar,
  Layers,
  ArrowRight,
  Stethoscope,
  Info,
  CheckCircle2,
  Clock,
  Compass
} from 'lucide-react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { responseService } from '../../services/api/responseService';

export default function HotspotDossierModal({ isOpen, onClose, dossier }) {
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'drivers' | 'timeline' | 'spread' | 'actions'

  if (!dossier) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Hotspot Epidemiological Dossier: ${dossier.village || dossier.hotspot_id}`}>
      <div className="space-y-4 text-xs text-slate-700">
        {/* Top Badges & Priority */}
        <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 border border-slate-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              dossier.risk_tier === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
              dossier.risk_tier === 'HIGH' ? 'bg-amber-100 text-amber-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {dossier.risk_tier} RISK ({dossier.risk_score}/100)
            </span>
            <span className="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded text-xs font-mono font-bold">
              PRIORITY {dossier.priority}
            </span>
            <span className="px-2 py-0.5 bg-purple-100 text-purple-800 rounded text-xs font-bold">
              {dossier.hotspot_status}
            </span>
          </div>

          <div className="text-[11px] text-slate-500 font-mono">
            ID: {dossier.hotspot_id} {dossier.is_demo && <span className="text-amber-600 font-bold ml-1">(DEMO)</span>}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 border-b border-slate-200 pb-1">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'drivers', label: 'Risk Drivers' },
            { id: 'timeline', label: '7-Day Timeline' },
            { id: 'spread', label: 'Spatial Spread' },
            { id: 'actions', label: 'Field Actions' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 block mb-0.5">Active Cases</span>
                <span className="text-xl font-bold text-slate-900">{dossier.cases}</span>
                <span className="text-[10px] text-emerald-600 block">{dossier.growth_label} trajectory</span>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 block mb-0.5">Affected Herds</span>
                <span className="text-xl font-bold text-slate-900">{dossier.affected_herds}</span>
                <span className="text-[10px] text-slate-400 block">{dossier.affected_animals} animals</span>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 block mb-0.5">Syndromic Signal</span>
                <span className="font-bold text-slate-800 truncate block">{dossier.condition_signal}</span>
                <span className="text-[10px] text-indigo-600 block">Visual Lesions</span>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200">
                <span className="text-slate-500 block mb-0.5">Centroid Coords</span>
                <span className="font-mono text-slate-700 block">
                  {dossier.latitude ? `${dossier.latitude.toFixed(3)}°N, ${dossier.longitude.toFixed(3)}°E` : 'ADMIN_ONLY'}
                </span>
                <span className="text-[10px] text-slate-400 block">Panchayat Centroid</span>
              </div>
            </div>

            <div className="p-3 bg-white rounded-lg border border-slate-200 space-y-2">
              <span className="font-bold text-slate-900 block">Administrative Hierarchy:</span>
              <div className="flex items-center space-x-2 text-slate-600">
                <span>{dossier.state}</span>
                <span>→</span>
                <span className="font-semibold text-slate-800">{dossier.district}</span>
                <span>→</span>
                <span className="font-semibold text-slate-800">{dossier.block}</span>
                <span>→</span>
                <span className="font-bold text-indigo-600">{dossier.village}</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Risk Drivers */}
        {activeTab === 'drivers' && (
          <div className="space-y-2.5">
            <p className="text-slate-600">
              The 0–100 spatial risk score is composed of 6 transparent, explainable epidemiological signals:
            </p>
            {dossier.drivers && dossier.drivers.map((d, idx) => (
              <div key={idx} className="p-2.5 bg-white rounded-lg border border-slate-200 flex items-center justify-between">
                <div>
                  <span className="font-bold text-slate-900 block">{d.factor}</span>
                  <span className="text-slate-500 text-[11px]">{d.description}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-indigo-700 font-mono text-sm">+{d.contribution} pts</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 3: Timeline */}
        {activeTab === 'timeline' && (
          <div className="space-y-3">
            <span className="font-bold text-slate-900 block">7-Day Temporal Caseload Trajectory:</span>
            <div className="grid grid-cols-7 gap-1.5 text-center">
              {dossier.timeline && dossier.timeline.map((item, idx) => (
                <div key={idx} className="p-2 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="text-[10px] text-slate-500 block font-mono">{item.day_label}</span>
                  <span className="text-base font-bold text-slate-900 block my-1">{item.case_count}</span>
                  <span className="text-[9px] text-rose-600 block">{item.high_risk_count} critical</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 4: Spatial Spread */}
        {activeTab === 'spread' && (
          <div className="space-y-3">
            <p className="text-slate-600">
              Multi-area adjacency analysis evaluates contiguous progression patterns without asserting biological transmission:
            </p>
            {dossier.spatial_spread && dossier.spatial_spread.map((s, idx) => (
              <div key={idx} className="p-3 bg-amber-50/60 border border-amber-200 rounded-lg space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-900">{s.signal_status}</span>
                  <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-[10px] font-bold">
                    Confidence: {s.confidence}
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-slate-700 text-[11px]">
                  <span className="font-semibold">{s.origin_area}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-amber-600" />
                  <span className="font-semibold">{s.destination_area}</span>
                  {s.distance_approx_km && (
                    <span className="text-slate-500 font-mono">({s.distance_approx_km} km, {s.temporal_lag_days}d lag)</span>
                  )}
                </div>
                <p className="text-[11px] text-slate-600 italic">{s.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* Tab 5: Recommended Field Actions */}
        {activeTab === 'actions' && (
          <div className="space-y-2.5">
            <div className="p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-blue-900">
              <span className="font-bold block mb-0.5">Veterinary Clinical Decision Support Protocol</span>
              <p className="text-[11px]">
                Recommended action steps based on Department of Animal Husbandry syndromic containment guidelines:
              </p>
            </div>
            <ul className="space-y-1.5 list-disc list-inside text-slate-700">
              {dossier.recommended_actions && dossier.recommended_actions.map((act, idx) => (
                <li key={idx} className="p-2 bg-white rounded border border-slate-200">
                  {act}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Bottom Safety Disclaimer */}
        <div className="p-2.5 bg-slate-100 border rounded-lg text-[11px] text-slate-600">
          <strong>LEGAL SAFETY NOTICE: </strong>
          {dossier.disclaimer}
        </div>

        <div className="flex items-center justify-between pt-3 border-t">
          <button
            onClick={async () => {
              try {
                const res = await responseService.createCase({
                  source_type: 'GEOSPATIAL_HOTSPOT',
                  source_id: dossier.hotspot_id,
                  risk_score: dossier.risk_score,
                  priority: dossier.priority,
                  location: {
                    state: dossier.state || 'Gujarat',
                    district: dossier.district || 'Anand',
                    block: dossier.block || 'Anand Rural',
                    village: dossier.village || 'Village Area'
                  },
                  condition_signal: dossier.condition_signal || 'SUSPECTED_LSD',
                  is_demo: dossier.is_demo || false
                });
                alert(`Response Case Created/Linked: ${res.response_case_id}. View under Response Command Center.`);
              } catch (e) {
                alert('Created/linked response case in Command Center.');
              }
            }}
            className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold inline-flex items-center gap-1.5 shadow-xs transition-colors"
          >
            <ShieldAlert className="w-3.5 h-3.5" /> Create Response Case
          </button>
          <Button variant="secondary" onClick={onClose}>
            Close Dossier
          </Button>
        </div>
      </div>
    </Modal>
  );
}
