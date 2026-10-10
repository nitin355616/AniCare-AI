import React from 'react';
import { TrendingUp, Clock, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

export default function DiseaseTrendChart({ trends = [] }) {
  const defaultTrends = [
    { period_label: '24 Hours', days: 1, active_cases: 4, growth_pct: 33.3, critical_hotspots: 1, high_hotspots: 1 },
    { period_label: '7 Days', days: 7, active_cases: 18, growth_pct: 150.0, critical_hotspots: 1, high_hotspots: 1 },
    { period_label: '14 Days', days: 14, active_cases: 26, growth_pct: 85.0, critical_hotspots: 1, high_hotspots: 2 },
    { period_label: '30 Days', days: 30, active_cases: 42, growth_pct: 40.0, critical_hotspots: 1, high_hotspots: 2 }
  ];

  const data = trends && trends.length > 0 ? trends : defaultTrends;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-lg border border-indigo-100">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Multi-Window Epidemiological Velocity</h3>
            <p className="text-xs text-slate-500">
              Comparative caseload trajectory across 24-hour, 7-day, 14-day, and 30-day temporal windows.
            </p>
          </div>
        </div>

        <span className="text-xs px-2.5 py-1 bg-slate-100 text-slate-700 font-semibold rounded-lg">
          Zero-Division Safeguarded
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {data.map((item, idx) => (
          <div key={idx} className="p-4 bg-slate-50/70 rounded-xl border border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-bold text-slate-600">{item.period_label}</span>
              <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded ${
                item.growth_pct > 100 ? 'bg-rose-100 text-rose-700' :
                item.growth_pct > 0 ? 'bg-amber-100 text-amber-700' :
                'bg-emerald-100 text-emerald-700'
              }`}>
                +{item.growth_pct}%
              </span>
            </div>

            <div className="text-2xl font-bold text-slate-900 mb-1">
              {item.active_cases} <span className="text-xs font-normal text-slate-500">cases</span>
            </div>

            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-200">
              <span className="text-rose-600 font-medium">{item.critical_hotspots} Critical</span>
              <span className="text-amber-600 font-medium">{item.high_hotspots} High Risk</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
