import React from 'react';
import {
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingDown,
  Gauge
} from 'lucide-react';

export default function SlaMetricsCard({ sla }) {
  if (!sla) return null;

  const metrics = [
    { label: 'Time to Acknowledge', val: sla.time_to_acknowledge_minutes, target: '30 min', overdue: sla.is_p1_ack_overdue },
    { label: 'Time to Assign', val: sla.time_to_assign_minutes, target: '60 min', overdue: false },
    { label: 'Time to Field Visit', val: sla.time_to_field_visit_minutes, target: '240 min', overdue: sla.is_p1_investigation_overdue },
    { label: 'Time to Sample', val: sla.time_to_sample_minutes, target: '300 min', overdue: false },
    { label: 'Time to Lab Result', val: sla.time_to_lab_result_minutes, target: '24-48 hrs', overdue: false },
    { label: 'Time to Resolution', val: sla.time_to_resolution_minutes, target: 'Clinical', overdue: false }
  ];

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
          <Gauge className="w-4 h-4 text-indigo-600" />
          Operational Turnaround & SLA Telemetry
        </h4>
        <span className="text-[11px] text-slate-400 font-medium">
          Calculated from real event timestamps
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {metrics.map((m, idx) => (
          <div
            key={idx}
            className={`p-2.5 rounded-lg border text-center transition-colors ${
              m.overdue
                ? 'bg-red-50/60 border-red-200'
                : m.val !== null
                ? 'bg-emerald-50/40 border-emerald-200'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="text-[11px] font-semibold text-slate-500 truncate">
              {m.label}
            </div>
            <div className="text-base font-bold font-mono text-slate-900 mt-0.5">
              {m.val !== null ? `${m.val}m` : '—'}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Target: {m.target}
            </div>
            {m.overdue && (
              <span className="inline-block mt-1 px-1.5 py-0.2 rounded text-[9px] font-bold bg-red-100 text-red-700">
                OVERDUE
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
