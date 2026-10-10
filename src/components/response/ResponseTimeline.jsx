import React from 'react';
import {
  Clock,
  ShieldAlert,
  CheckCircle2,
  UserCheck,
  ClipboardList,
  FlaskConical,
  FileCheck2,
  ShieldCheck,
  Check,
  RefreshCw
} from 'lucide-react';

export default function ResponseTimeline({ events }) {
  const getEventIcon = (type) => {
    switch (type) {
      case 'RISK_DETECTED':
      case 'ALERT_CREATED':
        return <ShieldAlert className="w-4 h-4 text-red-600" />;
      case 'ALERT_ACKNOWLEDGED':
        return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
      case 'INVESTIGATION_ASSIGNED':
        return <UserCheck className="w-4 h-4 text-amber-600" />;
      case 'FIELD_INVESTIGATION':
      case 'INVESTIGATION_COMPLETED':
        return <ClipboardList className="w-4 h-4 text-blue-600" />;
      case 'SAMPLE_COLLECTED':
        return <FlaskConical className="w-4 h-4 text-purple-600" />;
      case 'LAB_RESULT_RECORDED':
        return <FileCheck2 className="w-4 h-4 text-indigo-600" />;
      case 'DEPARTMENT_REVIEWED':
      case 'ACTION_AUTHORIZED':
        return <ShieldCheck className="w-4 h-4 text-emerald-600" />;
      case 'CASE_CLOSED':
        return <Check className="w-4 h-4 text-slate-600" />;
      case 'RISK_RECALCULATED':
        return <RefreshCw className="w-4 h-4 text-cyan-600" />;
      default:
        return <Clock className="w-4 h-4 text-slate-500" />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'RISK_DETECTED':
      case 'ALERT_CREATED':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'ALERT_ACKNOWLEDGED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'INVESTIGATION_ASSIGNED':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'FIELD_INVESTIGATION':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'SAMPLE_COLLECTED':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'LAB_RESULT_RECORDED':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'DEPARTMENT_REVIEWED':
      case 'ACTION_AUTHORIZED':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'CASE_CLOSED':
        return 'bg-slate-100 text-slate-800 border-slate-200';
      case 'RISK_RECALCULATED':
        return 'bg-cyan-100 text-cyan-800 border-cyan-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  if (!events || events.length === 0) {
    return (
      <div className="py-8 text-center text-slate-400 text-xs">
        No timeline events recorded yet.
      </div>
    );
  }

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {events.map((ev, idx) => (
        <div key={ev.event_id || idx} className="relative group">
          {/* Node icon */}
          <div className="absolute -left-6 top-1 w-5 h-5 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center group-hover:border-indigo-600 transition-colors">
            <div className="w-2 h-2 rounded-full bg-indigo-600" />
          </div>

          {/* Event Content */}
          <div className="bg-slate-50/80 rounded-xl p-3 border border-slate-200/80 hover:border-slate-300 transition-colors">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold border ${getEventColor(ev.event_type)}`}>
                {getEventIcon(ev.event_type)}
                {ev.event_type.replace(/_/g, ' ')}
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : 'N/A'}
              </span>
            </div>

            <p className="text-xs text-slate-800 font-medium mt-1.5 leading-relaxed">
              {ev.description}
            </p>

            <div className="mt-2 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-500">
              <span>
                By: <strong className="text-slate-700">{ev.actor || 'System'}</strong> ({ev.role || 'Authority'})
              </span>
              {ev.event_id && (
                <span className="font-mono text-[10px] text-slate-400">
                  {ev.event_id}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
