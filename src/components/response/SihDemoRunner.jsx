import React, { useState } from 'react';
import {
  PlayCircle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';

export default function SihDemoRunner({ onRunScenario }) {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);

  const stepsList = [
    { num: 1, title: 'Geospatial Detection', desc: 'Escalating cluster detected in Boriavi Sector (Score 88.5)' },
    { num: 2, title: 'Alert Generation', desc: 'P1 Critical operational alert generated with deduplication' },
    { num: 3, title: 'Dashboard Queuing', desc: 'Dispatched to Command Center alert queue' },
    { num: 4, title: 'Officer Acknowledgment', desc: 'DVO Dr. V. Sharma acknowledges and reviews signals' },
    { num: 5, title: 'Field Assignment', desc: 'Assigned to Dr. R. K. Patel (4-hour inspection target)' },
    { num: 6, title: 'On-site Investigation', desc: '18 cattle examined across 2 herds; 3 nodular lesions' },
    { num: 7, title: 'Specimen Collection', desc: 'Cutaneous lesion swab packaged in cold-chain transport' },
    { num: 8, title: 'Diagnostic Lab Dispatch', desc: 'Sample accessioned at State Lab (Status: LAB_PENDING)' },
    { num: 9, title: 'PCR Assay Result', desc: 'Real-time PCR result POSITIVE (Routes to Human Review)' },
    { num: 10, title: 'Department Review', desc: 'Joint Director DAHD reviews lab findings' },
    { num: 11, title: 'Authorized Containment', desc: 'Human-sanctioned vector barrier and biosecurity ring' },
    { num: 12, title: 'Veterinary Follow-up', desc: 'On-site recheck confirms clinical stabilization' },
    { num: 13, title: 'Response Case Closure', desc: 'Case marked RESOLVED with immutable audit trail' },
    { num: 14, title: 'Risk Recalculation', desc: 'Cluster downgraded to P4 Monitoring status' }
  ];

  const handleRun = async () => {
    setIsRunning(true);
    try {
      const res = await onRunScenario();
      setResult(res);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden p-5">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-200 mb-1">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" /> SIH 2026 National Hackathon Demonstration
          </span>
          <h3 className="text-base font-bold text-slate-900">
            End-to-End 14-Step Field Response & Government Action Protocol
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Demonstrates complete human-in-the-loop governance: AI detects & prioritizes; humans investigate & authorize.
          </p>
        </div>

        <button
          onClick={handleRun}
          disabled={isRunning}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-xs font-bold inline-flex items-center gap-2 shadow-xs transition-colors"
        >
          {isRunning ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Executing 14-Step Scenario...
            </>
          ) : (
            <>
              <PlayCircle className="w-4 h-4" />
              Run 14-Step Demonstration
            </>
          )}
        </button>
      </div>

      {/* Stepper Grid */}
      <div className="mt-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-2.5">
        {stepsList.map((st) => {
          const isCompleted = result && result.steps_completed >= st.num;
          return (
            <div
              key={st.num}
              className={`p-3 rounded-lg border text-left transition-all ${
                isCompleted
                  ? 'bg-emerald-50/70 border-emerald-200 shadow-2xs'
                  : 'bg-slate-50 border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${
                  isCompleted ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-600'
                }`}>
                  {st.num}
                </span>
                {isCompleted && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                )}
              </div>
              <div className="text-xs font-bold text-slate-800 truncate">
                {st.title}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5 line-clamp-2">
                {st.desc}
              </div>
            </div>
          );
        })}
      </div>

      {/* Scenario Execution Result Banner */}
      {result && (
        <div className="mt-5 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <div>
                <h4 className="text-sm font-bold">
                  {result.message}
                </h4>
                <p className="text-xs text-emerald-700 mt-0.5">
                  Case ID: <strong>{result.case_id}</strong> · Status: <strong>{result.final_status}</strong> · Auditable Events: <strong>{result.timeline_events_count}</strong>
                </p>
              </div>
            </div>
            <span className="text-xs font-mono text-emerald-600 font-bold bg-white px-3 py-1 rounded-md border border-emerald-200">
              14/14 Steps Verified
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
