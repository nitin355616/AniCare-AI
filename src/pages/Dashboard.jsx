import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  PawPrint,
  HeartPulse,
  AlertTriangle,
  ShieldCheck,
  Activity,
  ScanEye,
  Camera,
  UploadCloud,
  PlusCircle,
  FileText,
  PhoneCall,
  Calendar,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  Sparkles,
  Info,
  Thermometer,
  ShieldAlert,
  ChevronRight,
  HelpCircle,
  FileSpreadsheet
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import HealthScoreGauge from '../components/charts/HealthScoreGauge';
import DiseasePrevalenceChart from '../components/charts/DiseasePrevalenceChart';
import {
  MOCK_SUMMARY_METRICS,
  MOCK_ANIMALS,
  MOCK_ALERTS,
  MOCK_HEALTH_REPORTS,
  MOCK_VETS,
  DEMO_DISCLAIMER
} from '../data/mockData';

export default function Dashboard() {
  const navigate = useNavigate();

  // Quick action modal states
  const [showAddAnimalModal, setShowAddAnimalModal] = useState(false);
  const [showContactVetModal, setShowContactVetModal] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Drag and drop image state in dashboard AI section
  const [dashPreviewImage, setDashPreviewImage] = useState(
    'https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=600&q=80'
  );
  const [dragActive, setDragActive] = useState(false);

  // New Animal Form state
  const [newAnimalData, setNewAnimalData] = useState({
    tag: '',
    name: '',
    species: 'Cattle',
    breed: 'Gir',
    location: 'Shed 01'
  });

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    showToast('Image uploaded. Click "Analyze Animal Health" to run AI detection.');
  };

  const handleAddAnimalSubmit = (e) => {
    e.preventDefault();
    showToast(`Simulation: Animal ${newAnimalData.tag || 'TAG-New'} successfully added to central monitoring registry.`);
    setShowAddAnimalModal(false);
  };

  // Filter recent animals for the display list
  const recentAnimals = MOCK_ANIMALS.slice(0, 5);

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-200">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-sm px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 border border-slate-700 animate-in slide-in-from-bottom-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Welcome / Header Section */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 rounded-2xl p-6 sm:p-8 text-white border border-slate-800 shadow-sm relative overflow-hidden">
        {/* Subtle background decoration */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-[radial-gradient(ellipse_at_top_right,#10b981_0%,transparent_70%)] opacity-20 pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                AniCare AI &bull; National Epizootic Surveillance
              </span>
              <span className="text-xs text-slate-400">
                &bull; Tuesday, October 6, 2026
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-white">
              Livestock Health & Disease Early-Warning Hub
            </h1>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed">
              Monitoring <strong className="text-emerald-300">1,420 livestock units</strong> across 12 dairy sheds. Continuous AI sensor telemetry, early lesion analysis, and regional biosecurity containment.
            </p>
          </div>

          {/* Real-time system pulse status */}
          <div className="flex-shrink-0 flex flex-col sm:flex-row lg:flex-col items-start lg:items-end gap-2.5">
            <div className="bg-slate-800/90 border border-slate-700/80 px-4 py-2.5 rounded-xl flex items-center gap-3">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              <div>
                <p className="text-xs font-bold text-white leading-tight">Live Telemetry Active</p>
                <p className="text-[11px] text-emerald-400 font-mono leading-tight">{MOCK_SUMMARY_METRICS.lastSync}</p>
              </div>
            </div>
            <span className="text-xs text-slate-400">SIH 2026 Evaluation Prototype</span>
          </div>
        </div>
      </div>

      {/* 2. Key Statistics Cards (Total Animals, Healthy, At Risk, Critical, Active Alerts) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
        {/* Total Animals */}
        <div
          onClick={() => navigate('/animals')}
          className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-2xs hover:shadow-md hover:border-slate-300 cursor-pointer transition-all duration-150"
        >
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <span>Total Animals</span>
            <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
              <PawPrint className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {MOCK_SUMMARY_METRICS.totalAnimals.toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-400 mt-1 truncate">12 Dairy Sheds Monitored</p>
        </div>

        {/* Healthy */}
        <div
          onClick={() => navigate('/animals?status=Healthy')}
          className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-2xs hover:shadow-md hover:border-emerald-300 cursor-pointer transition-all duration-150"
        >
          <div className="flex items-center justify-between text-xs font-semibold text-emerald-700 uppercase tracking-wider">
            <span>Healthy</span>
            <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-emerald-600 tracking-tight">
            {MOCK_SUMMARY_METRICS.healthyAnimals.toLocaleString()}
          </div>
          <p className="text-[11px] text-emerald-700/80 mt-1 font-medium truncate">92.8% Nominal State</p>
        </div>

        {/* At Risk */}
        <div
          onClick={() => navigate('/animals?status=Under Observation')}
          className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-2xs hover:shadow-md hover:border-amber-300 cursor-pointer transition-all duration-150"
        >
          <div className="flex items-center justify-between text-xs font-semibold text-amber-700 uppercase tracking-wider">
            <span>At Risk</span>
            <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
              <HeartPulse className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-amber-600 tracking-tight">
            {MOCK_SUMMARY_METRICS.atRisk}
          </div>
          <p className="text-[11px] text-amber-700/80 mt-1 font-medium truncate">Requires Surveillance</p>
        </div>

        {/* Critical */}
        <div
          onClick={() => navigate('/animals?status=Critical')}
          className="bg-white rounded-xl border border-rose-200 p-4 shadow-2xs hover:shadow-md hover:border-rose-300 cursor-pointer transition-all duration-150 bg-rose-50/20"
        >
          <div className="flex items-center justify-between text-xs font-semibold text-rose-700 uppercase tracking-wider">
            <span>Critical</span>
            <div className="p-1.5 rounded-lg bg-rose-100 text-rose-600">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-rose-600 tracking-tight">
            {MOCK_SUMMARY_METRICS.critical}
          </div>
          <p className="text-[11px] text-rose-700/80 mt-1 font-semibold truncate">Isolated / Quarantine</p>
        </div>

        {/* Active Alerts */}
        <div
          onClick={() => navigate('/alerts')}
          className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-2xs hover:shadow-md hover:border-rose-300 cursor-pointer transition-all duration-150 col-span-2 sm:col-span-1"
        >
          <div className="flex items-center justify-between text-xs font-semibold text-rose-700 uppercase tracking-wider">
            <span>Active Alerts</span>
            <div className="p-1.5 rounded-lg bg-rose-50 text-rose-600">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {MOCK_SUMMARY_METRICS.activeAlerts}
          </div>
          <p className="text-[11px] text-rose-600 mt-1 font-semibold truncate">3 Urgent Attention</p>
        </div>
      </div>

      {/* 3. AI Disease Detection Section (Interactive Dropzone + Camera Area + Analyze CTA) */}
      <div className="bg-white rounded-2xl border-2 border-emerald-500/30 p-5 sm:p-7 shadow-sm">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-5">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                <ScanEye className="w-5 h-5 text-emerald-700" />
              </span>
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                AI Multimodal Disease Screening & Triage
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-emerald-50 text-emerald-700 border border-emerald-200">
                AniCare-Net v1.2
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-500">
              Upload dermatological lesions, muzzle swabs, or eye discharge images for instant AI-assisted differential diagnosis.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span>ResNet-50 Vision + Clinical BERT</span>
          </div>
        </div>

        {/* Large Photo Upload / Camera Area */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
          {/* Dropzone Container */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`lg:col-span-8 rounded-xl border-2 border-dashed p-6 flex flex-col items-center justify-center text-center transition-all ${
              dragActive
                ? 'border-emerald-600 bg-emerald-50/70 scale-[0.99]'
                : 'border-slate-300 bg-slate-50/70 hover:border-emerald-500 hover:bg-slate-50'
            }`}
          >
            <div className="flex flex-col sm:flex-row items-center gap-6 w-full justify-center">
              {/* Preview image */}
              <div className="relative w-36 h-36 rounded-xl overflow-hidden border border-slate-300 shadow-xs flex-shrink-0 group">
                <img
                  src={dashPreviewImage}
                  alt="Inspection lesion sample"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-slate-900/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-[11px] text-white font-medium p-2">
                  Sample Lesion Loaded
                </div>
              </div>

              {/* Instructions & CTA */}
              <div className="text-left space-y-2 max-w-sm">
                <div className="flex items-center gap-2">
                  <UploadCloud className="w-5 h-5 text-emerald-600" />
                  <span className="text-sm font-bold text-slate-800">
                    Drag and drop inspection photo here
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">
                  Supports high-resolution dermatological photos of lesions, skin nodules, muzzle erosions, or CMT milk trays.
                </p>
                <div className="pt-2 flex items-center gap-2 flex-wrap">
                  <Button
                    variant="outline"
                    size="sm"
                    icon={Camera}
                    onClick={() => {
                      showToast('Simulating device camera activation for livestock scan...');
                      navigate('/disease-detection');
                    }}
                  >
                    Open Camera UI
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setDashPreviewImage('https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?auto=format&fit=crop&w=600&q=80');
                      showToast('Swapped to Bovine Respiratory inspection sample.');
                    }}
                  >
                    Load Sample Photo
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Action & Info Box */}
          <div className="lg:col-span-4 bg-slate-900 text-white rounded-xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs text-emerald-400 font-mono mb-2">
                <span>AI PREDICTION ENGINE</span>
                <span>ONLINE</span>
              </div>
              <h3 className="font-bold text-base text-white">
                Pre-Clinical Anomaly Scan
              </h3>
              <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                AniCare AI extracts feature embeddings and cross-matches syndromic ontology with 94.6% benchmark prototype accuracy.
              </p>
            </div>

            <div className="pt-4 space-y-2">
              <Button
                variant="primary"
                size="md"
                className="w-full shadow-lg shadow-emerald-600/30 font-bold"
                icon={ScanEye}
                onClick={() => navigate('/disease-detection')}
              >
                Analyze Animal Health &rarr;
              </Button>
              <p className="text-[10px] text-center text-slate-400">
                SIH Demo &bull; Synthetic inference representation
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Recent Animal Health & 7. Quick Actions Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left (8 cols): Recent Animal Health */}
        <div className="lg:col-span-8">
          <Card
            title="Recent Animal Health Checkups"
            subtitle="Latest individual telemetry records and clinical status"
            icon={PawPrint}
            actions={
              <Link
                to="/animals"
                className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
              >
                Full Registry ({MOCK_ANIMALS.length}) <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            }
            bodyClassName="p-0"
          >
            <div className="divide-y divide-slate-100">
              {recentAnimals.map((animal) => (
                <div
                  key={animal.id}
                  onClick={() => navigate(`/animals?tag=${animal.tag}`)}
                  className="p-4 hover:bg-slate-50 transition-colors flex items-center justify-between gap-3 cursor-pointer group"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <img
                      src={animal.avatar}
                      alt={animal.name}
                      className="w-12 h-12 rounded-xl object-cover border border-slate-200 flex-shrink-0 group-hover:scale-105 transition-transform"
                    />
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="font-bold text-sm text-slate-900 group-hover:text-emerald-700 transition-colors truncate">
                          {animal.name}
                        </h4>
                        <span className="font-mono text-xs text-slate-500 font-semibold bg-slate-100 px-1.5 py-0.2 rounded">
                          {animal.tag}
                        </span>
                        <Badge
                          variant={
                            animal.healthStatus === 'Critical'
                              ? 'critical'
                              : animal.healthStatus === 'At Risk' || animal.healthStatus === 'Under Observation'
                              ? 'warning'
                              : animal.healthStatus === 'Recovering'
                              ? 'info'
                              : 'success'
                          }
                          size="sm"
                          pulse={animal.healthStatus === 'Critical'}
                        >
                          {animal.healthStatus}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">
                        {animal.species} &bull; {animal.breed} &bull; {animal.location}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        Last check: {animal.lastCheck}
                      </p>
                    </div>
                  </div>

                  {/* Right side: Risk score & temp */}
                  <div className="text-right flex-shrink-0 space-y-1">
                    <div className="flex items-center gap-1 justify-end text-xs font-bold text-slate-800">
                      <Thermometer className="w-3.5 h-3.5 text-rose-500" />
                      <span>{animal.temperature}</span>
                    </div>
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${
                        animal.riskScore >= 80
                          ? 'bg-rose-100 text-rose-700'
                          : animal.riskScore >= 50
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      Risk: {animal.riskScore}/100
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right (4 cols): 7. Quick Actions */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
            <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider text-slate-400">
              Quick Actions
            </h3>
            <div className="space-y-2.5">
              {/* Add Animal */}
              <button
                onClick={() => setShowAddAnimalModal(true)}
                className="w-full p-3 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-emerald-50 text-emerald-700 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                    <PlusCircle className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">Add Animal</p>
                    <p className="text-[11px] text-slate-500">Register new RFID livestock head</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600" />
              </button>

              {/* Scan Animal */}
              <button
                onClick={() => navigate('/disease-detection')}
                className="w-full p-3 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-50 text-indigo-700 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                    <ScanEye className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">Scan Animal</p>
                    <p className="text-[11px] text-slate-500">Run multimodal triage screening</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
              </button>

              {/* View Health Report */}
              <button
                onClick={() => navigate('/reports')}
                className="w-full p-3 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-sky-50 text-sky-700 group-hover:bg-sky-600 group-hover:text-white transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">View Health Report</p>
                    <p className="text-[11px] text-slate-500">Inspect verified lab assays & dossiers</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-sky-600" />
              </button>

              {/* Contact Veterinarian */}
              <button
                onClick={() => setShowContactVetModal(true)}
                className="w-full p-3 rounded-xl border border-slate-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition-all flex items-center justify-between group text-left"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-rose-50 text-rose-700 group-hover:bg-rose-600 group-hover:text-white transition-colors">
                    <PhoneCall className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">Contact Veterinarian</p>
                    <p className="text-[11px] text-slate-500">Call on-duty polyclinic specialist</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-rose-600" />
              </button>
            </div>
          </div>

          {/* Quick Notice Card */}
          <div className="bg-slate-50 rounded-xl border border-slate-200 p-4 text-xs text-slate-600 space-y-1.5">
            <span className="font-bold text-slate-800 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-emerald-600" />
              SIH 2026 Hackathon Prototype
            </span>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              All data and AI outputs shown are synthetic simulations. Real ML pipeline integration ready for FastAPI + PyTorch backend.
            </p>
          </div>
        </div>
      </div>

      {/* 5. Disease Risk Overview (Charts showing healthy/at-risk/critical + Trends) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left (4 cols): Health Distribution Gauge & Breakdown */}
        <div className="lg:col-span-4">
          <Card
            title="Disease Risk Distribution"
            subtitle="Overall herd biosecurity segmentation"
            icon={Activity}
          >
            <HealthScoreGauge
              score={MOCK_SUMMARY_METRICS.herdHealthIndex}
              label="Herd Biosecurity Score"
              subtitle="1,420 livestock units monitored"
            />
            {/* Visual breakdown progress bars */}
            <div className="mt-4 pt-4 border-t border-slate-100 space-y-2 text-xs">
              <div>
                <div className="flex justify-between font-medium">
                  <span className="text-emerald-700 font-semibold">Healthy (1,318)</span>
                  <span className="text-slate-600">92.8%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-1">
                  <div className="bg-emerald-500 h-full" style={{ width: '92.8%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium">
                  <span className="text-amber-700 font-semibold">At Risk (83)</span>
                  <span className="text-slate-600">5.8%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-1">
                  <div className="bg-amber-500 h-full" style={{ width: '5.8%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium">
                  <span className="text-rose-700 font-semibold">Critical / Isolated (19)</span>
                  <span className="text-slate-600">1.4%</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-1">
                  <div className="bg-rose-500 h-full" style={{ width: '1.4%' }} />
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Right (8 cols): Recent Disease Trends */}
        <div className="lg:col-span-8">
          <Card
            title="Recent Disease Occurrence Trends"
            subtitle="6-Month syndromic epidemiological tracking (May - Oct 2026)"
            icon={TrendingUp}
            actions={
              <Link
                to="/analytics"
                className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
              >
                Deep Analytics <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            }
          >
            <DiseasePrevalenceChart />
          </Card>
        </div>
      </div>

      {/* 6. Alerts Section (Critical health alerts, follow-up reminders, vet review notifications) */}
      <Card
        title="Active Surveillance Alerts & Reminders"
        subtitle="Prioritized epizootic alarms, follow-up reminders, and veterinary review triggers"
        icon={AlertTriangle}
        actions={
          <Link
            to="/alerts"
            className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center gap-1"
          >
            All Alerts ({MOCK_ALERTS.length}) <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        }
        bodyClassName="p-0"
      >
        <div className="divide-y divide-slate-100">
          {MOCK_ALERTS.slice(0, 4).map((alert) => (
            <div
              key={alert.id}
              className="p-4 sm:p-5 hover:bg-slate-50 transition-colors flex items-start justify-between gap-4"
            >
              <div className="flex items-start gap-3.5 min-w-0">
                <div
                  className={`p-2 rounded-xl flex-shrink-0 mt-0.5 ${
                    alert.severity === 'Critical'
                      ? 'bg-rose-100 text-rose-700 border border-rose-200'
                      : alert.severity === 'High'
                      ? 'bg-rose-50 text-rose-600 border border-rose-200'
                      : alert.severity === 'Medium'
                      ? 'bg-amber-50 text-amber-600 border border-amber-200'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  <AlertTriangle className="w-4 h-4" />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                      {alert.id}
                    </span>
                    <h4 className="font-bold text-sm text-slate-900 truncate">
                      {alert.title}
                    </h4>
                    <Badge
                      variant={
                        alert.severity === 'Critical'
                          ? 'critical'
                          : alert.severity === 'High'
                          ? 'danger'
                          : alert.severity === 'Medium'
                          ? 'warning'
                          : 'neutral'
                      }
                      size="sm"
                      pulse={alert.severity === 'Critical'}
                    >
                      {alert.alertType || alert.severity}
                    </Badge>
                  </div>

                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">
                    {alert.description}
                  </p>

                  <div className="mt-2 flex items-center gap-3 text-[11px] text-slate-400 flex-wrap">
                    <span className="font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                      {alert.affectedTag}
                    </span>
                    <span>&bull;</span>
                    <span>{alert.location}</span>
                    <span>&bull;</span>
                    <span>{alert.timestamp}</span>
                  </div>
                </div>
              </div>

              {/* Action trigger */}
              <div className="text-right flex-shrink-0 flex flex-col items-end gap-1.5">
                <span className="text-[11px] font-semibold text-emerald-700">
                  {alert.dispatchStatus}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate('/alerts')}
                >
                  Review Alert
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Add Animal Modal */}
      {showAddAnimalModal && (
        <Modal
          isOpen={showAddAnimalModal}
          onClose={() => setShowAddAnimalModal(false)}
          title="Register New Livestock Animal"
          subtitle="Enrol into National Animal Disease Surveillance Registry"
          maxWidth="max-w-md"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowAddAnimalModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleAddAnimalSubmit}>
                Save to Central Registry
              </Button>
            </>
          }
        >
          <form onSubmit={handleAddAnimalSubmit} className="space-y-3.5 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">RFID / Ear Tag Number *</label>
              <input
                type="text"
                required
                placeholder="e.g. TAG-9901"
                value={newAnimalData.tag}
                onChange={(e) => setNewAnimalData({ ...newAnimalData, tag: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Animal Name / Identification</label>
              <input
                type="text"
                placeholder="e.g. Kasturi"
                value={newAnimalData.name}
                onChange={(e) => setNewAnimalData({ ...newAnimalData, name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Species</label>
                <select
                  value={newAnimalData.species}
                  onChange={(e) => setNewAnimalData({ ...newAnimalData, species: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                >
                  <option>Cattle</option>
                  <option>Buffalo</option>
                  <option>Goat</option>
                  <option>Sheep</option>
                </select>
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Assigned Shed</label>
                <input
                  type="text"
                  value={newAnimalData.location}
                  onChange={(e) => setNewAnimalData({ ...newAnimalData, location: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
            </div>
          </form>
        </Modal>
      )}

      {/* Contact Veterinarian Modal */}
      {showContactVetModal && (
        <Modal
          isOpen={showContactVetModal}
          onClose={() => setShowContactVetModal(false)}
          title="On-Duty Veterinary Emergency Dispatch"
          subtitle="District Polyclinic Field Officers On Standby"
          maxWidth="max-w-lg"
          footer={
            <Button variant="outline" size="sm" onClick={() => setShowContactVetModal(false)}>
              Close
            </Button>
          }
        >
          <div className="space-y-3 text-xs">
            {MOCK_VETS.map((vet) => (
              <div
                key={vet.id}
                className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3">
                  <img
                    src={vet.avatar}
                    alt={vet.name}
                    className="w-10 h-10 rounded-full object-cover border border-slate-300"
                  />
                  <div>
                    <h5 className="font-bold text-slate-900">{vet.name}</h5>
                    <p className="text-[11px] text-slate-500">{vet.specialization}</p>
                    <p className="text-[10px] text-emerald-700 font-semibold">{vet.nextAvailableSlot}</p>
                  </div>
                </div>
                <Button
                  variant="primary"
                  size="sm"
                  icon={PhoneCall}
                  onClick={() => {
                    showToast(`Simulated: Dialing ${vet.name} (${vet.contactPhone})...`);
                    setShowContactVetModal(false);
                  }}
                >
                  Call
                </Button>
              </div>
            ))}
          </div>
        </Modal>
      )}
    </div>
  );
}
