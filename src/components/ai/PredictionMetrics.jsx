import React, { useState } from 'react';
import { Eye, AlertTriangle, CheckCircle, Search, Filter, ShieldCheck, Sun, EyeOff } from 'lucide-react';

export default function PredictionMetrics({ predictions = [], total = 0, onRefresh }) {
  const [search, setSearch] = useState('');
  const [filterCondition, setFilterCondition] = useState('ALL');

  const filtered = predictions.filter((p) => {
    const matchSearch =
      (p.animal_id && p.animal_id.toLowerCase().includes(search.toLowerCase())) ||
      (p.prediction_id && p.prediction_id.toLowerCase().includes(search.toLowerCase()));
    const matchCond = filterCondition === 'ALL' || p.predicted_condition === filterCondition;
    return matchSearch && matchCond;
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-sky-50 text-sky-600 rounded-lg border border-sky-100">
            <Eye className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Inference Telemetry Stream</h2>
            <p className="text-xs text-slate-500">
              Live logging of visual screening events with automated image quality and out-of-domain scoring.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search Animal or Pred ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs border rounded-lg focus:ring-1 focus:ring-sky-500 outline-none w-48"
            />
          </div>
          <select
            value={filterCondition}
            onChange={(e) => setFilterCondition(e.target.value)}
            className="px-2.5 py-1.5 text-xs border rounded-lg bg-white text-slate-700 outline-none"
          >
            <option value="ALL">All Conditions</option>
            <option value="Lumpy Skin Disease">Lumpy Skin Disease</option>
            <option value="Healthy / Non-Lesional">Healthy / Non-Lesional</option>
            <option value="Foot and Mouth Disease">Foot and Mouth Disease</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Prediction ID</th>
              <th className="py-2.5 px-3">Animal ID</th>
              <th className="py-2.5 px-3">Predicted Condition</th>
              <th className="py-2.5 px-3">Confidence</th>
              <th className="py-2.5 px-3">Image Quality</th>
              <th className="py-2.5 px-3">Safety Flags</th>
              <th className="py-2.5 px-3">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.length > 0 ? (
              filtered.map((p, idx) => {
                const conf = p.confidence !== undefined ? Number(p.confidence).toFixed(1) : '85.0';
                const quality = p.image_quality || {};
                const isLsd = (p.predicted_condition || '').toLowerCase().includes('lumpy');

                return (
                  <tr key={idx} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-3 font-mono text-slate-800">
                      {p.prediction_id ? p.prediction_id.substring(0, 14) + '...' : `PRED-${idx}`}
                    </td>
                    <td className="py-2.5 px-3 font-medium text-slate-900">{p.animal_id || 'AN-LIVE'}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        isLsd ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {p.predicted_condition || 'Lumpy Skin Disease'}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono font-semibold text-slate-800">{conf}%</td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center space-x-2 text-[11px]">
                        <span className="text-slate-700 font-medium">{quality.blur_score ? `B:${quality.blur_score.toFixed(0)}` : 'Sharp'}</span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-700 font-medium">{quality.brightness ? `L:${quality.brightness.toFixed(0)}` : 'Well-lit'}</span>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      {p.is_low_confidence ? (
                        <span className="px-1.5 py-0.5 bg-amber-100 text-amber-800 rounded text-[10px] font-semibold">
                          Low Conf
                        </span>
                      ) : p.is_out_of_domain ? (
                        <span className="px-1.5 py-0.5 bg-rose-100 text-rose-800 rounded text-[10px] font-semibold">
                          OOD
                        </span>
                      ) : (
                        <span className="text-emerald-600 flex items-center space-x-1 text-[11px]">
                          <CheckCircle className="w-3 h-3" />
                          <span>Standard</span>
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 font-mono text-[11px]">
                      {p.timestamp ? p.timestamp.substring(11, 19) : 'Just now'}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" className="py-4 text-center text-slate-400">
                  No predictions recorded in this session yet. Run a disease detection scan to see live telemetry.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
