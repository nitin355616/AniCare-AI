import React from 'react';
import { FlaskConical, TrendingUp, CheckCircle, ArrowRight, ShieldCheck, Zap } from 'lucide-react';

export default function ExperimentComparison({ experiments = [] }) {
  // Baseline experiment data from Milestone 8B / Dataset A official test
  const defaultExperiments = [
    {
      experiment_id: 'EXP-01-BASELINE-V1',
      model_name: 'EfficientNet-B0 (Production V1)',
      status: 'PRODUCTION',
      threshold: 0.50,
      sensitivity: 80.95,
      specificity: 97.92,
      macro_f1: 0.9106,
      roc_auc: 0.9452,
      pr_auc: 0.9352,
      ece: 0.1673,
      latency_ms: 142
    },
    {
      experiment_id: 'EXP-011-SHADOW-V2',
      model_name: 'EfficientNet-B0 + Curated Mining (Candidate V2)',
      status: 'SHADOW',
      threshold: 0.50,
      sensitivity: 83.33,
      specificity: 97.92,
      macro_f1: 0.9214,
      roc_auc: 0.9510,
      pr_auc: 0.9420,
      ece: 0.1412,
      latency_ms: 146
    }
  ];

  const exps = experiments && experiments.length > 0 ? experiments : defaultExperiments;
  const baseline = exps[0] || defaultExperiments[0];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg border border-blue-100">
            <FlaskConical className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Side-by-Side Model Benchmark Matrix</h2>
            <p className="text-xs text-slate-500">
              Evaluated strictly on Dataset A official held-out test set (N=138, 42 positive, 96 healthy). Operating threshold frozen at τ = 0.50.
            </p>
          </div>
        </div>

        <span className="text-xs px-2.5 py-1 bg-slate-100 text-slate-700 font-semibold rounded-lg border border-slate-200">
          Dataset A Held-Out (N=138)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Experiment</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3">Sensitivity</th>
              <th className="py-2.5 px-3">Specificity</th>
              <th className="py-2.5 px-3">Macro F1</th>
              <th className="py-2.5 px-3">ROC-AUC</th>
              <th className="py-2.5 px-3">PR-AUC</th>
              <th className="py-2.5 px-3">ECE (Calibration)</th>
              <th className="py-2.5 px-3">Latency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {exps.map((exp, idx) => {
              const isProd = exp.status === 'PRODUCTION';
              const sensDiff = exp.sensitivity - baseline.sensitivity;
              const f1Diff = exp.macro_f1 - baseline.macro_f1;
              const eceDiff = baseline.ece - exp.ece; // lower is better

              return (
                <tr key={idx} className={`hover:bg-slate-50/50 ${isProd ? 'bg-emerald-50/20' : ''}`}>
                  <td className="py-3 px-3">
                    <div className="font-bold text-slate-900">{exp.model_name || exp.experiment_id}</div>
                    <span className="text-[10px] text-slate-400 font-mono">{exp.experiment_id}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      isProd ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'
                    }`}>
                      {exp.status}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-800">
                    {exp.sensitivity ? `${Number(exp.sensitivity).toFixed(2)}%` : '80.95%'}
                    {!isProd && sensDiff > 0 && (
                      <span className="text-[10px] text-emerald-600 font-bold ml-1">+{sensDiff.toFixed(2)}%</span>
                    )}
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-800">
                    {exp.specificity ? `${Number(exp.specificity).toFixed(2)}%` : '97.92%'}
                  </td>
                  <td className="py-3 px-3 font-semibold text-slate-800">
                    {exp.macro_f1 ? Number(exp.macro_f1).toFixed(4) : '0.9106'}
                    {!isProd && f1Diff > 0 && (
                      <span className="text-[10px] text-emerald-600 font-bold ml-1">+{f1Diff.toFixed(4)}</span>
                    )}
                  </td>
                  <td className="py-3 px-3">{exp.roc_auc ? Number(exp.roc_auc).toFixed(4) : '0.9452'}</td>
                  <td className="py-3 px-3">{exp.pr_auc ? Number(exp.pr_auc).toFixed(4) : '0.9352'}</td>
                  <td className="py-3 px-3 font-mono">
                    {exp.ece ? Number(exp.ece).toFixed(4) : '0.1673'}
                    {!isProd && eceDiff > 0 && (
                      <span className="text-[10px] text-emerald-600 font-bold ml-1">(-{eceDiff.toFixed(4)})</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-500">
                    {exp.latency_ms ? `${exp.latency_ms}ms` : '142ms'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
