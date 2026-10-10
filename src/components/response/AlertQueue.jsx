import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUpRight,
  ShieldAlert,
  ChevronRight,
  Filter,
  Check
} from 'lucide-react';

export default function AlertQueue({ alerts, onAcknowledge, onEscalate, onSelectCase }) {
  const [priorityFilter, setPriorityFilter] = useState('ALL');
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [ackComment, setAckComment] = useState('Alert acknowledged by field veterinary officer.');
  const [showAckModal, setShowAckModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const filteredAlerts = alerts.filter(a => {
    if (priorityFilter !== 'ALL' && a.priority !== priorityFilter) return false;
    return true;
  });

  const handleOpenAck = (alert, e) => {
    e.stopPropagation();
    setSelectedAlert(alert);
    setAckComment(`Alert acknowledged for ${alert.location?.village || 'cluster'} by veterinary authority.`);
    setShowAckModal(true);
  };

  const handleConfirmAck = async () => {
    if (!selectedAlert) return;
    setIsSubmitting(true);
    try {
      await onAcknowledge(selectedAlert.alert_id, ackComment);
      setShowAckModal(false);
      setSelectedAlert(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPriorityBadge = (p) => {
    switch (p) {
      case 'P1':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-200"><ShieldAlert className="w-3 h-3 text-red-600" /> P1 CRITICAL</span>;
      case 'P2':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200"><AlertTriangle className="w-3 h-3 text-amber-600" /> P2 HIGH</span>;
      case 'P3':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200"><Clock className="w-3 h-3 text-blue-600" /> P3 MODERATE</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200">P4 MONITOR</span>;
    }
  };

  const getStatusBadge = (s) => {
    switch (s) {
      case 'ACTIVE':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-700 border border-red-200">ACTIVE</span>;
      case 'ACKNOWLEDGED':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">ACKNOWLEDGED</span>;
      case 'RESOLVED':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-50 text-slate-600 border border-slate-200">RESOLVED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">{s}</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header & Priority Filter Toolbar */}
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-indigo-600" />
            Operational Alert Queue ({filteredAlerts.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Deduplicated early-warning signals prioritized for field inspection
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <div className="inline-flex rounded-lg border border-slate-300 p-0.5 bg-white text-xs font-medium">
            {['ALL', 'P1', 'P2', 'P3', 'P4'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-2.5 py-1 rounded-md transition-colors ${
                  priorityFilter === p
                    ? 'bg-indigo-600 text-white font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100/75 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Priority</th>
              <th className="py-3 px-4">Location</th>
              <th className="py-3 px-4">Clinical Signal</th>
              <th className="py-3 px-4 text-center">Risk Score</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Created</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredAlerts.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-400 text-sm">
                  No active operational alerts matching current filter.
                </td>
              </tr>
            ) : (
              filteredAlerts.map((alert) => (
                <tr
                  key={alert.alert_id}
                  onClick={() => onSelectCase && onSelectCase(alert.response_case_id)}
                  className="hover:bg-indigo-50/40 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4 whitespace-nowrap">
                    {getPriorityBadge(alert.priority)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">
                      {alert.location?.village || 'Village Sector'}
                    </div>
                    <div className="text-xs text-slate-500">
                      {alert.location?.block}, {alert.location?.district}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-medium text-slate-800">
                      {(alert.condition_signal || 'Health Risk').replace(/_/g, ' ')}
                    </span>
                    <div className="text-xs text-slate-400 truncate max-w-xs">
                      {alert.alert_type}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="inline-block px-2 py-0.5 rounded font-mono font-bold text-xs bg-slate-100 text-slate-800 border border-slate-200">
                      {alert.risk_score?.toFixed(1) || 'N/A'}
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {getStatusBadge(alert.status)}
                  </td>
                  <td className="py-3 px-4 text-xs text-slate-500 whitespace-nowrap">
                    {alert.created_at ? new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent'}
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      {alert.status === 'ACTIVE' && (
                        <button
                          onClick={(e) => handleOpenAck(alert, e)}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-semibold inline-flex items-center gap-1 shadow-xs transition-colors"
                          title="Acknowledge Alert"
                        >
                          <Check className="w-3 h-3" /> Acknowledge
                        </button>
                      )}
                      <button
                        onClick={() => onSelectCase && onSelectCase(alert.response_case_id)}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs font-semibold inline-flex items-center gap-1 transition-colors"
                      >
                        Dossier <ChevronRight className="w-3 h-3 text-slate-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Acknowledge Modal */}
      {showAckModal && selectedAlert && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl border border-slate-200 p-6">
            <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-600" />
              Acknowledge Alert: {selectedAlert.alert_id}
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Priority {selectedAlert.priority} — {selectedAlert.location?.village}, {selectedAlert.location?.block}
            </p>

            <div className="mt-4">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Acknowledgement Remarks / Directives:
              </label>
              <textarea
                value={ackComment}
                onChange={(e) => setAckComment(e.target.value)}
                rows={3}
                className="w-full text-sm border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-emerald-500 focus:outline-hidden"
                placeholder="Enter field instructions or acknowledgment notes..."
              />
            </div>

            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                onClick={() => setShowAckModal(false)}
                className="px-3.5 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmAck}
                disabled={isSubmitting}
                className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 shadow-xs transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
                {isSubmitting ? 'Recording...' : 'Confirm Acknowledgement'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
