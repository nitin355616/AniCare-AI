import React, { useState } from 'react';
import { MapPin, ShieldAlert, Radio, AlertTriangle, Compass, Eye, Layers, Info, CheckCircle2, ChevronRight, Activity } from 'lucide-react';
import Badge from '../common/Badge';

export default function InteractiveRiskMap({
  points = [],
  selectedPoint = null,
  onSelectPoint,
  onOpenDossier,
  level = 'village'
}) {
  const [activePoint, setActivePoint] = useState(selectedPoint || points[0] || null);
  const [viewMode, setViewMode] = useState('radar'); // 'radar' | 'grid'

  const handlePointClick = (pt) => {
    setActivePoint(pt);
    if (onSelectPoint) onSelectPoint(pt);
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'CRITICAL':
        return { bg: 'bg-rose-500', text: 'text-rose-700', border: 'border-rose-300', ping: 'bg-rose-400' };
      case 'HIGH':
        return { bg: 'bg-amber-500', text: 'text-amber-700', border: 'border-amber-300', ping: 'bg-amber-400' };
      case 'MODERATE':
        return { bg: 'bg-blue-500', text: 'text-blue-700', border: 'border-blue-300', ping: 'bg-blue-400' };
      default:
        return { bg: 'bg-emerald-500', text: 'text-emerald-700', border: 'border-emerald-300', ping: 'bg-emerald-400' };
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      {/* Top Map Surface Header */}
      <div className="p-4 bg-slate-900 text-white flex flex-wrap items-center justify-between gap-3 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Compass className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-bold text-sm">Privacy-Safe Geospatial Risk Surface</h3>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                Centroid-Aggregated
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Aggregated to administrative boundaries. Exact farmer and household coordinates are strictly protected.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex rounded-lg bg-slate-800 p-0.5 border border-slate-700 text-xs">
            <button
              onClick={() => setViewMode('radar')}
              className={`px-3 py-1 rounded-md font-medium transition ${viewMode === 'radar' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Coordinate Radar
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 rounded-md font-medium transition ${viewMode === 'grid' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
            >
              Spatial Cell Grid
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'radar' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3">
          {/* Visual Interactive Coordinate Surface */}
          <div className="lg:col-span-2 relative bg-slate-950 p-6 min-h-[420px] flex flex-col justify-between overflow-hidden">
            {/* Background gridlines & concentric radar circles */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:32px_32px] opacity-30 pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full border border-indigo-900/40 pointer-events-none" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full border border-indigo-800/30 pointer-events-none" />

            {/* Surface telemetry status */}
            <div className="relative z-10 flex items-center justify-between text-xs text-slate-400 font-mono">
              <div className="flex items-center space-x-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span>Active Surveillance Radar: {points.length} Monitored Sectors</span>
              </div>
              <span className="text-[11px] bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-indigo-400">
                Resolution: {level.toUpperCase()}
              </span>
            </div>

            {/* Interactive Centroid Nodes */}
            <div className="relative z-10 my-8 h-64 flex items-center justify-around px-4">
              {points.map((pt, idx) => {
                const isSelected = (activePoint && activePoint.point_id === pt.point_id) || idx === 0;
                const style = getTierColor(pt.risk_tier);
                const isCrit = pt.risk_tier === 'CRITICAL';
                const isHigh = pt.risk_tier === 'HIGH';

                return (
                  <button
                    key={pt.point_id || idx}
                    onClick={() => handlePointClick(pt)}
                    className={`relative flex flex-col items-center group transition-all transform hover:scale-110 focus:outline-none ${
                      isSelected ? 'scale-110 z-20' : 'opacity-85 z-10'
                    }`}
                  >
                    {/* Ping ripple for critical or high hotspots */}
                    {(isCrit || isHigh) && (
                      <span className="absolute -top-1 -right-1 flex h-4 w-4">
                        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${style.ping} opacity-75`} />
                        <span className={`relative inline-flex rounded-full h-4 w-4 ${style.bg}`} />
                      </span>
                    )}

                    {/* Node Circle */}
                    <div
                      className={`w-12 h-12 rounded-full flex flex-col items-center justify-center font-bold text-xs shadow-lg transition-colors border-2 ${
                        style.bg
                      } text-white ${isSelected ? 'ring-4 ring-indigo-400/50 ' + style.border : style.border}`}
                    >
                      <span className="text-[10px] font-mono leading-none">{pt.priority || 'P1'}</span>
                      <span className="text-xs font-extrabold">{pt.risk_score}</span>
                    </div>

                    {/* Label below node */}
                    <div className="mt-2 text-center">
                      <span className={`text-[11px] font-bold block ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                        {pt.name || pt.village}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        {pt.active_cases} cases ({pt.growth_label})
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Bottom coordinate indicators */}
            <div className="relative z-10 flex items-center justify-between text-[11px] text-slate-500 font-mono pt-2 border-t border-slate-900">
              <span>Projection: WGS84 Coarse Centroids</span>
              <span>Anand / Mehsana Dairy Belt</span>
            </div>
          </div>

          {/* Point Inspector Card (Sidebar panel) */}
          <div className="p-5 bg-slate-50 border-t lg:border-t-0 lg:border-l border-slate-200 flex flex-col justify-between">
            {activePoint ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                    activePoint.risk_tier === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                    activePoint.risk_tier === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {activePoint.risk_tier} RISK ({activePoint.risk_score}/100)
                  </span>
                  <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                    PRIORITY {activePoint.priority}
                  </span>
                </div>

                <div>
                  <h4 className="text-base font-bold text-slate-900">{activePoint.name || activePoint.village}</h4>
                  <p className="text-xs text-slate-500">
                    {activePoint.block}, {activePoint.district}, {activePoint.state}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 bg-white rounded-lg border border-slate-200">
                    <span className="text-slate-500 text-[11px] block">Active Cases</span>
                    <span className="text-base font-bold text-slate-900">{activePoint.active_cases}</span>
                    <span className="text-[10px] text-emerald-600 block">{activePoint.growth_label} 7d growth</span>
                  </div>
                  <div className="p-2.5 bg-white rounded-lg border border-slate-200">
                    <span className="text-slate-500 text-[11px] block">Affected Herds</span>
                    <span className="text-base font-bold text-slate-900">{activePoint.affected_herds}</span>
                    <span className="text-[10px] text-slate-400 block">{activePoint.affected_animals} animals</span>
                  </div>
                </div>

                <div className="p-3 bg-white rounded-lg border border-slate-200 text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Syndromic Signal:</span>
                    <span className="font-semibold text-slate-800">{activePoint.condition_signal}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Hotspot Status:</span>
                    <span className="font-semibold text-indigo-700">{activePoint.hotspot_status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Centroid Coords:</span>
                    <span className="font-mono text-slate-600">
                      {activePoint.latitude ? `${activePoint.latitude.toFixed(3)}°N, ${activePoint.longitude.toFixed(3)}°E` : 'ADMIN_ONLY'}
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-xs">
                  <span className="font-semibold block mb-0.5">Recommended Field Action:</span>
                  <span>Veterinary physical inspection and vector barrier verification recommended.</span>
                </div>

                {onOpenDossier && (
                  <button
                    onClick={() => onOpenDossier(activePoint.point_id || 'GEO-DEMO-001')}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-semibold flex items-center justify-center space-x-1 shadow-sm transition"
                  >
                    <span>Inspect Full Hotspot Dossier</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400 text-xs">
                Select an area node on the radar to inspect details.
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Tabular Spatial Cell Grid */
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {points.map((pt, idx) => (
              <div
                key={idx}
                onClick={() => handlePointClick(pt)}
                className="p-4 bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-400 transition cursor-pointer"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    pt.risk_tier === 'CRITICAL' ? 'bg-rose-100 text-rose-800' :
                    pt.risk_tier === 'HIGH' ? 'bg-amber-100 text-amber-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {pt.risk_tier} ({pt.risk_score})
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-700">{pt.priority}</span>
                </div>
                <h4 className="font-bold text-sm text-slate-900">{pt.name || pt.village}</h4>
                <p className="text-xs text-slate-500 mb-2">{pt.block}, {pt.district}</p>
                <div className="flex justify-between text-xs text-slate-700 font-medium pt-2 border-t border-slate-200">
                  <span>{pt.active_cases} Active Cases</span>
                  <span className="text-indigo-600">{pt.growth_label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safety Disclaimer Banner */}
      <div className="p-3 bg-slate-100 border-t border-slate-200 text-slate-600 text-[11px] flex items-center space-x-2">
        <Info className="w-4 h-4 text-indigo-600 shrink-0" />
        <span>
          <strong>DECISION-SUPPORT NOTICE: </strong>
          Geospatial risk signals are intended for early-warning decision support. Disease outbreaks require field investigation and appropriate confirmatory veterinary/laboratory procedures.
        </span>
      </div>
    </div>
  );
}
