import React, { useState } from 'react';
import {
  FlaskConical,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileBadge,
  UserCheck,
  PlusCircle,
  FileCheck2
} from 'lucide-react';

export default function SampleLabTable({ cases, onRecordResult }) {
  // Aggregate samples from all cases
  const samples = [];
  cases.forEach(c => {
    (c.samples || []).forEach(s => {
      samples.push({
        ...s,
        case_id: c.response_case_id,
        village: c.location?.village,
        condition: c.condition_signal
      });
    });
  });

  const [selectedSample, setSelectedSample] = useState(null);
  const [resultType, setResultType] = useState('POSITIVE');
  const [testName, setTestName] = useState('Real-Time RT-PCR Assay');
  const [labRef, setLabRef] = useState('LAB-REF-2026-');
  const [reviewer, setReviewer] = useState('Dr. Sharma (State Lab)');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleOpenResultModal = (sample) => {
    setSelectedSample(sample);
    setLabRef(`LAB-REF-${sample.sample_id.replace('SMP-', '')}`);
    setNotes(`Diagnostic confirmatory assay performed for ${sample.purpose || 'investigation'}.`);
  };

  const handleConfirmResult = async () => {
    if (!selectedSample) return;
    setIsSubmitting(true);
    try {
      await onRecordResult(selectedSample.sample_id, {
        result: resultType,
        test_name: testName,
        lab_reference: labRef,
        reviewer: reviewer,
        notes: notes
      });
      setSelectedSample(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RESULT_AVAILABLE':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200"><CheckCircle2 className="w-3 h-3 text-emerald-600" /> RESULT AVAILABLE</span>;
      case 'LAB_PENDING':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-purple-100 text-purple-800 border border-purple-200"><Clock className="w-3 h-3 text-purple-600" /> LAB PENDING</span>;
      case 'PROCESSING':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200"><Clock className="w-3 h-3 text-blue-600" /> PROCESSING</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">{status}</span>;
    }
  };

  const getResultBadge = (res) => {
    switch (res) {
      case 'POSITIVE':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800 border border-red-200">POSITIVE</span>;
      case 'NEGATIVE':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">NEGATIVE</span>;
      case 'INCONCLUSIVE':
        return <span className="px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200">INCONCLUSIVE</span>;
      default:
        return <span className="text-xs text-slate-400 italic">Pending Assay</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Governance Banner */}
      <div className="p-3.5 bg-indigo-50/70 border-b border-indigo-100 flex items-start gap-2.5 text-xs text-indigo-950">
        <AlertTriangle className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Human Governance Guard:</span> Diagnostic laboratory results advance cases to <strong>Department Review</strong>. Autonomous medication, quarantine, or vaccination is strictly prohibited by statutory veterinary regulations.
        </div>
      </div>

      <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-indigo-600" />
            Biological Specimen & Laboratory Registry ({samples.length})
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Cold-chain diagnostic tracking for field swab, blood, tissue, and serum specimens
          </p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-100/75 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
            <tr>
              <th className="py-3 px-4">Sample ID</th>
              <th className="py-3 px-4">Case / Location</th>
              <th className="py-3 px-4">Specimen Type</th>
              <th className="py-3 px-4">Collected By</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Lab Result</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {samples.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-400 text-sm">
                  No biological samples currently registered in this response window.
                </td>
              </tr>
            ) : (
              samples.map((s) => (
                <tr key={s.sample_id} className="hover:bg-indigo-50/40 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100 text-xs">
                      {s.sample_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900 text-xs">
                      {s.case_id}
                    </div>
                    <div className="text-xs text-slate-500">
                      {s.village || 'Field Settlement'}
                    </div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-800 rounded font-semibold text-xs border border-slate-200">
                      {s.sample_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-xs">
                    <div className="font-medium text-slate-800">{s.collected_by_name || 'Inspector'}</div>
                    <div className="text-slate-400 text-[11px]">{s.collected_at ? new Date(s.collected_at).toLocaleDateString() : 'Recent'}</div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {getStatusBadge(s.status)}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    {getResultBadge(s.lab_result)}
                  </td>
                  <td className="py-3 px-4 text-right whitespace-nowrap">
                    {s.status === 'LAB_PENDING' ? (
                      <button
                        onClick={() => handleOpenResultModal(s)}
                        className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-semibold inline-flex items-center gap-1 shadow-xs transition-colors"
                      >
                        <FileCheck2 className="w-3.5 h-3.5" /> Enter Result
                      </button>
                    ) : (
                      <span className="text-xs text-slate-400 font-medium">Verified</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Enter Result Modal */}
      {selectedSample && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl max-w-md w-full shadow-xl border border-slate-200 p-6">
            <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FlaskConical className="w-5 h-5 text-indigo-600" />
              Record Diagnostic Result: {selectedSample.sample_id}
            </h4>
            <p className="text-xs text-slate-500 mt-1">
              Specimen: {selectedSample.sample_type} · Case: {selectedSample.case_id}
            </p>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Diagnostic Result:
                </label>
                <select
                  value={resultType}
                  onChange={(e) => setResultType(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                >
                  <option value="POSITIVE">POSITIVE (Pathogen Confirmed)</option>
                  <option value="NEGATIVE">NEGATIVE (No Pathogen Detected)</option>
                  <option value="INCONCLUSIVE">INCONCLUSIVE (Repeat Specimen Required)</option>
                  <option value="INVALID">INVALID (Specimen Compromised)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Assay / Test Methodology:
                </label>
                <input
                  type="text"
                  value={testName}
                  onChange={(e) => setTestName(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Laboratory Accession Reference:
                </label>
                <input
                  type="text"
                  value={labRef}
                  onChange={(e) => setLabRef(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reviewing Pathologist Name:
                </label>
                <input
                  type="text"
                  value={reviewer}
                  onChange={(e) => setReviewer(e.target.value)}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Diagnostic Notes / Ct Value:
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  className="w-full text-sm border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 focus:outline-hidden"
                />
              </div>
            </div>

            <div className="mt-5 flex items-center justify-end gap-2">
              <button
                onClick={() => setSelectedSample(null)}
                className="px-3.5 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmResult}
                disabled={isSubmitting}
                className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-semibold inline-flex items-center gap-1.5 shadow-xs transition-colors"
              >
                {isSubmitting ? 'Recording...' : 'Submit Diagnostic Result'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
