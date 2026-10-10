import React, { useState } from 'react';
import { Activity, AlertTriangle, CheckCircle, RefreshCw, Sparkles, TrendingUp, Sun, EyeOff, AlertOctagon } from 'lucide-react';
import Button from '../common/Button';
import Badge from '../common/Badge';

export default function DriftStatusCard({ driftData, onSimulateDrift, onRefresh, isSimulating }) {
  if (!driftData) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Evaluating population drift metrics...</p>
      </div>
    );
  }

  const status = driftData.overall_status || 'NORMAL';
  const psi = driftData.psi_confidence !== undefined ? Number(driftData.psi_confidence).toFixed(4) : '0.0000';

  const getStatusColor = (st) => {
    switch (st) {
      case 'NORMAL':
        return {
          bg: 'bg-emerald-50',
          text: 'text-emerald-700',
          border: 'border-emerald-200',
          dot: 'bg-emerald-500',
          badgeText: 'NORMAL (PSI < 0.10)'
        };
      case 'WATCH':
        return {
          bg: 'bg-blue-50',
          text: 'text-blue-700',
          border: 'border-blue-200',
          dot: 'bg-blue-500',
          badgeText: 'WATCH (0.10 ≤ PSI < 0.20)'
        };
      case 'WARNING':
        return {
          bg: 'bg-amber-50',
          text: 'text-amber-700',
          border: 'border-amber-200',
          dot: 'bg-amber-500',
          badgeText: 'WARNING (0.20 ≤ PSI < 0.25)'
        };
      case 'CRITICAL':
        return {
          bg: 'bg-rose-50',
          text: 'text-rose-700',
          border: 'border-rose-200',
          dot: 'bg-rose-500',
          badgeText: 'CRITICAL (PSI ≥ 0.25)'
        };
      default:
        return {
          bg: 'bg-slate-50',
          text: 'text-slate-700',
          border: 'border-slate-200',
          dot: 'bg-slate-400',
          badgeText: st
        };
    }
  };

  const statusStyle = getStatusColor(status);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-lg border border-indigo-100">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900">Population Drift Monitoring</h2>
              <span className={`text-xs px-2.5 py-0.5 font-bold rounded-full ${statusStyle.bg} ${statusStyle.text} border ${statusStyle.border}`}>
                {statusStyle.badgeText}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Multi-signal statistical telemetry compared against frozen Dataset A baseline.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onSimulateDrift}
            disabled={isSimulating}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            title="Simulate distribution shift for SIH hackathon demonstration"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isSimulating ? 'Simulating...' : 'Simulate Drift (SIH Demo)'}</span>
          </button>
          <button
            onClick={onRefresh}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition"
            title="Refresh drift statistics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main PSI Bar & Multi-Signals */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-5">
        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Population Stability Index (PSI)</span>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-slate-900">{psi}</span>
          </div>
          <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className={`h-full ${statusStyle.dot}`}
              style={{ width: `${Math.min(Number(psi) * 200, 100)}%` }}
            />
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">Baseline: Dataset A Held-out Test</span>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">Confidence Shift</span>
            {driftData.confidence_drift_detected ? (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 font-semibold">DRIFT</span>
            ) : (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 font-semibold">STABLE</span>
            )}
          </div>
          <p className="text-xs text-slate-700 mt-2 font-medium">
            {driftData.confidence_drift_detected ? 'Confidence deciles shifted significantly' : 'Decile distributions closely track baseline'}
          </p>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">Image Quality Shift</span>
            {(driftData.illumination_drift_detected || driftData.blur_drift_detected) ? (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 font-semibold">ALTERED</span>
            ) : (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 font-semibold">STABLE</span>
            )}
          </div>
          <div className="flex items-center space-x-3 text-xs text-slate-600 mt-2">
            <div className="flex items-center space-x-1">
              <Sun className="w-3.5 h-3.5 text-amber-500" />
              <span>{driftData.illumination_drift_detected ? 'Light shift' : 'Lighting OK'}</span>
            </div>
            <div className="flex items-center space-x-1">
              <EyeOff className="w-3.5 h-3.5 text-slate-400" />
              <span>{driftData.blur_drift_detected ? 'Blur elevated' : 'Sharpness OK'}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-50/70 p-3.5 rounded-lg border border-slate-100">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-slate-500">Species Anomaly Rate</span>
            {driftData.species_anomaly_alert ? (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 font-semibold">ELEVATED</span>
            ) : (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 font-semibold">ACCEPTABLE</span>
            )}
          </div>
          <div className="text-lg font-bold text-slate-900 mt-1">
            {driftData.species_anomaly_rate !== undefined ? `${(Number(driftData.species_anomaly_rate) * 100).toFixed(1)}%` : '0.0%'}
          </div>
          <span className="text-[11px] text-slate-400 block">Unsupported species / OOD</span>
        </div>
      </div>

      {/* Advisory Banner */}
      <div className={`p-3.5 rounded-lg border flex items-start space-x-3 ${statusStyle.bg} ${statusStyle.border}`}>
        <AlertTriangle className={`w-4 h-4 mt-0.5 shrink-0 ${statusStyle.text}`} />
        <div className="text-xs">
          <span className={`font-semibold ${statusStyle.text}`}>Clinical AI Governance Recommendation: </span>
          <span className="text-slate-700">{driftData.recommendation || 'Continue standard surveillance.'}</span>
        </div>
      </div>
    </div>
  );
}
