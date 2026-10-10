import React, { useState } from 'react';
import {
  X,
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  FlaskConical,
  FileCheck2,
  CheckCircle2,
  Clock,
  UserCheck,
  AlertTriangle,
  MapPin,
  Check,
  FileText,
  Calendar,
  Layers,
  ArrowRight
} from 'lucide-react';
import ResponseTimeline from './ResponseTimeline';
import SlaMetricsCard from './SlaMetricsCard';

export default function ResponseDossierModal({ caseData, onClose, onRefresh }) {
  if (!caseData) return null;

  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'alerts', label: `Alerts (${caseData.alerts?.length || 0})`, icon: ShieldAlert },
    { id: 'investigation', label: `Investigation (${caseData.investigations?.length || 0})`, icon: ClipboardList },
    { id: 'samples', label: `Samples (${caseData.samples?.length || 0})`, icon: FlaskConical },
    { id: 'review', label: `Dept Review (${caseData.department_reviews?.length || 0})`, icon: FileCheck2 },
    { id: 'actions', label: `Actions (${caseData.actions?.length || 0})`, icon: ShieldCheck },
    { id: 'followup', label: `Follow-up (${caseData.follow_ups?.length || 0})`, icon: CheckCircle2 },
    { id: 'timeline', label: `Audit Log (${caseData.timeline?.length || 0})`, icon: Clock }
  ];

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-5 bg-slate-900 text-white flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                {caseData.response_case_id}
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-500/30 text-red-200 border border-red-400/30">
                {caseData.priority} {caseData.severity}
              </span>
              <span className="text-xs uppercase font-semibold text-slate-300">
                {caseData.status?.replace(/_/g, ' ')}
              </span>
            </div>
            <h3 className="text-lg font-bold text-white mt-1">
              {(caseData.condition_signal || 'Health Risk Signal').replace(/_/g, ' ')}
            </h3>
            <p className="text-xs text-slate-300 flex items-center gap-1.5 mt-0.5">
              <MapPin className="w-3.5 h-3.5 text-indigo-400" />
              {caseData.location?.village}, {caseData.location?.block}, {caseData.location?.district}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Safety Disclaimer Banner */}
        <div className="px-5 py-2.5 bg-amber-50 border-b border-amber-200 flex items-center gap-2 text-xs text-amber-900">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
          <span>
            <strong>Statutory Decision Support:</strong> AI risk signals support prioritization. Field investigation and authorized veterinary/department decisions remain human-controlled.
          </span>
        </div>

        {/* Tab Navigation */}
        <div className="px-5 bg-slate-50 border-b border-slate-200 flex items-center gap-1 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 px-3 text-xs font-bold inline-flex items-center gap-1.5 border-b-2 whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-indigo-600 text-indigo-700 bg-white/50'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-5">
          {activeTab === 'overview' && (
            <div className="space-y-5">
              {/* SLA Metrics Card */}
              <SlaMetricsCard sla={caseData.sla_metrics} />

              {/* Case Metadata Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-50 rounded-xl p-4 border border-slate-200">
                <div>
                  <span className="text-[11px] font-semibold text-slate-500">Source Identifier</span>
                  <div className="text-xs font-mono font-bold text-slate-800 mt-0.5">{caseData.source_id}</div>
                  <div className="text-[10px] text-slate-400">{caseData.source_type}</div>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-500">Risk Score</span>
                  <div className="text-base font-mono font-bold text-slate-900 mt-0.5">{caseData.risk_score?.toFixed(1) || '0.0'}/100</div>
                  <div className="text-[10px] text-slate-400">Multi-factor Spatial Model</div>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-500">Assigned Officer</span>
                  <div className="text-xs font-bold text-slate-800 mt-0.5">{caseData.assigned_officer_name || 'Unassigned'}</div>
                  <div className="text-[10px] text-slate-400">{caseData.assigned_to || 'Pending'}</div>
                </div>
                <div>
                  <span className="text-[11px] font-semibold text-slate-500">Created At</span>
                  <div className="text-xs font-medium text-slate-800 mt-0.5">
                    {caseData.created_at ? new Date(caseData.created_at).toLocaleString() : 'N/A'}
                  </div>
                  <div className="text-[10px] text-slate-400">Server Synchronized</div>
                </div>
              </div>

              {/* Quick Status Summary */}
              <div className="bg-white rounded-xl border border-slate-200 p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 mb-3">
                  Workflow Execution Summary
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-slate-600">On-Site Field Investigations:</span>
                    <strong className="text-slate-900">{caseData.investigations?.length || 0} visits completed</strong>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-slate-600">Biological Specimens Dispatched:</span>
                    <strong className="text-slate-900">{caseData.samples?.length || 0} samples collected</strong>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-slate-600">Departmental Reviews:</span>
                    <strong className="text-slate-900">{caseData.department_reviews?.length || 0} reviews recorded</strong>
                  </div>
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                    <span className="text-slate-600">Authorized Containment Actions:</span>
                    <strong className="text-slate-900">{caseData.actions?.length || 0} actions active</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="space-y-3">
              {(caseData.alerts || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No alerts associated.</div>
              ) : (
                caseData.alerts.map((a) => (
                  <div key={a.alert_id} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{a.alert_id}</span>
                      <span className="text-xs font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded">{a.priority} {a.status}</span>
                    </div>
                    <h5 className="font-bold text-sm text-slate-900 mt-1">{a.title}</h5>
                    <p className="text-xs text-slate-600 mt-0.5">{a.message}</p>
                    {a.acknowledged_by && (
                      <div className="mt-2 pt-2 border-t border-slate-200 text-[11px] text-emerald-700 font-medium">
                        ✓ Acknowledged by {a.acknowledged_by} ({new Date(a.acknowledged_at).toLocaleString()})
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'investigation' && (
            <div className="space-y-3">
              {(caseData.investigations || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No on-site investigations logged yet.</div>
              ) : (
                caseData.investigations.map((inv) => (
                  <div key={inv.investigation_id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{inv.investigation_id}</span>
                      <span className="text-xs text-slate-500">{new Date(inv.visit_date).toLocaleString()}</span>
                    </div>
                    <div className="text-xs font-semibold text-slate-800">
                      Investigating Officer: <strong>{inv.officer_name}</strong>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs bg-white p-2.5 rounded-lg border border-slate-200">
                      <div>Animals Examined: <strong>{inv.animals_observed}</strong></div>
                      <div>Affected Animals: <strong className="text-red-600">{inv.affected_animals}</strong></div>
                      <div>Herds Checked: <strong>{inv.herds_observed}</strong></div>
                    </div>
                    <div className="text-xs text-slate-700">
                      <strong>Symptoms:</strong> {inv.symptoms_observed?.join(', ') || 'None noted'}
                    </div>
                    <div className="text-xs text-slate-700">
                      <strong>Biosecurity:</strong> {inv.biosecurity_observations}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'samples' && (
            <div className="space-y-3">
              {(caseData.samples || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No biological specimens collected.</div>
              ) : (
                caseData.samples.map((s) => (
                  <div key={s.sample_id} className="p-3.5 rounded-xl border border-slate-200 bg-slate-50">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{s.sample_id}</span>
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-800">{s.status}</span>
                    </div>
                    <div className="text-xs font-bold text-slate-900 mt-1">
                      Type: {s.sample_type} · Purpose: {s.purpose}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      Collected By: {s.collected_by_name} ({new Date(s.collected_at).toLocaleDateString()})
                    </div>
                    {s.lab_result && (
                      <div className="mt-2 p-2 rounded-lg bg-white border border-slate-200 text-xs">
                        Diagnostic Result: <strong className={s.lab_result === 'POSITIVE' ? 'text-red-700' : 'text-emerald-700'}>{s.lab_result}</strong> via {s.test_name} (Ref: {s.lab_reference})
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'review' && (
            <div className="space-y-3">
              {(caseData.department_reviews || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No department reviews recorded yet.</div>
              ) : (
                caseData.department_reviews.map((r) => (
                  <div key={r.review_id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{r.review_id}</span>
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-indigo-100 text-indigo-800">{r.decision}</span>
                    </div>
                    <p className="text-xs text-slate-800">{r.reason}</p>
                    <div className="text-[11px] text-slate-500 pt-1">
                      Reviewed by: <strong>{r.reviewer}</strong> ({r.reviewer_role}) on {new Date(r.reviewed_at).toLocaleString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'actions' && (
            <div className="space-y-3">
              {(caseData.actions || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No department containment actions authorized yet.</div>
              ) : (
                caseData.actions.map((act) => (
                  <div key={act.action_id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{act.action_id}</span>
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">{act.status}</span>
                    </div>
                    <div className="text-xs font-bold text-slate-900">{act.action_type.replace(/_/g, ' ')}</div>
                    <p className="text-xs text-slate-700">{act.reason}</p>
                    <div className="text-[11px] text-slate-500 pt-1">
                      Authorized by: <strong>{act.authorized_by}</strong> on {new Date(act.authorized_at).toLocaleDateString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'followup' && (
            <div className="space-y-3">
              {(caseData.follow_ups || []).length === 0 ? (
                <div className="py-8 text-center text-slate-400 text-xs">No follow-up visits recorded yet.</div>
              ) : (
                caseData.follow_ups.map((flw) => (
                  <div key={flw.follow_up_id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-indigo-700">{flw.follow_up_id}</span>
                      <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">{flw.risk_change}</span>
                    </div>
                    <div className="text-xs text-slate-800">
                      <strong>Observations:</strong> {flw.new_observations}
                    </div>
                    <div className="text-xs text-slate-800">
                      <strong>Containment Outcome:</strong> {flw.action_outcome}
                    </div>
                    <div className="text-[11px] text-slate-500 pt-1">
                      Logged by <strong>{flw.officer_name}</strong> on {new Date(flw.follow_up_date).toLocaleDateString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'timeline' && (
            <ResponseTimeline events={caseData.timeline} />
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Case ID: <strong className="text-slate-800">{caseData.response_case_id}</strong> · Status: <strong>{caseData.status}</strong>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition-colors"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
}
