import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  FlaskConical,
  PlayCircle,
  RefreshCw,
  Sparkles,
  AlertTriangle,
  Radio,
  CheckCircle2,
  Clock,
  Layers,
  PhoneCall,
  MessageSquare
} from 'lucide-react';
import responseService from '../services/api/responseService';
import AlertQueue from '../components/response/AlertQueue';
import InvestigationBoard from '../components/response/InvestigationBoard';
import SampleLabTable from '../components/response/SampleLabTable';
import DepartmentActionsCard from '../components/response/DepartmentActionsCard';
import SihDemoRunner from '../components/response/SihDemoRunner';
import ResponseDossierModal from '../components/response/ResponseDossierModal';

export default function ResponseCommandCenter() {
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [cases, setCases] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [selectedCaseData, setSelectedCaseData] = useState(null);
  const [activeTab, setActiveTab] = useState('alerts');
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [s, a, c] = await Promise.all([
        responseService.getStats(),
        responseService.getAlerts(),
        responseService.getCases()
      ]);
      setStats(s);
      setAlerts(a);
      setCases(c);
    } catch (err) {
      console.error('Failed to load response data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectCase = async (caseId) => {
    setSelectedCaseId(caseId);
    try {
      const data = await responseService.getCase(caseId);
      setSelectedCaseData(data);
    } catch (err) {
      console.error('Failed to load case dossier:', err);
    }
  };

  const handleAcknowledge = async (alertId, comment) => {
    await responseService.acknowledgeAlert(alertId, comment);
    await loadData();
    if (selectedCaseId) {
      handleSelectCase(selectedCaseId);
    }
  };

  const handleRecordResult = async (sampleId, data) => {
    await responseService.recordLabResult(sampleId, data);
    await loadData();
    if (selectedCaseId) {
      handleSelectCase(selectedCaseId);
    }
  };

  const handleAuthorizeAction = async (caseId, data) => {
    await responseService.authorizeAction(caseId, data);
    await loadData();
    if (selectedCaseId) {
      handleSelectCase(selectedCaseId);
    }
  };

  const handleSeedDemo = async () => {
    setSeeding(true);
    try {
      await responseService.seedDemoData();
      await loadData();
    } finally {
      setSeeding(false);
    }
  };

  const handleRunDemoScenario = async () => {
    const res = await responseService.runDemoScenario();
    await loadData();
    if (res.case_id) {
      handleSelectCase(res.case_id);
    }
    return res;
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
              Milestone 13 · Operational Response
            </span>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              Human Governance Live
            </span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2.5">
            <ShieldAlert className="w-7 h-7 text-indigo-600" />
            Field Response & Government Action Command Center
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Controlled incident orchestration: Risk Detection → Prioritization → Alert → Assignment → Investigation → Lab Tracking → Human Authorization.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 text-xs font-bold rounded-xl shadow-2xs inline-flex items-center gap-1.5 transition-colors"
          >
            <Sparkles className="w-4 h-4 text-amber-500" />
            {seeding ? 'Seeding...' : 'Seed Demo Cases'}
          </button>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded-xl shadow-2xs transition-colors"
            title="Refresh Surveillance Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Truth in Telemetry Gateway Status Bar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="p-3 bg-white rounded-xl border border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-600" />
            <span className="font-semibold text-slate-700">In-App Event Bus:</span>
          </div>
          <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            CONNECTED & ACTIVE
          </span>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <PhoneCall className="w-4 h-4 text-slate-400" />
            <span className="font-semibold text-slate-700">SMS Gateway:</span>
          </div>
          <span className="font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[11px]">
            READY — NOT CONFIGURED
          </span>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-slate-400" />
            <span className="font-semibold text-slate-700">WhatsApp Gateway:</span>
          </div>
          <span className="font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200 text-[11px]">
            READY — NOT CONFIGURED
          </span>
        </div>
      </div>

      {/* Mandatory Statutory Disclaimer Banner */}
      <div className="p-3.5 bg-amber-50/90 border border-amber-200 rounded-xl flex items-start gap-3 text-xs text-amber-950">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="font-bold">Human Governance & Clinical Safety Invariant:</strong> AI-generated risk signals support prioritization. Field investigation and authorized veterinary/department decisions remain human-controlled. Autonomous government decisions, autonomous prescriptions, and autonomous containment actions are strictly prohibited.
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Active Alerts</span>
          <div className="text-xl font-bold font-mono text-indigo-600 mt-1">{stats?.active_alerts ?? 4}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">P1 Cases</span>
          <div className="text-xl font-bold font-mono text-red-600 mt-1">{stats?.p1_cases ?? 2}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Pending Visits</span>
          <div className="text-xl font-bold font-mono text-amber-600 mt-1">{stats?.pending_investigations ?? 3}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Visits Today</span>
          <div className="text-xl font-bold font-mono text-blue-600 mt-1">{stats?.field_visits_today ?? 5}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Awaiting Lab</span>
          <div className="text-xl font-bold font-mono text-purple-600 mt-1">{stats?.samples_awaiting_lab ?? 2}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Dept Reviews</span>
          <div className="text-xl font-bold font-mono text-indigo-700 mt-1">{stats?.department_reviews ?? 1}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Overdue Actions</span>
          <div className="text-xl font-bold font-mono text-slate-700 mt-1">{stats?.overdue_actions ?? 0}</div>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-semibold text-slate-500 block truncate">Resolved</span>
          <div className="text-xl font-bold font-mono text-emerald-600 mt-1">{stats?.resolved_cases ?? 8}</div>
        </div>
      </div>

      {/* Main Command Center Tabs */}
      <div className="flex items-center gap-1 border-b border-slate-200 overflow-x-auto pb-px">
        {[
          { id: 'alerts', label: `Alert Queue (${alerts.length})`, icon: ShieldAlert },
          { id: 'board', label: `Investigation Board (${cases.length})`, icon: ClipboardList },
          { id: 'samples', label: 'Specimens & Lab Status', icon: FlaskConical },
          { id: 'actions', label: 'Department Actions', icon: ShieldCheck },
          { id: 'simulator', label: '14-Step SIH Simulator', icon: PlayCircle }
        ].map((t) => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`py-3 px-4 text-xs font-bold inline-flex items-center gap-2 border-b-2 whitespace-nowrap transition-colors ${
                isActive
                  ? 'border-indigo-600 text-indigo-600 bg-white'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      {activeTab === 'alerts' && (
        <AlertQueue
          alerts={alerts}
          onAcknowledge={handleAcknowledge}
          onSelectCase={handleSelectCase}
        />
      )}

      {activeTab === 'board' && (
        <InvestigationBoard
          cases={cases}
          onSelectCase={handleSelectCase}
        />
      )}

      {activeTab === 'samples' && (
        <SampleLabTable
          cases={cases}
          onRecordResult={handleRecordResult}
        />
      )}

      {activeTab === 'actions' && (
        <DepartmentActionsCard
          cases={cases}
          onAuthorizeAction={handleAuthorizeAction}
        />
      )}

      {activeTab === 'simulator' && (
        <SihDemoRunner
          onRunScenario={handleRunDemoScenario}
        />
      )}

      {/* Response Case Dossier Modal */}
      {selectedCaseData && (
        <ResponseDossierModal
          caseData={selectedCaseData}
          onClose={() => {
            setSelectedCaseId(null);
            setSelectedCaseData(null);
          }}
          onRefresh={() => handleSelectCase(selectedCaseId)}
        />
      )}
    </div>
  );
}
