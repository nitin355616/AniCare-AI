import React from 'react';
import {
  ClipboardList,
  UserCheck,
  MapPin,
  Calendar,
  AlertCircle,
  FileText,
  ChevronRight,
  ShieldCheck,
  Stethoscope
} from 'lucide-react';

export default function InvestigationBoard({ cases, onSelectCase, onAssign, onRecordVisit }) {
  const getPriorityBadge = (p) => {
    switch (p) {
      case 'P1':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-200">P1 CRITICAL</span>;
      case 'P2':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">P2 HIGH</span>;
      case 'P3':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">P3 MODERATE</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-700">P4 MONITOR</span>;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ALERT_GENERATED':
      case 'ALERT_ACKNOWLEDGED':
        return 'border-l-4 border-l-red-500 bg-red-50/20';
      case 'INVESTIGATION_ASSIGNED':
        return 'border-l-4 border-l-amber-500 bg-amber-50/20';
      case 'FIELD_INVESTIGATION':
        return 'border-l-4 border-l-blue-500 bg-blue-50/20';
      case 'LAB_PENDING':
        return 'border-l-4 border-l-purple-500 bg-purple-50/20';
      case 'DEPARTMENT_REVIEW':
        return 'border-l-4 border-l-indigo-500 bg-indigo-50/20';
      case 'ACTION_IN_PROGRESS':
      case 'FOLLOW_UP':
        return 'border-l-4 border-l-emerald-500 bg-emerald-50/20';
      case 'RESOLVED':
        return 'border-l-4 border-l-slate-400 bg-slate-50/30 opacity-75';
      default:
        return 'border-l-4 border-l-slate-300';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-indigo-600" />
            Field Investigation & Operational Response Board ({cases.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Active response cases tracked across field verification, specimen collection, and departmental actions
          </p>
        </div>
      </div>

      <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cases.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-400 text-sm">
            No active operational response cases found.
          </div>
        ) : (
          cases.map((c) => (
            <div
              key={c.response_case_id}
              onClick={() => onSelectCase && onSelectCase(c.response_case_id)}
              className={`rounded-xl border border-slate-200 p-4 shadow-2xs hover:shadow-md transition-all cursor-pointer ${getStatusColor(c.status)}`}
            >
              {/* Top row: Priority & Status */}
              <div className="flex items-center justify-between gap-2">
                {getPriorityBadge(c.priority)}
                <span className="text-[11px] font-semibold tracking-wider uppercase px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md">
                  {c.status.replace(/_/g, ' ')}
                </span>
              </div>

              {/* Case ID & Condition */}
              <div className="mt-3">
                <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                  {c.response_case_id}
                </span>
                <h4 className="text-sm font-bold text-slate-900 mt-1">
                  {(c.condition_signal || 'Health Risk').replace(/_/g, ' ')}
                </h4>
              </div>

              {/* Location */}
              <div className="mt-2.5 flex items-center gap-1.5 text-xs text-slate-600">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="truncate">
                  {c.location?.village}, {c.location?.block} ({c.location?.district})
                </span>
              </div>

              {/* Assignment & Risk Score */}
              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-slate-600 truncate max-w-[65%]">
                  <UserCheck className="w-3.5 h-3.5 text-indigo-500 shrink-0" />
                  <span className="truncate">
                    {c.assigned_officer_name || 'Unassigned'}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 text-[10px]">Risk:</span>{' '}
                  <span className="font-mono font-bold text-slate-900">
                    {c.risk_score?.toFixed(1) || '0.0'}
                  </span>
                </div>
              </div>

              {/* Card Footer Action */}
              <div className="mt-3 pt-2 flex items-center justify-between text-xs">
                <span className="text-[11px] text-slate-400">
                  {c.investigations?.length || 0} visits · {c.samples?.length || 0} samples
                </span>
                <span className="text-indigo-600 font-bold inline-flex items-center gap-0.5 hover:underline">
                  View Dossier <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
