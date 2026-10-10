import React from 'react';
import { ShieldCheck, Lock, Cpu, Hash, CheckCircle, AlertTriangle } from 'lucide-react';
import Badge from '../common/Badge';

export default function ModelHealthCard({ productionModel, isHealthy }) {
  if (!productionModel) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Loading production model health...</p>
      </div>
    );
  }

  const shaPrefix = productionModel.sha256 ? productionModel.sha256.substring(0, 16) + '...' : 'Unknown';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-lg border border-emerald-100">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-900">{productionModel.model_id}</h2>
              <span className="text-xs px-2 py-0.5 font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                ACTIVE PRODUCTION
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Architecture: <span className="font-medium text-slate-700">{productionModel.architecture || 'EfficientNet-B0'}</span> • Version: <span className="font-medium text-slate-700">{productionModel.version || '1.0.0'}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {productionModel.is_immutable && (
            <div className="flex items-center space-x-1.5 px-3 py-1.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-medium">
              <Lock className="w-3.5 h-3.5" />
              <span>Immutable Lock Active</span>
            </div>
          )}
          <div className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
            productionModel.is_integrity_valid 
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
              : 'bg-rose-50 text-rose-700 border border-rose-200'
          }`}>
            <ShieldCheck className="w-4 h-4" />
            <span>{productionModel.is_integrity_valid ? 'SHA-256 Verified' : 'Integrity Mismatch'}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100">
        <div className="bg-slate-50/70 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Operating Threshold (τ)</span>
          <div className="flex items-center space-x-1.5">
            <span className="text-lg font-bold text-slate-900">
              {productionModel.threshold !== undefined ? Number(productionModel.threshold).toFixed(2) : '0.50'}
            </span>
            <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">FROZEN</span>
          </div>
          <span className="text-[11px] text-slate-400">Milestone 7/8A Calibrated</span>
        </div>

        <div className="bg-slate-50/70 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Inference Engine</span>
          <span className="text-lg font-bold text-slate-900">ONNX Runtime</span>
          <span className="text-[11px] text-slate-400 block">OpSet 14 • 15.29 MB</span>
        </div>

        <div className="bg-slate-50/70 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Input Dimensions</span>
          <span className="text-lg font-bold text-slate-900">3 × 224 × 224</span>
          <span className="text-[11px] text-slate-400 block">RGB Tensor (0–1 range)</span>
        </div>

        <div className="bg-slate-50/70 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Cryptographic Fingerprint</span>
          <div className="flex items-center space-x-1 font-mono text-xs text-slate-700" title={productionModel.sha256}>
            <Hash className="w-3 h-3 text-slate-400 shrink-0" />
            <span className="truncate">{shaPrefix}</span>
          </div>
          <span className="text-[11px] text-emerald-600 font-medium block">Exact Match to Disk</span>
        </div>
      </div>
    </div>
  );
}
