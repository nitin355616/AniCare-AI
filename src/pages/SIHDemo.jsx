import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  ChevronRight,
  ChevronLeft,
  ExternalLink,
  CheckCircle2,
  Clock,
  Cpu,
  Layers,
  Compass,
  Radio,
  FileText,
  UserCheck,
  Activity,
  ShieldAlert,
  Maximize2,
  Minimize2,
  Lock,
  ArrowRight
} from 'lucide-react';
import demoService from '../services/api/demoService';

export default function SIHDemo() {
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);
  const [stages, setStages] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [presentationMode, setPresentationMode] = useState(false);
  const [actionNotice, setActionNotice] = useState(null);
  const autoPlayRef = useRef(null);

  // Load health and demo state
  const loadDemoData = async () => {
    try {
      const [h, s] = await Promise.all([
        demoService.getHealth(),
        demoService.getState()
      ]);
      setHealth(h);
      setStages(s.stages || []);
      if (s.current_step) setCurrentStep(s.current_step);
    } catch (err) {
      console.error('Failed to load demo data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDemoData();
  }, []);

  // Auto-play timer
  useEffect(() => {
    if (isAutoPlaying) {
      autoPlayRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= 10) {
            setIsAutoPlaying(false);
            return 10;
          }
          const next = prev + 1;
          demoService.advanceStep(next).catch(() => {});
          return next;
        });
      }, 3800);
    } else {
      if (autoPlayRef.current) clearInterval(autoPlayRef.current);
    }
    return () => {
      if (autoPlayRef.current) clearInterval(autoPlayRef.current);
    };
  }, [isAutoPlaying]);

  const handleStepClick = async (stepId) => {
    setCurrentStep(stepId);
    try {
      await demoService.advanceStep(stepId);
    } catch (err) {
      console.warn('Advance step warning:', err);
    }
  };

  const handleNext = () => {
    if (currentStep < 10) {
      handleStepClick(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      handleStepClick(currentStep - 1);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setActionNotice(null);
    try {
      const res = await demoService.seedDemo();
      setActionNotice({ type: 'success', message: res.message || 'Demo scenario seeded successfully!' });
      setCurrentStep(1);
      await loadDemoData();
    } catch (err) {
      setActionNotice({ type: 'error', message: 'Failed to seed demo: ' + err.message });
    } finally {
      setSeeding(false);
    }
  };

  const handleReset = async () => {
    setResetting(true);
    setActionNotice(null);
    setIsAutoPlaying(false);
    try {
      const res = await demoService.resetDemo();
      setActionNotice({ type: 'success', message: res.message || 'Safe reset completed. Demo data purged.' });
      setCurrentStep(1);
      await loadDemoData();
    } catch (err) {
      setActionNotice({ type: 'error', message: 'Failed to reset demo: ' + err.message });
    } finally {
      setResetting(false);
    }
  };

  const currentStage = stages.find((s) => s.step_id === currentStep) || stages[0];

  return (
    <div className={`space-y-6 transition-all duration-300 ${presentationMode ? 'p-2 max-w-7xl mx-auto' : ''}`}>
      {/* 1. Synthetic Data Disclaimer Banner */}
      <div className="bg-amber-950/40 border-2 border-amber-500/50 rounded-2xl p-4 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 shrink-0">
            <Lock className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black tracking-widest uppercase bg-amber-500 text-slate-950 px-2 py-0.5 rounded font-mono">
                SIH EVALUATION SANDBOX
              </span>
              <span className="text-xs font-semibold text-amber-300">Isolated Demonstration Environment</span>
            </div>
            <p className="text-xs text-amber-200/90 mt-1 leading-relaxed">
              <strong>DEMONSTRATION RUNTIME:</strong> All cases, locations, and actions in this walkthrough are synthetically generated for national jury evaluation. Production animal databases remain isolated and cannot be modified or corrupted.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => setPresentationMode(!presentationMode)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 border border-slate-700 transition"
            title="Toggle presentation focus mode"
          >
            {presentationMode ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            <span>{presentationMode ? 'Exit Focus' : 'Presentation View'}</span>
          </button>
        </div>
      </div>

      {/* 2. Top Header & Invariant Badges */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              SIH 2026 Interactive Demonstration
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Stage {currentStep} of 10
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            End-to-End Livestock Health Lifecycle: <span className="text-emerald-400 font-medium">Detect &rarr; Assess &rarr; Map &rarr; Alert &rarr; Investigate &rarr; Respond &rarr; Monitor</span>
          </p>
        </div>

        {/* System Invariant Telemetry Pills */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>ONNX Model:</span>
            <span className="font-mono text-emerald-300 font-bold">Bovine v1 (tau=0.50)</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
            <span>Dataset A Test:</span>
            <span className="font-mono text-blue-300 font-bold">92.75% Acc (N=138)</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <Lock className="w-3.5 h-3.5 text-amber-400" />
            <span>Dataset B:</span>
            <span className="font-mono text-amber-300 font-bold">QUARANTINED</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-teal-400" />
            <span>Regression:</span>
            <span className="font-mono text-teal-300 font-bold">230/230 PASS</span>
          </div>
        </div>
      </div>

      {/* Action Notification Banner */}
      {actionNotice && (
        <div
          className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
            actionNotice.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
              : 'bg-rose-950/40 border-rose-500/50 text-rose-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            <span>{actionNotice.message}</span>
          </div>
          <button
            onClick={() => setActionNotice(null)}
            className="text-slate-400 hover:text-white text-xs underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 3. Demo Control Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-950/60 transition disabled:opacity-50"
          >
            <Sparkles className={`w-4 h-4 ${seeding ? 'animate-spin' : ''}`} />
            <span>{seeding ? 'Seeding Scenario...' : 'Seed SIH Live Scenario'}</span>
          </button>

          <button
            onClick={() => setIsAutoPlaying(!isAutoPlaying)}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold border transition ${
              isAutoPlaying
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            {isAutoPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isAutoPlaying ? 'Pause Walkthrough' : 'Auto-Play Walkthrough'}</span>
          </button>

          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-950/30 text-rose-300 border border-rose-800/40 hover:bg-rose-900/40 transition disabled:opacity-50"
            title="Purges only demo synthetic records. Leaves real records untouched."
          >
            <RotateCcw className={`w-4 h-4 ${resetting ? 'animate-spin' : ''}`} />
            <span>{resetting ? 'Resetting...' : 'Safe Demo Reset'}</span>
          </button>
        </div>

        {/* Step Navigation Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrev}
            disabled={currentStep <= 1}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700 disabled:opacity-40 border border-slate-700 transition"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Back</span>
          </button>
          <span className="text-xs font-mono text-slate-400 px-2 font-semibold">
            {currentStep} / 10
          </span>
          <button
            onClick={handleNext}
            disabled={currentStep >= 10}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-40 transition shadow-md shadow-emerald-950/40"
          >
            <span>Next Stage</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 4. 10-Stage Horizontal Stepper Track */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 shadow-lg overflow-x-auto">
        <div className="min-w-[850px] flex items-center justify-between relative">
          {/* Background Track Line */}
          <div className="absolute top-4 left-6 right-6 h-0.5 bg-slate-800 -z-0" />
          <div
            className="absolute top-4 left-6 h-0.5 bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-400 -z-0 transition-all duration-500"
            style={{ width: `${((currentStep - 1) / 9) * 94}%` }}
          />

          {stages.map((stage) => {
            const isCompleted = stage.step_id < currentStep;
            const isCurrent = stage.step_id === currentStep;
            return (
              <button
                key={stage.step_id}
                onClick={() => handleStepClick(stage.step_id)}
                className="flex flex-col items-center group relative z-10 focus:outline-none transition-transform"
              >
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 border-2 shadow-lg ${
                    isCurrent
                      ? 'bg-emerald-500 text-slate-950 border-white ring-4 ring-emerald-500/30 scale-110'
                      : isCompleted
                      ? 'bg-teal-600 text-white border-teal-400'
                      : 'bg-slate-950 text-slate-500 border-slate-700 group-hover:border-slate-500'
                  }`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : stage.step_id}
                </div>
                <span
                  className={`text-[10px] mt-2 font-bold tracking-tight uppercase transition-colors whitespace-nowrap ${
                    isCurrent
                      ? 'text-emerald-400 font-extrabold'
                      : isCompleted
                      ? 'text-teal-300'
                      : 'text-slate-500 group-hover:text-slate-300'
                  }`}
                >
                  {stage.stage_name}
                </span>
                <span
                  className={`text-[9px] max-w-[75px] text-center truncate ${
                    isCurrent ? 'text-slate-200' : 'text-slate-500'
                  }`}
                >
                  {stage.title}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 5. Spotlight Active Stage Card */}
      {currentStage && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Stage Details (2 cols) */}
          <div className="lg:col-span-2 bg-gradient-to-br from-slate-900 to-slate-950 border-2 border-emerald-500/30 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-emerald-500/5 rounded-full blur-3xl -z-0" />

            <div className="flex flex-wrap items-center justify-between gap-3 relative z-10 pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center font-extrabold text-lg">
                  {currentStage.step_id}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl font-bold text-white">{currentStage.title}</h2>
                    <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {currentStage.stage_name}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">Responsible Role: <strong className="text-emerald-300">{currentStage.role}</strong></span>
                </div>
              </div>

              {currentStage.target_route && (
                <button
                  onClick={() => navigate(currentStage.target_route)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600/30 hover:bg-emerald-600 text-emerald-200 hover:text-white border border-emerald-500/40 transition group"
                >
                  <span>Open {currentStage.target_route}</span>
                  <ExternalLink className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              )}
            </div>

            <div className="mt-5 space-y-4 relative z-10">
              <div>
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Scenario Context & Lifecycle Event</h4>
                <p className="text-sm text-slate-200 mt-1 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                  {currentStage.description}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  <span className="text-xs font-bold text-teal-400 uppercase tracking-wider block mb-1">
                    System Action Executed
                  </span>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {currentStage.action}
                  </p>
                </div>

                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider block mb-1">
                    Verified Evidence / Output
                  </span>
                  <p className="text-xs font-mono text-cyan-200/90 leading-relaxed">
                    {currentStage.evidence}
                  </p>
                </div>
              </div>

              {/* Strict Human-in-the-Loop Safety Invariant */}
              <div className="bg-emerald-950/30 border border-emerald-500/40 p-3.5 rounded-xl flex items-start gap-3">
                <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider block">
                    Human-in-the-Loop Governance Invariant
                  </span>
                  <p className="text-xs text-emerald-100/90 mt-0.5">
                    {currentStage.safety_invariant}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Jury Context & Navigation (1 col) */}
          <div className="space-y-4">
            {/* Quick Links to Live Workflows */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <Compass className="w-4 h-4 text-emerald-400" />
                <span>Jump to Core Modules</span>
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/disease-detection')}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 text-left transition group"
                >
                  <div className="flex items-center gap-2.5">
                    <Cpu className="w-4 h-4 text-teal-400" />
                    <div>
                      <span className="text-xs font-bold text-slate-200 block">AI Disease Detection</span>
                      <span className="text-[10px] text-slate-400">ONNX Model Inference &amp; Symptoms</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition" />
                </button>

                <button
                  onClick={() => navigate('/geospatial')}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 text-left transition group"
                >
                  <div className="flex items-center gap-2.5">
                    <Radio className="w-4 h-4 text-cyan-400" />
                    <div>
                      <span className="text-xs font-bold text-slate-200 block">Geospatial Intelligence</span>
                      <span className="text-[10px] text-slate-400">Spatial Risk Mapping &amp; Clustering</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition" />
                </button>

                <button
                  onClick={() => navigate('/response')}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 text-left transition group"
                >
                  <div className="flex items-center gap-2.5">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <div>
                      <span className="text-xs font-bold text-slate-200 block">Response Command Center</span>
                      <span className="text-[10px] text-slate-400">Alerts, Samples &amp; Govt Actions</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition" />
                </button>

                <button
                  onClick={() => navigate('/farmer')}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 text-left transition group"
                >
                  <div className="flex items-center gap-2.5">
                    <UserCheck className="w-4 h-4 text-emerald-400" />
                    <div>
                      <span className="text-xs font-bold text-slate-200 block">Farmer Experience Portal</span>
                      <span className="text-[10px] text-slate-400">Hindi/English, Voice &amp; Offline Sync</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition" />
                </button>

                <button
                  onClick={() => navigate('/ai-monitoring')}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 text-left transition group"
                >
                  <div className="flex items-center gap-2.5">
                    <Activity className="w-4 h-4 text-blue-400" />
                    <div>
                      <span className="text-xs font-bold text-slate-200 block">AI Continuous Monitoring</span>
                      <span className="text-[10px] text-slate-400">Drift, Feedback &amp; Governance</span>
                    </div>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition" />
                </button>
              </div>
            </div>

            {/* SIH Jury Quick Reference */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span>Jury Reference Material</span>
              </h3>
              <p className="text-xs text-slate-400 mb-3">
                Review presentation materials, FAQ, and SIH requirement mapping:
              </p>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => navigate('/sih-dashboard')}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold text-center border border-slate-700"
                >
                  Executive Pitch
                </button>
                <button
                  onClick={() => navigate('/ai-validation')}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold text-center border border-slate-700"
                >
                  AI Validation
                </button>
                <button
                  onClick={() => navigate('/jury-qa')}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold text-center border border-slate-700"
                >
                  Jury Q&amp;A (8 Qs)
                </button>
                <button
                  onClick={() => navigate('/sih-mapping')}
                  className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold text-center border border-slate-700"
                >
                  SIH Matrix
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
