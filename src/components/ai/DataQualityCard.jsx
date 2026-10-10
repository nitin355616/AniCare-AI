import React from 'react';
import { Database, ShieldAlert, CheckCircle, FileCheck, AlertTriangle, Layers, Filter } from 'lucide-react';

export default function DataQualityCard({ dataQuality }) {
  const quality = dataQuality || {
    total_candidate_samples: 18,
    accepted_samples: 16,
    rejected_samples: 2,
    quarantined_samples: 0,
    dataset_b_quarantined: true,
    quarantine_notice: 'Dataset B remains legally quarantined (PERMISSION_REQUIRED) under Milestone 8A governance.',
    evidence_tier_breakdown: {
      UNVERIFIED: 0,
      VET_REVIEWED: 14,
      LAB_CONFIRMED: 2,
      REJECTED: 2
    }
  };

  const tiers = quality.evidence_tier_breakdown || {};

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-50 text-amber-600 rounded-lg border border-amber-100">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Data Curation & Provenance Pipeline</h2>
            <p className="text-xs text-slate-500">
              8-stage automated curation filter ensures 0% data leakage, image quality validation, and statutory licensing.
            </p>
          </div>
        </div>

        <span className="text-xs px-2.5 py-1 bg-emerald-50 text-emerald-700 font-semibold rounded-lg border border-emerald-200">
          Leakage Guard: 0% Cross-Split
        </span>
      </div>

      {/* Legal Quarantine Banner */}
      {quality.dataset_b_quarantined && (
        <div className="mb-5 p-3.5 bg-amber-50/80 border border-amber-200 rounded-lg flex items-start space-x-3">
          <ShieldAlert className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
          <div className="text-xs text-amber-800">
            <span className="font-bold">Dataset B Legal Quarantine Invariant: </span>
            <span>{quality.quarantine_notice}</span>
          </div>
        </div>
      )}

      {/* 8-Stage Curation Pipeline Steps */}
      <div className="mb-5">
        <span className="text-xs font-semibold text-slate-700 block mb-2">8-Stage Automated Admission Stages:</span>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">1. File & Format Check</span>
            <span className="text-[11px] text-slate-500">MIME, header, decode</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">2. Image Quality Gate</span>
            <span className="text-[11px] text-slate-500">Blur, brightness, energy</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">3. Unsupported Species</span>
            <span className="text-[11px] text-slate-500">Reject non-bovine/OOD</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">4. Duplicate Detection</span>
            <span className="text-[11px] text-slate-500">SHA-256 + 64-bit dHash</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">5. Legal Permission Gate</span>
            <span className="text-[11px] text-slate-500">CC-BY / Quarantined</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">6. Clinical Verification</span>
            <span className="text-[11px] text-slate-500">Licensed Vet Review</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">7. Leakage Guard</span>
            <span className="text-[11px] text-slate-500">Animal-level grouping</span>
          </div>
          <div className="p-2 bg-slate-50 rounded border border-slate-100">
            <span className="font-semibold text-slate-800 block">8. Candidate Admission</span>
            <span className="text-[11px] text-slate-500">Admitted to Train/Val</span>
          </div>
        </div>
      </div>

      {/* Evidence Tier Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100">
        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Tier 1: Lab Confirmed</span>
          <div className="text-xl font-bold text-emerald-700">{tiers.LAB_CONFIRMED || 0}</div>
          <span className="text-[11px] text-slate-400">RT-PCR / Viral Isolation</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Tier 2: Vet Reviewed</span>
          <div className="text-xl font-bold text-blue-700">{tiers.VET_REVIEWED || 0}</div>
          <span className="text-[11px] text-slate-400">Licensed Clinical Diagnosis</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Tier 3: Rejected / OOD</span>
          <div className="text-xl font-bold text-rose-700">{tiers.REJECTED || 0}</div>
          <span className="text-[11px] text-slate-400">Low Quality / False Positive</span>
        </div>

        <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block mb-1">Total Curated Admitted</span>
          <div className="text-xl font-bold text-slate-900">{quality.accepted_samples || 0}</div>
          <span className="text-[11px] text-slate-400">Safe for Candidate Training</span>
        </div>
      </div>
    </div>
  );
}
