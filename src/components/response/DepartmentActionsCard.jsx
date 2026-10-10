import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Clock,
  UserCheck,
  PlusCircle,
  FileText,
  AlertTriangle
} from 'lucide-react';

export default function DepartmentActionsCard({ cases, onAuthorizeAction }) {
  // Aggregate actions
  const actions = [];
  cases.forEach(c => {
    (c.actions || []).forEach(a => {
      actions.push({
        ...a,
        case_id: c.response_case_id,
        village: c.location?.village,
        block: c.location?.block
      });
    });
  });

  const [showModal, setShowModal] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState(cases[0]?.response_case_id || '');
  const [actionType, setActionType] = useState('BIOSECURITY_REVIEW');
  const [reason, setReason] = useState('Ring biosecurity containment and vector barrier spraying.');
  const [authorizedBy, setAuthorizedBy] = useState('District Magistrate & DVO');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAuthorize = async () => {
    if (!selectedCaseId) return;
    setIsSubmitting(true);
    try {
      await onAuthorizeAction(selectedCaseId, {
        action_type: actionType,
        reason: reason,
        authorized_by: authorizedBy
      });
      setShowModal(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getActionBadge = (type) => {
    switch (type) {
      case 'AUTHORIZED_CONTAINMENT':
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-200">RING CONTAINMENT</span>;
      case 'BIOSECURITY_REVIEW':
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">BIOSECURITY REVIEW</span>;
      case 'AUTHORIZED_VACCINATION_REVIEW':
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-purple-100 text-purple-800 border border-purple-200">VACCINATION REVIEW</span>;
      case 'FIELD_RECHECK':
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">FIELD RECHECK</span>;
      case 'FARMER_GUIDANCE':
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">FARMER GUIDANCE</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-700">{type.replace(/_/g, ' ')}</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-600" />
            Authorized Department Actions & Interventions ({actions.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Legally sanctioned biosecurity rings, quarantine perimeters, and targeted field directives
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold inline-flex items-center gap-1.5 shadow-xs transition-colors"
        >
          <PlusCircle className="w-4 h-4" /> Authorize Intervention
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100/75 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Action ID</th>
              <th className="py-3 px-4">Case / Area</th>
              <th className="py-3 px-4">Action Type</th>
              <th className="py-3 px-4">Sanctioned By</th>
              <th className="py-3 px-4">Regulatory Justification</th>
              <th className="py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {actions.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-400 text-sm">
                  No active department interventions authorized. Use button above to authorize action following clinical review.
                </td>
              </tr>
            ) : (
              actions.map((act) => (
                <tr key={act.action_id} className="hover:bg-indigo-50/40 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-slate-800 text-xs">
                      {act.action_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900 text-xs">{act.case_id}</div>
                    <div className="text-xs text-slate-500">{act.village}, {act.block}</div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {getActionBadge(act.action_type)}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-xs">
                    <div className="font-semibold text-slate-800">{act.authorized_by}</div>
                    <div className="text-slate-400 text-[11px]">{act.authorized_at ? new Date(act.authorized_at).toLocaleDateString() : 'Recent'}</div>
                  </td>
                  <td className="py-3 px-4 text-xs text-slate-700 max-w-xs">
                    {act.reason}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {act.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Authorize Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl border border-slate-200 p-6">
            <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-indigo-600" />
              Authorize Department Intervention
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Select response case and authorize containment or preventive measures.
            </p>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Response Case:
                </label>
                <select
                  value={selectedCaseId}
                  onChange={(e) => setSelectedCaseId(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                >
                  {cases.map((c) => (
                    <option key={c.response_case_id} value={c.response_case_id}>
                      {c.response_case_id} — {c.location?.village} ({c.priority})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Action Type:
                </label>
                <select
                  value={actionType}
                  onChange={(e) => setActionType(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                >
                  <option value="BIOSECURITY_REVIEW">BIOSECURITY REVIEW (Ring Vector Control & Enclosure)</option>
                  <option value="AUTHORIZED_CONTAINMENT">AUTHORIZED CONTAINMENT (Livestock Movement Restriction)</option>
                  <option value="FIELD_RECHECK">FIELD RECHECK (Secondary Inspection Within 48 Hours)</option>
                  <option value="AUTHORIZED_VACCINATION_REVIEW">AUTHORIZED VACCINATION REVIEW (Vaccine Stock Audit)</option>
                  <option value="ADDITIONAL_SAMPLING">ADDITIONAL SAMPLING (Expanded Epidemiological Swabs)</option>
                  <option value="VETERINARY_VISIT">VETERINARY VISIT (Senior Epidemiologist On-site Review)</option>
                  <option value="FARMER_GUIDANCE">FARMER GUIDANCE (Bilingual Isolation Advisory)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Regulatory Justification:
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={2}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Authorizing Authority / Officer:
                </label>
                <input
                  type="text"
                  value={authorizedBy}
                  onChange={(e) => setAuthorizedBy(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-3.5 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAuthorize}
                disabled={isSubmitting}
                className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 shadow-xs transition-colors"
              >
                {isSubmitting ? 'Authorizing...' : 'Authorize Action'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
