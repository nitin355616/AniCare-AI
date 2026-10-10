import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Layers,
  Compass,
  Radio,
  FileText,
  UserCheck,
  Activity,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  MapPin,
  Clock,
  Sparkles,
  Award,
  Zap,
  Lock,
  GitBranch,
  Search,
  Database
} from 'lucide-react';

export default function SIHExecutiveDashboard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* 1. Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950/60 border border-emerald-500/30 p-8 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-0 pointer-events-none" />

        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 font-mono">
              SIH 2026 NATIONAL FINALIST
            </span>
            <span className="text-xs font-semibold text-slate-400">
              Problem Statement: AI-Powered Animal Health &amp; Disease Early Warning System
            </span>
          </div>

          <h1 className="text-3xl md:text-5xl font-black text-white tracking-tight leading-tight">
            AniCare AI — Livestock Health Intelligence &amp; Early Warning Platform
          </h1>

          <p className="text-slate-300 text-base md:text-lg max-w-4xl leading-relaxed">
            <strong className="text-white">Core Positioning:</strong> AniCare AI is a privacy-first, human-in-the-loop livestock health intelligence platform that converts animal-level health signals into geospatial early warnings and controlled veterinary/department response workflows.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => navigate('/sih-demo')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 shadow-lg shadow-emerald-950/80 transition transform hover:-translate-y-0.5"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch Live Interactive Walkthrough</span>
            </button>
            <button
              onClick={() => navigate('/jury-qa')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Jury Q&amp;A Defense Dossier</span>
            </button>
            <button
              onClick={() => navigate('/ai-validation')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <ShieldCheck className="w-4 h-4 text-teal-400" />
              <span>AI Validation &amp; Governance</span>
            </button>
          </div>
        </div>
      </div>

      {/* 2. Key Metrics Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Detection Speed</span>
            <Zap className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">Day 0 &ndash; 1</p>
          <span className="text-[11px] text-emerald-400 font-medium">vs 7&ndash;14 days traditional paper reporting</span>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Model Accuracy</span>
            <Award className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">92.75%</p>
          <span className="text-[11px] text-blue-300 font-medium">Held-Out Test Set (N=138, tau=0.50)</span>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Automated Tests</span>
            <CheckCircle2 className="w-4 h-4 text-teal-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">230 / 230 PASS</p>
          <span className="text-[11px] text-teal-300 font-medium">100% Backend &amp; Model Regression</span>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase">Safety Policy</span>
            <ShieldCheck className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-white mt-1">100% Human Sign-Off</p>
          <span className="text-[11px] text-amber-300 font-medium">Zero autonomous prescriptions</span>
        </div>
      </div>

      {/* 3. Problem vs Solution Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-rose-950/20 border border-rose-800/40 rounded-3xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Traditional Livestock Surveillance</h3>
              <span className="text-xs text-rose-300">Fragmented, Reactive, Delayed</span>
            </div>
          </div>
          <ul className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold shrink-0">&bull;</span>
              <span><strong>Delayed Reporting:</strong> Farmers often wait 7&ndash;14 days before consulting veterinarians, allowing diseases like Lumpy Skin Disease (LSD) and FMD to spread across village borders.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold shrink-0">&bull;</span>
              <span><strong>Isolated Animal Data:</strong> No spatial clustering. Single cases are treated in isolation without recognizing rising village-level outbreak patterns.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold shrink-0">&bull;</span>
              <span><strong>No Field Investigation Audit:</strong> Alert handoffs to mobile veterinary units rely on informal calls with zero chain-of-custody tracking for biological samples.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-rose-400 font-bold shrink-0">&bull;</span>
              <span><strong>Paper-Based Containment:</strong> Ring vaccination and quarantine directives take weeks to authorize and coordinate across district offices.</span>
            </li>
          </ul>
        </div>

        <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-3xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">AniCare AI Integrated Platform</h3>
              <span className="text-xs text-emerald-300">Proactive, Geospatial, Human-Governed</span>
            </div>
          </div>
          <ul className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">&bull;</span>
              <span><strong>Day 0 Multimodal Signal:</strong> Farmers report instantly in Hindi/English with offline synchronization; AI produces preliminary multimodal risk index.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">&bull;</span>
              <span><strong>Geospatial Outbreak Intelligence:</strong> Automated spatial density and clustering detects emerging hotspots at the village and block levels before widespread spread.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">&bull;</span>
              <span><strong>Audited Operational Response:</strong> P1/P2/P3 alerts dispatch Rapid Response Units with digital investigation protocols and barcoded cold-chain sample tracking.</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 font-bold shrink-0">&bull;</span>
              <span><strong>Continuous Model Assurance:</strong> Confirmed field diagnoses feed into drift monitoring (PSI) and continuous validation pipelines with frozen weights protection.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* 4. "Why Not Just an AI Image Classifier?" Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-indigo-950/40 border border-indigo-500/40 rounded-3xl p-6 shadow-xl">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-2xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 shrink-0">
            <Cpu className="w-7 h-7" />
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">Critical Architectural Insight</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-500/20 text-indigo-300">
                Why AniCare is NOT "Just a Classifier"
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              In livestock healthcare, a standalone computer vision model deployed to a mobile app is dangerous and clinically insufficient:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <strong className="text-xs text-indigo-300 block mb-1">1. Clinical Ambiguity</strong>
                <span className="text-[11px] text-slate-400">
                  Cutaneous lesions of Lumpy Skin Disease closely resemble pseudo-lumpy disease, insect hypersensitivity, and dermatophilosis. Reliable triage requires multimodal fusing of rectal temperature, lymphadenopathy, and seasonal vector history.
                </span>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <strong className="text-xs text-indigo-300 block mb-1">2. Veterinary Law &amp; Safety</strong>
                <span className="text-[11px] text-slate-400">
                  Allowing an AI model or farmer to prescribe schedule drugs or vaccines violates Indian Veterinary Council regulations and causes antibiotic resistance. AniCare strictly gates prescriptions behind verified veterinary license numbers.
                </span>
              </div>
              <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <strong className="text-xs text-indigo-300 block mb-1">3. Institutional Response</strong>
                <span className="text-[11px] text-slate-400">
                  An individual diagnosis does not contain an epidemic. AniCare bridges individual signals to district veterinary dashboards, geospatial radius mapping, cold-chain lab PCR verification, and authorized ring vaccination orders.
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 5. The 6 Pillars of AniCare AI */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-emerald-400" />
          <span>The Six Architectural Pillars</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <UserCheck className="w-5 h-5 text-emerald-400" />
              <h4 className="text-sm font-bold text-white">1. Farmer-First UX</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Bilingual Hindi/English interface designed for low-literacy rural users with icon-driven symptom logging, voice inputs, and full offline IndexedDB queue synchronization.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <Cpu className="w-5 h-5 text-teal-400" />
              <h4 className="text-sm font-bold text-white">2. Multimodal Risk Fusion</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Fuses EfficientNet-B0 vision features with structured clinical biomarkers and regional vector dynamics to output a calibrated risk index (0&ndash;100).
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <Compass className="w-5 h-5 text-cyan-400" />
              <h4 className="text-sm font-bold text-white">3. Geospatial Early Warning</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Automated spatial density and clustering algorithms group animal cases within 5km radii to detect emerging village and block-level outbreaks.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              <h4 className="text-sm font-bold text-white">4. Field Command Center</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Prioritized P1&ndash;P3 operational alerts, automated mobile unit dispatch, on-site investigation checklists, and chain-of-custody biological sample tracking.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <h4 className="text-sm font-bold text-white">5. Human Governance</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Strict veterinary licensing gatekeeping. All prescriptions, official outbreak alerts, and containment orders require verified digital signatures from qualified officials.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-5 h-5 text-blue-400" />
              <h4 className="text-sm font-bold text-white">6. Continuous AI Assurance</h4>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Population Stability Index (PSI) drift monitoring, isolated feedback pipelines, frozen production model weights, and quarantined external dataset governance.
            </p>
          </div>
        </div>
      </div>

      {/* 6. Navigation to Other Sections */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold text-white">Explore Full Technical Implementation</h3>
          <p className="text-xs text-slate-400 mt-1">
            Access the complete suite of SIH demonstration and evaluation modules:
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => navigate('/sih-demo')}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5"
          >
            <span>Live 10-Stage Walkthrough</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => navigate('/sih-mapping')}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            SIH Requirement Matrix
          </button>
        </div>
      </div>
    </div>
  );
}
