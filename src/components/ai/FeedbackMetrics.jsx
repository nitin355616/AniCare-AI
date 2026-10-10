import React, { useState } from 'react';
import { Stethoscope, CheckCircle2, Edit3, XCircle, MessageSquare, Plus, ShieldCheck } from 'lucide-react';
import Modal from '../common/Modal';
import Button from '../common/Button';

export default function FeedbackMetrics({ feedbackSummary, feedbackList = [], onSubmitFeedback }) {
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    prediction_id: '',
    animal_id: '',
    agreement: 'AGREE',
    true_condition: 'Lumpy Skin Disease',
    notes: '',
    veterinarian_license: 'VET-REG-88402-GJ'
  });
  const [submitting, setSubmitting] = useState(false);

  const summary = feedbackSummary || {
    total_feedback: 0,
    agreed_count: 0,
    modified_count: 0,
    rejected_count: 0,
    agreement_rate: 100.0,
    rejection_rate: 0.0
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.prediction_id || !formData.animal_id) {
      alert('Please fill Prediction Event ID and Animal ID');
      return;
    }
    setSubmitting(true);
    try {
      await onSubmitFeedback(formData);
      setShowModal(false);
      setFormData({
        prediction_id: '',
        animal_id: '',
        agreement: 'AGREE',
        true_condition: 'Lumpy Skin Disease',
        notes: '',
        veterinarian_license: 'VET-REG-88402-GJ'
      });
    } catch (err) {
      alert(err.message || 'Error submitting clinical feedback');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-lg border border-emerald-100">
            <Stethoscope className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Veterinary Clinical Feedback Loop</h2>
            <p className="text-xs text-slate-500">
              Only certified veterinarians can submit ground-truth reviews. Farmer accounts are strictly blocked.
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Submit Clinical Feedback</span>
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Total Verified Reviews</span>
          <span className="text-2xl font-bold text-slate-900">{summary.total_feedback}</span>
          <span className="text-[11px] text-slate-400 block mt-0.5">Licensed Clinical Reviews</span>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">AI Agreement Rate</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-emerald-700">
            {summary.agreement_rate !== undefined ? `${Number(summary.agreement_rate).toFixed(1)}%` : '0%'}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">{summary.agreed_count} Verified Agreements</span>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">Modification Rate</span>
            <Edit3 className="w-3.5 h-3.5 text-amber-500" />
          </div>
          <div className="text-2xl font-bold text-amber-700">
            {summary.total_feedback > 0 ? `${((summary.modified_count / summary.total_feedback) * 100).toFixed(1)}%` : '0%'}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">{summary.modified_count} Adjusted Diagnoses</span>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">Rejection Rate</span>
            <XCircle className="w-3.5 h-3.5 text-rose-500" />
          </div>
          <div className="text-2xl font-bold text-rose-700">
            {summary.rejection_rate !== undefined ? `${Number(summary.rejection_rate).toFixed(1)}%` : '0%'}
          </div>
          <span className="text-[11px] text-slate-400 block mt-0.5">{summary.rejected_count} False Positives / OOD</span>
        </div>
      </div>

      {/* Recent Feedback Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Event ID</th>
              <th className="py-2.5 px-3">Animal</th>
              <th className="py-2.5 px-3">Decision</th>
              <th className="py-2.5 px-3">True Condition</th>
              <th className="py-2.5 px-3">Veterinarian Notes</th>
              <th className="py-2.5 px-3">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {feedbackList && feedbackList.length > 0 ? (
              feedbackList.slice(0, 5).map((item, idx) => (
                <tr key={idx} className="hover:bg-slate-50/50">
                  <td className="py-2.5 px-3 font-mono text-slate-800">{item.prediction_id ? item.prediction_id.substring(0, 12) + '...' : `FB-${idx}`}</td>
                  <td className="py-2.5 px-3 font-medium text-slate-900">{item.animal_id || 'AN-UNKNOWN'}</td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      item.agreement === 'AGREE' ? 'bg-emerald-100 text-emerald-800' :
                      item.agreement === 'MODIFY' ? 'bg-amber-100 text-amber-800' :
                      'bg-rose-100 text-rose-800'
                    }`}>
                      {item.agreement}
                    </span>
                  </td>
                  <td className="py-2.5 px-3">{item.true_condition || 'N/A'}</td>
                  <td className="py-2.5 px-3 text-slate-500 max-w-xs truncate">{item.notes || 'No notes'}</td>
                  <td className="py-2.5 px-3 text-slate-400">{item.created_at ? item.created_at.substring(0, 10) : 'Today'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="py-4 text-center text-slate-400">
                  No clinical feedback recorded yet. Certified veterinarians can submit reviews above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Submit Feedback Modal */}
      {showModal && (
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Submit Certified Clinical Feedback">
          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-800">
              <p className="font-semibold">Veterinary Authorization Required</p>
              <p className="mt-0.5 text-[11px]">
                Ground-truth feedback enters the continuous learning curation pipeline. All feedback is logged with statutory veterinary license credentials.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Prediction Event ID</label>
                <input
                  type="text"
                  required
                  placeholder="PRED-2026-..."
                  value={formData.prediction_id}
                  onChange={(e) => setFormData({ ...formData, prediction_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
              <div>
                <label className="block font-medium text-slate-700 mb-1">Animal ID / Tag</label>
                <input
                  type="text"
                  required
                  placeholder="AN-GJ-2024-..."
                  value={formData.animal_id}
                  onChange={(e) => setFormData({ ...formData, animal_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-emerald-500 outline-none"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-medium text-slate-700 mb-1">Clinical Agreement</label>
                <select
                  value={formData.agreement}
                  onChange={(e) => setFormData({ ...formData, agreement: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg bg-white focus:ring-1 focus:ring-emerald-500 outline-none"
                >
                  <option value="AGREE">AGREE (AI Screening Confirmed)</option>
                  <option value="MODIFY">MODIFY (Adjust Condition / Severity)</option>
                  <option value="REJECT">REJECT (False Positive / Artifact)</option>
                </select>
              </div>
              <div>
                <label className="block font-medium text-slate-700 mb-1">Veterinarian License No.</label>
                <input
                  type="text"
                  required
                  value={formData.veterinarian_license}
                  onChange={(e) => setFormData({ ...formData, veterinarian_license: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-emerald-500 outline-none font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Definitive / True Condition</label>
              <input
                type="text"
                required
                value={formData.true_condition}
                onChange={(e) => setFormData({ ...formData, true_condition: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-emerald-500 outline-none"
              />
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Clinical Examination Notes</label>
              <textarea
                rows="3"
                placeholder="Observed distinct circumscribed cutaneous lesions, pyrexia 104°F..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-1 focus:ring-emerald-500 outline-none"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-3 border-t">
              <Button variant="secondary" onClick={() => setShowModal(false)} type="button">
                Cancel
              </Button>
              <Button variant="primary" type="submit" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Feedback'}
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
