import React, { useState } from 'react';
import { MapPin, ShieldAlert, Radio, AlertCircle, Compass } from 'lucide-react';
import { MOCK_ANALYTICS_DATA } from '../../data/mockData';
import Badge from '../common/Badge';

export default function OutbreakGeoMap() {
  const [activeZone, setActiveZone] = useState(MOCK_ANALYTICS_DATA.regionalRiskZones[0]);

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual Map Surface */}
        <div className="lg:col-span-2 relative bg-slate-900 rounded-xl overflow-hidden p-6 text-white min-h-[320px] flex flex-col justify-between border border-slate-800 shadow-inner">
          {/* Background gridlines & radar ripples */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:24px_24px] opacity-40 pointer-events-none" />

          {/* Top telemetry bar */}
          <div className="relative z-10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
              </span>
              <span className="text-xs font-mono uppercase tracking-wider text-slate-300">
                Satellite & Drone Geo-Telemetry Feed
              </span>
            </div>
            <span className="text-[11px] font-mono bg-slate-800 text-emerald-400 px-2 py-0.5 rounded border border-slate-700">
              Coverage: 5 Key Livestock Clusters
            </span>
          </div>

          {/* Map Node Pins (Positioned across simulated Indian coordinate map) */}
          <div className="relative z-10 my-8 h-44 flex items-center justify-around">
            {MOCK_ANALYTICS_DATA.regionalRiskZones.map((zone, idx) => {
              const isSelected = activeZone.district === zone.district;
              const isHigh = zone.riskLevel.includes('Critical');
              const isMod = zone.riskLevel.includes('Moderate');

              return (
                <button
                  key={zone.district}
                  onClick={() => setActiveZone(zone)}
                  className={`relative flex flex-col items-center group transition-all transform hover:scale-110 focus:outline-none ${
                    isSelected ? 'scale-110' : 'opacity-85'
                  }`}
                >
                  {/* Ping effect for critical zone */}
                  {isHigh && (
                    <span className="absolute -top-1 -right-1 flex h-4 w-4">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-500 opacity-80" />
                      <span className="relative inline-flex rounded-full h-4 w-4 bg-rose-600" />
                    </span>
                  )}

                  {/* Pin button */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs shadow-lg transition-colors border-2 ${
                      isHigh
                        ? 'bg-rose-500 text-white border-rose-300'
                        : isMod
                        ? 'bg-amber-500 text-white border-amber-300'
                        : 'bg-emerald-500 text-white border-emerald-300'
                    } ${isSelected ? 'ring-4 ring-white/30' : ''}`}
                  >
                    <MapPin className="w-5 h-5" />
                  </div>

                  <span className="mt-2 text-[11px] font-semibold text-slate-200 bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800 truncate max-w-[100px]">
                    {zone.district.split(' ')[0]}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {zone.activeCases} cases
                  </span>
                </button>
              );
            })}
          </div>

          {/* Bottom map overlay note */}
          <div className="relative z-10 flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
            <span className="flex items-center gap-1.5">
              <Compass className="w-4 h-4 text-emerald-400" />
              National Veterinary Epidemiology System (NVEDP)
            </span>
            <span className="text-[11px] text-amber-400 font-mono">
              10km Bio-Safety Geofence Enforced
            </span>
          </div>
        </div>

        {/* Selected Zone Deep Dive Card */}
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Zone Telemetry Inspector
              </span>
              <Badge
                variant={
                  activeZone.riskLevel.includes('Critical')
                    ? 'danger'
                    : activeZone.riskLevel.includes('Moderate')
                    ? 'warning'
                    : 'success'
                }
                pulse={activeZone.riskLevel.includes('Critical')}
              >
                {activeZone.riskLevel.split(' ')[0]}
              </Badge>
            </div>

            <h4 className="text-lg font-bold text-slate-900 tracking-tight">
              {activeZone.district}
            </h4>
            <p className="text-xs text-slate-500 mt-0.5">
              Regional Dairy & Livestock Surveillance Basin
            </p>

            <div className="mt-4 space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-200">
                <span className="text-slate-500">Active Disease Clusters</span>
                <span className="font-bold text-slate-800">{activeZone.activeCases} verified</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-200">
                <span className="text-slate-500">Susceptible Population</span>
                <span className="font-semibold text-slate-800">{activeZone.cattlePopulation} heads</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-200">
                <span className="text-slate-500">Quarantine Hubs Active</span>
                <span className="font-semibold text-slate-800">{activeZone.quarantineHubs} stations</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Ring Vaccination Status</span>
                <span className="font-semibold text-emerald-600">88.4% Ring Coverage</span>
              </div>
            </div>
          </div>

          <div className="mt-4 p-3 bg-white rounded-lg border border-slate-200 text-xs text-slate-600">
            <p className="font-semibold text-slate-900">Standard Operating Protocol:</p>
            <p className="text-[11px] text-slate-500 mt-1">
              Restrict cattle movement beyond sub-district boundaries. Mandatory thermal scan at dairy collection chilling centres.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
