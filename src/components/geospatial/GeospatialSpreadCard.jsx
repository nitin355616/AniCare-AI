import React from 'react';
import { Compass, ArrowRight, AlertTriangle, ShieldCheck, Info } from 'lucide-react';

export default function GeospatialSpreadCard({ spreadSignals = [], totalPatterns = 0 }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-50 text-amber-600 rounded-lg border border-amber-100">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Geographical Spread Pattern Analysis</h3>
            <p className="text-xs text-slate-500">
              Evaluates multi-area adjacency and temporal lags to detect contiguous spatial progression signals.
            </p>
          </div>
        </div>

        <span className="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-lg text-xs font-bold border border-amber-200">
          {totalPatterns} Pattern(s) Detected
        </span>
      </div>

      <div className="space-y-3">
        {spreadSignals && spreadSignals.length > 0 ? (
          spreadSignals.map((sig, idx) => (
            <div key={idx} className="p-4 bg-slate-50/70 border border-slate-200 rounded-xl space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded text-xs font-bold font-mono">
                  {sig.signal_status}
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  Confidence: <span className="font-semibold text-slate-700">{sig.confidence}</span>
                </span>
              </div>

              <div className="flex items-center space-x-2 text-slate-800 text-xs font-medium">
                <span className="font-bold text-slate-900">{sig.origin_area}</span>
                <ArrowRight className="w-4 h-4 text-amber-600 shrink-0" />
                <span className="font-bold text-indigo-700">{sig.destination_area}</span>
                {sig.distance_approx_km && (
                  <span className="text-slate-500 font-mono text-[11px]">
                    (~{sig.distance_approx_km} km • {sig.temporal_lag_days}d lag)
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-600 italic">
                {sig.description}
              </p>
            </div>
          ))
        ) : (
          <div className="p-4 bg-slate-50 rounded-lg text-center text-slate-400 text-xs">
            No contiguous spatial spread patterns detected across monitored clusters.
          </div>
        )}
      </div>

      <div className="mt-4 p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-amber-800 text-[11px] flex items-center space-x-2">
        <Info className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong>EPIDEMIOLOGICAL PRINCIPLE: </strong>
          Spatial proximity does NOT prove biological transmission without genetic sequencing or field veterinary contact tracing.
        </span>
      </div>
    </div>
  );
}
