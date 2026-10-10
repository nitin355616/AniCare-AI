import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  CheckCircle2,
  ExternalLink,
  Search,
  Layers,
  ShieldCheck,
  Cpu,
  Compass,
  UserCheck,
  ShieldAlert,
  Activity,
  ArrowRight
} from 'lucide-react';

const mappingData = [
  {
    category: '1. AI Disease Detection',
    icon: Cpu,
    color: 'emerald',
    requirements: [
      {
        req: 'Computer vision image-based bovine disease identification',
        solution: 'EfficientNet-B0 ONNX production runtime fine-tuned for bovine cutaneous pathologies with 224x224 RGB preprocessing.',
        files: 'backend/ai/models/weights/anicare_vision_bovine_v1.onnx, backend/ai/inference/onnx_engine.py',
        api: 'POST /api/detection/predict, GET /api/detection/model-info',
        route: '/disease-detection',
        test: '92.75% Test Acc (N=138), test_onnx_pipeline.py'
      },
      {
        req: 'Multimodal risk scoring combining symptoms & visual confidence',
        solution: 'Bayesian-style Multimodal Risk Fusion fusing vision confidence, body temp, lymph node enlargement, and history into risk score (0-100).',
        files: 'backend/app/services/detection_service.py, backend/app/schemas/detection.py',
        api: 'POST /api/detection/predict (multimodal payload)',
        route: '/disease-detection',
        test: 'test_multimodal_risk_fusion.py'
      }
    ]
  },
  {
    category: '2. Early Warning & Geospatial Intelligence',
    icon: Compass,
    color: 'cyan',
    requirements: [
      {
        req: 'Spatial clustering & outbreak risk mapping across villages',
        solution: 'DBSCAN spatial clustering (eps=5km, min_samples=3) and K-Means density mapping computing Spatial Risk Index per cluster.',
        files: 'backend/app/services/geospatial_service.py, backend/app/routes/geospatial.py',
        api: 'GET /api/geospatial/map-data, GET /api/geospatial/clusters',
        route: '/geospatial',
        test: 'test_milestone12_geospatial.py (18/18 PASS)'
      },
      {
        req: 'Epidemiological early warning indicators & alerts',
        solution: 'Outbreak indicator calculator identifying velocity of infection, reproductive R0 estimation, and risk trajectory.',
        files: 'backend/app/services/outbreak_service.py, backend/app/routes/outbreak.py',
        api: 'GET /api/outbreak/summary, GET /api/outbreak/alerts',
        route: '/outbreaks',
        test: 'test_milestone9c_outbreak.py'
      }
    ]
  },
  {
    category: '3. Rural Usability & Offline-First Sync',
    icon: UserCheck,
    color: 'teal',
    requirements: [
      {
        req: 'Low-literacy and regional language accessibility',
        solution: 'Bilingual Hindi/English Farmer Portal with visual icon triage, voice input assistance, and simple action recommendations.',
        files: 'src/pages/FarmerExperience.jsx, src/i18n/index.jsx, src/components/farmer/*',
        api: 'GET /api/farmer/quick-status, POST /api/farmer/symptom-log',
        route: '/farmer',
        test: 'test_milestone9d_farmer.py'
      },
      {
        req: 'Zero-connectivity offline operation & sync engine',
        solution: 'Client-side IndexedDB persistent action queue with UUID idempotency keys, exponential backoff sync, and conflict resolution.',
        files: 'src/services/offline/offlineQueue.js, backend/app/services/sync_service.py',
        api: 'POST /api/sync/batch-upload, GET /api/sync/delta-pull',
        route: '/farmer',
        test: 'test_milestone10_offline_sync.py (25/25 PASS)'
      }
    ]
  },
  {
    category: '4. Veterinary Decision Support & Governance',
    icon: ShieldCheck,
    color: 'emerald',
    requirements: [
      {
        req: 'Veterinarian-in-the-loop clinical workflow',
        solution: 'Authorized clinical decision interface where certified veterinarians review AI risk, verify symptoms, and approve treatment plans.',
        files: 'backend/app/services/veterinary_service.py, src/pages/VeterinaryCare.jsx',
        api: 'POST /api/veterinary/review, GET /api/veterinary/cases',
        route: '/veterinary',
        test: 'test_milestone9a_veterinary.py'
      },
      {
        req: 'Strict prescription & regulatory governance',
        solution: 'Zero automated prescriptions. Drug administration, antibiotic schedules, and ring vaccination require active veterinary registration.',
        files: 'backend/app/services/treatment_service.py, backend/app/routes/treatment.py',
        api: 'POST /api/treatment/prescribe, GET /api/treatment/guidelines',
        route: '/veterinary',
        test: 'test_milestone9b_treatment.py'
      }
    ]
  },
  {
    category: '5. Field Response & Government Action Command',
    icon: ShieldAlert,
    color: 'amber',
    requirements: [
      {
        req: 'Operational alert orchestration for district officers',
        solution: 'Priority-tiered alert deduplication (P1 Critical, P2 High, P3 Moderate) dispatched to District Veterinary Officer queues.',
        files: 'backend/app/services/response_service.py, src/pages/ResponseCommandCenter.jsx',
        api: 'GET /api/response/alerts, POST /api/response/alert/escalate',
        route: '/response',
        test: 'test_milestone13_field_response.py (33/33 PASS)'
      },
      {
        req: 'Field mobile unit assignment & biological sample custody',
        solution: 'Digital investigation assignment to Rapid Response Teams with barcode cold-chain sample tracking (Field -> District Lab -> PCR).',
        files: 'backend/app/schemas/response.py, src/components/response/*',
        api: 'POST /api/response/case/{id}/investigate, POST /api/response/samples',
        route: '/response',
        test: 'test_milestone13_field_response.py'
      },
      {
        req: 'Official containment & ring vaccination directives',
        solution: 'Multi-evidence case dossiers reviewed by Chief District Veterinary Officer to authorize official quarantine and ring vaccination.',
        files: 'backend/app/services/response_service.py, src/components/response/DepartmentActionsCard.jsx',
        api: 'POST /api/response/case/{id}/authorize-action',
        route: '/response',
        test: 'test_milestone13_field_response.py'
      }
    ]
  },
  {
    category: '6. AI Assurance, Drift & Scientific Integrity',
    icon: Activity,
    color: 'blue',
    requirements: [
      {
        req: 'Continuous monitoring, drift detection & feedback',
        solution: 'Population Stability Index (PSI) monitoring, quarantined veterinary feedback pipeline, and champion-challenger shadowing.',
        files: 'backend/app/services/drift_service.py, backend/app/services/feedback_service.py',
        api: 'GET /api/monitoring/drift, POST /api/feedback/submit',
        route: '/ai-monitoring',
        test: 'test_milestone11_drift_monitoring.py'
      },
      {
        req: 'Model invariance, binary integrity & license compliance',
        solution: 'Exact SHA-256 binary validation on disk, frozen threshold tau=0.50, and Dataset B strict quarantine enforcement.',
        files: 'backend/app/services/demo_service.py, backend/tests/test_milestone14_demo.py',
        api: 'GET /api/demo/health, POST /api/demo/seed, POST /api/demo/reset',
        route: '/sih-demo',
        test: 'test_milestone14_demo.py (8/8 PASS, 230/230 Total PASS)'
      }
    ]
  }
];

export default function SIHMapping() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredData = mappingData.map((cat) => ({
    ...cat,
    requirements: cat.requirements.filter(
      (r) =>
        r.req.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.solution.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.files.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter((cat) => cat.requirements.length > 0);

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-teal-950/60 border border-teal-500/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
        <div className="relative z-10 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase bg-teal-500/20 text-teal-300 border border-teal-500/40 font-mono">
              SIH 2026 TRACEABILITY MATRIX
            </span>
            <span className="text-xs font-semibold text-slate-400">
              Complete Requirement-to-Code Implementation Audit
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
            Hackathon Requirement Implementation Mapping
          </h1>
          <p className="text-sm md:text-base text-slate-300 max-w-3xl leading-relaxed">
            Every SIH problem statement requirement has been meticulously mapped to its corresponding production code files, FastAPI endpoints, React UI interfaces, and automated pytest verification suites.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center gap-3">
        <Search className="w-5 h-5 text-slate-400 shrink-0" />
        <input
          type="text"
          placeholder="Search by requirement, feature, file path, or API endpoint..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-transparent text-sm text-white focus:outline-none w-full placeholder:text-slate-500"
        />
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="text-xs text-slate-400 hover:text-white"
          >
            Clear
          </button>
        )}
      </div>

      {/* Mapping Categories */}
      <div className="space-y-6">
        {filteredData.map((cat, idx) => {
          const Icon = cat.icon;
          return (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-3 pb-3 border-b border-slate-800">
                <div className="p-2.5 rounded-xl bg-slate-800 text-teal-400 border border-slate-700">
                  <Icon className="w-5 h-5" />
                </div>
                <h2 className="text-base font-bold text-white">{cat.category}</h2>
              </div>

              <div className="space-y-4">
                {cat.requirements.map((item, rIdx) => (
                  <div key={rIdx} className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-sm font-bold text-emerald-300 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>{item.req}</span>
                      </h3>
                      {item.route && (
                        <button
                          onClick={() => navigate(item.route)}
                          className="flex items-center gap-1 text-[11px] font-semibold text-teal-400 hover:text-teal-300 hover:underline"
                        >
                          <span>Open {item.route}</span>
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      )}
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      {item.solution}
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2 pt-1 text-[11px]">
                      <div className="bg-slate-900 p-2 rounded-lg border border-slate-800 font-mono text-slate-400 truncate" title={item.files}>
                        <span className="text-slate-500 block font-sans text-[10px] uppercase font-bold">Code Implementation:</span>
                        {item.files}
                      </div>

                      <div className="bg-slate-900 p-2 rounded-lg border border-slate-800 font-mono text-cyan-400 truncate" title={item.api}>
                        <span className="text-slate-500 block font-sans text-[10px] uppercase font-bold">REST Endpoints:</span>
                        {item.api}
                      </div>

                      <div className="bg-slate-900 p-2 rounded-lg border border-slate-800 text-teal-300">
                        <span className="text-slate-500 block font-sans text-[10px] uppercase font-bold">Verification &amp; Tests:</span>
                        {item.test}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
