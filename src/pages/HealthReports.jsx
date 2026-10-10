import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Download,
  Plus,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  User,
  ShieldCheck,
  Stethoscope,
  Printer,
  Share2,
  FileSpreadsheet,
  Clock,
  Sparkles,
  ShieldAlert,
  ChevronRight,
  Eye,
  Award,
  Layers,
  History,
  RefreshCw,
  Tag,
  Activity,
  ScanEye
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import SearchInput from '../components/common/SearchInput';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { MOCK_HEALTH_REPORTS, DEMO_DISCLAIMER } from '../data/mockData';
import { detectionService } from '../services/api/detectionService';

export default function HealthReports() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('reports'); // 'reports' | 'history'

  // Diagnostic Reports state
  const [searchQuery, setSearchQuery] = useState('');
  const [filterContagious, setFilterContagious] = useState('All'); // 'All' | 'Contagious' | 'Non-Contagious'
  const [selectedReport, setSelectedReport] = useState(MOCK_HEALTH_REPORTS[0]);
  const [showDossierModal, setShowDossierModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // Past Screenings History state
  const [historyItems, setHistoryItems] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historySearch, setHistorySearch] = useState('');
  const [historySpeciesFilter, setHistorySpeciesFilter] = useState('All');
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Fetch history when tab changes to 'history'
  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await detectionService.getHistory();
      if (res && res.items) {
        setHistoryItems(res.items);
      } else if (Array.isArray(res)) {
        setHistoryItems(res);
      }
    } catch (err) {
      console.error('Failed to load assessment history:', err);
      showToast('Could not reach backend history; displaying offline cached records.');
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'history' && historyItems.length === 0) {
      loadHistory();
    }
  }, [activeTab]);

  const filteredReports = MOCK_HEALTH_REPORTS.filter((report) => {
    const matchesSearch =
      report.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.animalName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.provisionalDiagnosis.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.veterinarian.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesContagious =
      filterContagious === 'All' ||
      (filterContagious === 'Contagious' && report.isContagious) ||
      (filterContagious === 'Non-Contagious' && !report.isContagious);

    return matchesSearch && matchesContagious;
  });

  const filteredHistory = historyItems.filter((item) => {
    const matchesSearch =
      (item.animal_id || '').toLowerCase().includes(historySearch.toLowerCase()) ||
      (item.assessment_id || '').toLowerCase().includes(historySearch.toLowerCase()) ||
      (item.possible_condition || '').toLowerCase().includes(historySearch.toLowerCase()) ||
      (item.species || '').toLowerCase().includes(historySearch.toLowerCase());

    const matchesSpecies =
      historySpeciesFilter === 'All' ||
      (item.species || '').toLowerCase().includes(historySpeciesFilter.toLowerCase());

    return matchesSearch && matchesSpecies;
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-200">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-sm px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 border border-slate-700 animate-in slide-in-from-bottom-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Page Header */}
      <PageHeader
        title="Diagnostic Health Reports & Clinical Dossiers"
        subtitle="Certified veterinary diagnostic records, multimodal AI assessments, laboratory biomarker panels, and quarantine clearance certifications."
        badge={
          <Badge variant="neutral">
            {activeTab === 'reports' ? `${MOCK_HEALTH_REPORTS.length} Certified Records` : `${historyItems.length} AI Screenings`}
          </Badge>
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              icon={FileSpreadsheet}
              onClick={() => showToast('Simulating bulk diagnostic report export (CSV)...')}
            >
              Export CSV Ledger
            </Button>
            {activeTab === 'reports' ? (
              <Button
                variant="primary"
                size="sm"
                icon={Plus}
                onClick={() => setShowGenerateModal(true)}
              >
                New Clinical Report
              </Button>
            ) : (
              <Button
                variant="primary"
                size="sm"
                icon={ScanEye}
                onClick={() => navigate('/disease-detection')}
              >
                New AI Screening
              </Button>
            )}
          </>
        }
      />

      {/* Main Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto pb-1 text-xs">
        <button
          onClick={() => setActiveTab('reports')}
          className={`px-4 py-2.5 rounded-t-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'reports'
              ? 'border-b-2 border-emerald-600 text-emerald-900 bg-emerald-50/70 shadow-2xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Certified Veterinary Reports</span>
          <span className="ml-1 px-1.5 py-0.5 rounded-full text-[10px] bg-slate-200 text-slate-700">
            {MOCK_HEALTH_REPORTS.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`px-4 py-2.5 rounded-t-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
            activeTab === 'history'
              ? 'border-b-2 border-emerald-600 text-emerald-900 bg-emerald-50/70 shadow-2xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <History className="w-4 h-4" />
          <span>Animal Health History (Past Screenings)</span>
          <span className="ml-1 px-1.5 py-0.5 rounded-full text-[10px] bg-emerald-100 text-emerald-800 font-bold">
            Live
          </span>
        </button>
      </div>

      {/* TAB 1: CERTIFIED REPORTS */}
      {activeTab === 'reports' && (
        <div className="space-y-6">
          {/* Search and Filter Row */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex-1 max-w-md">
              <SearchInput
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by Report ID, patient name, diagnosis, or doctor..."
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-slate-400 uppercase">Filter:</span>
              {['All', 'Contagious', 'Non-Contagious'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilterContagious(f)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
                    filterContagious === f
                      ? 'bg-slate-900 text-white font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Reports Grid List */}
          {filteredReports.length === 0 ? (
            <EmptyState
              title="No diagnostic reports match filter"
              description="Try resetting your search query or selecting a different contagion filter."
              actionLabel="Reset Search"
              onAction={() => {
                setSearchQuery('');
                setFilterContagious('All');
              }}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {filteredReports.map((report) => (
                <div
                  key={report.id}
                  className="bg-white rounded-xl border border-slate-200 hover:border-slate-300 hover:shadow-md transition-all duration-200 p-5 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    {/* Header info */}
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <span className="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                          {report.id}
                        </span>
                        <h3 className="text-base font-bold text-slate-900 mt-1">
                          {report.animalName}
                        </h3>
                      </div>

                      <div className="flex items-center gap-1.5 flex-wrap justify-end">
                        {report.isContagious && (
                          <Badge variant="danger" size="sm" pulse>
                            Contagious (Bio-Risk)
                          </Badge>
                        )}
                        <Badge
                          variant={
                            report.riskLevel === 'CRITICAL'
                              ? 'critical'
                              : report.riskLevel === 'HIGH'
                              ? 'danger'
                              : report.riskLevel === 'MODERATE'
                              ? 'warning'
                              : 'success'
                          }
                          size="sm"
                        >
                          {report.riskLevel} Risk
                        </Badge>
                      </div>
                    </div>

                    {/* AI Assessment & Condition */}
                    <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-slate-400 font-semibold uppercase text-[10px]">
                          AI Provisional Diagnosis:
                        </span>
                        <span className="font-mono font-bold text-emerald-800 bg-emerald-50 px-1.5 py-0.2 rounded border border-emerald-200">
                          {report.confidence}% Confidence
                        </span>
                      </div>
                      <p className="font-bold text-slate-800 text-sm">
                        {report.provisionalDiagnosis}
                      </p>
                      <p className="text-[11px] text-slate-500">
                        Modality: {report.diagnosticType}
                      </p>
                    </div>

                    {/* Vitals & Telemetry */}
                    <div className="text-xs text-slate-600 bg-emerald-50/60 border border-emerald-100 p-2.5 rounded-lg font-mono">
                      {report.vitalsSummary}
                    </div>

                    <p className="text-xs text-slate-500 line-clamp-2">
                      <span className="font-semibold text-slate-700">Rx Protocol:</span> {report.recommendationSummary}
                    </p>
                  </div>

                  {/* Footer info & CTA buttons */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <div className="text-slate-500 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <span className="truncate max-w-[160px]">{report.veterinarian.split(',')[0]}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={Printer}
                        onClick={handlePrint}
                      >
                        Print
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        icon={Eye}
                        onClick={() => {
                          setSelectedReport(report);
                          setShowDossierModal(true);
                        }}
                      >
                        View Dossier
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: ANIMAL HEALTH HISTORY (PAST SCREENINGS) */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* Controls Bar */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex-1 max-w-md">
              <SearchInput
                value={historySearch}
                onChange={(e) => setHistorySearch(e.target.value)}
                placeholder="Filter by Tag ID (e.g. TAG-8821), condition, or species..."
              />
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-slate-400 uppercase">Species:</span>
              {['All', 'Cattle', 'Buffalo', 'Caprine', 'Poultry'].map((sp) => (
                <button
                  key={sp}
                  onClick={() => setHistorySpeciesFilter(sp)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
                    historySpeciesFilter === sp
                      ? 'bg-slate-900 text-white font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {sp}
                </button>
              ))}

              <Button
                variant="outline"
                size="sm"
                icon={RefreshCw}
                isLoading={historyLoading}
                onClick={loadHistory}
                className="ml-auto"
              >
                Refresh History
              </Button>
            </div>
          </div>

          {/* History Content */}
          {historyLoading ? (
            <div className="py-16 text-center">
              <LoadingSpinner message="Querying Central Health Screening Ledger..." subtext="Retrieving historical veterinary records from MongoDB persistence layer" />
            </div>
          ) : filteredHistory.length === 0 ? (
            <EmptyState
              title="No Past Screenings Found"
              description="No historical AI disease screenings match your search. Upload an animal photo on the Disease Detection page to record an assessment."
              actionLabel="Run New Disease Screening"
              onAction={() => navigate('/disease-detection')}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredHistory.map((item, idx) => (
                <div
                  key={item.assessment_id || idx}
                  className="bg-white rounded-xl border border-slate-200 hover:border-emerald-300 hover:shadow-md transition-all p-5 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    {/* Header with Tag & Risk */}
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-1.5">
                          <Tag className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="font-mono font-bold text-sm text-slate-900">
                            {item.animal_id || 'UNKNOWN-TAG'}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 font-medium">
                          {item.species || 'Livestock (Bovine)'}
                        </p>
                      </div>

                      <Badge
                        variant={
                          item.risk_level === 'CRITICAL'
                            ? 'critical'
                            : item.risk_level === 'HIGH'
                            ? 'danger'
                            : item.risk_level === 'MODERATE'
                            ? 'warning'
                            : 'success'
                        }
                        size="sm"
                      >
                        {item.risk_level || 'EVALUATED'}
                      </Badge>
                    </div>

                    {/* Condition & Confidence */}
                    <div className="p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Identified Condition:
                        </span>
                        <span className="font-mono font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                          {item.confidence ? `${item.confidence}%` : '85.0%'}
                        </span>
                      </div>
                      <p className="font-bold text-slate-900 text-sm leading-snug">
                        {item.possible_condition || 'Syndromic Evaluation'}
                      </p>
                    </div>

                    {/* Symptoms preview */}
                    {item.symptoms_detected && item.symptoms_detected.length > 0 && (
                      <div className="space-y-1 text-xs">
                        <span className="text-[10px] font-bold uppercase text-slate-400 block">
                          Reported Clinical Signs:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {item.symptoms_detected.slice(0, 3).map((sym, sIdx) => (
                            <span
                              key={sIdx}
                              className="px-2 py-0.5 bg-slate-100 text-slate-700 rounded text-[11px] font-medium"
                            >
                              {sym}
                            </span>
                          ))}
                          {item.symptoms_detected.length > 3 && (
                            <span className="px-1.5 py-0.5 bg-slate-200 text-slate-600 rounded text-[10px]">
                              +{item.symptoms_detected.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Summary explanation */}
                    {item.explanation && (
                      <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed bg-amber-50/50 p-2 rounded-lg border border-amber-100/60">
                        {item.explanation}
                      </p>
                    )}
                  </div>

                  {/* Footer with date & CTA */}
                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center gap-1 text-[11px]">
                      <Clock className="w-3.5 h-3.5" />
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                    </span>

                    <Button
                      variant="outline"
                      size="sm"
                      icon={Eye}
                      onClick={() => {
                        setSelectedHistoryItem(item);
                        setShowHistoryModal(true);
                      }}
                    >
                      Full Assessment
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* History Item Detail Modal */}
      {showHistoryModal && selectedHistoryItem && (
        <Modal
          isOpen={showHistoryModal}
          onClose={() => setShowHistoryModal(false)}
          title={`Clinical Screening Dossier: ${selectedHistoryItem.animal_id || 'ANIMAL'}`}
          subtitle={`Assessment ID: ${selectedHistoryItem.assessment_id || 'N/A'}`}
          maxWidth="max-w-2xl"
          footer={
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-slate-500">
                Logged via {selectedHistoryItem.source === 'api_inference' ? 'FastAPI Multimodal Pipeline' : 'Clinical Offline Ledger'}
              </span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setShowHistoryModal(false)}>
                  Close
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  icon={ScanEye}
                  onClick={() => {
                    setShowHistoryModal(false);
                    navigate('/disease-detection');
                  }}
                >
                  Re-Screen Animal
                </Button>
              </div>
            </div>
          }
        >
          <div className="space-y-4 text-xs">
            {/* Top Info Banner */}
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Animal Tag</span>
                <span className="font-bold text-slate-900 font-mono text-sm">{selectedHistoryItem.animal_id}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Species</span>
                <span className="font-bold text-slate-800">{selectedHistoryItem.species}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Risk Level</span>
                <Badge
                  variant={
                    selectedHistoryItem.risk_level === 'CRITICAL'
                      ? 'critical'
                      : selectedHistoryItem.risk_level === 'HIGH'
                      ? 'danger'
                      : 'warning'
                  }
                  size="sm"
                >
                  {selectedHistoryItem.risk_level}
                </Badge>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Confidence</span>
                <span className="font-mono font-bold text-emerald-700 text-sm">{selectedHistoryItem.confidence}%</span>
              </div>
            </div>

            {/* Suspected Condition & Clinical Explanation */}
            <div className="p-4 bg-emerald-50/60 rounded-xl border border-emerald-200 space-y-1.5">
              <h4 className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                Suspected Condition: {selectedHistoryItem.possible_condition}
              </h4>
              <p className="text-emerald-900 leading-relaxed text-xs">
                {selectedHistoryItem.explanation}
              </p>
            </div>

            {/* Symptoms Detected */}
            {selectedHistoryItem.symptoms_detected && selectedHistoryItem.symptoms_detected.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
                  Clinical Signs Documented:
                </h4>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 bg-slate-50 p-3 rounded-xl border border-slate-200">
                  {selectedHistoryItem.symptoms_detected.map((sym, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-slate-700">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                      <span>{sym}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Immediate Actions */}
            {selectedHistoryItem.recommended_immediate_actions && selectedHistoryItem.recommended_immediate_actions.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-bold text-slate-700 uppercase tracking-wider text-[11px]">
                  Recommended Veterinary & Husbandry Actions:
                </h4>
                <ul className="space-y-1.5 bg-amber-50/60 p-3.5 rounded-xl border border-amber-200">
                  {selectedHistoryItem.recommended_immediate_actions.map((act, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-amber-950">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-700 flex-shrink-0 mt-0.5" />
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Statutory Safety Disclaimer */}
            <div className="p-3 bg-slate-100 rounded-xl border border-slate-200 text-slate-600 text-[11px] leading-relaxed flex items-start gap-2">
              <ShieldAlert className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
              <span>
                <strong>Veterinary Advisory:</strong> This assessment was generated by AniCare AI multimodal screening. In compliance with statutory veterinary guidelines, AI findings are non-prescriptive assistive triage. A registered veterinary practitioner must conduct physical examination before pharmacological intervention.
              </span>
            </div>
          </div>
        </Modal>
      )}

      {/* Existing Certified Dossier Modal */}
      {showDossierModal && selectedReport && (
        <Modal
          isOpen={showDossierModal}
          onClose={() => setShowDossierModal(false)}
          title={`Clinical Diagnostic Dossier: ${selectedReport.id}`}
          subtitle={`Animal Patient: ${selectedReport.animalName} (${selectedReport.animalTag})`}
          maxWidth="max-w-2xl"
          footer={
            <div className="flex items-center justify-between w-full">
              <span className="text-xs text-slate-500">
                Certified by {selectedReport.veterinarian}
              </span>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" icon={Printer} onClick={handlePrint}>
                  Print
                </Button>
                <Button variant="outline" size="sm" onClick={() => setShowDossierModal(false)}>
                  Close
                </Button>
              </div>
            </div>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Exam Date</span>
                <span className="font-bold text-slate-800">{selectedReport.date}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Facility</span>
                <span className="font-bold text-slate-800 truncate block">{selectedReport.location}</span>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">Risk Tier</span>
                <Badge variant={selectedReport.riskLevel === 'CRITICAL' ? 'critical' : 'warning'} size="sm">
                  {selectedReport.riskLevel}
                </Badge>
              </div>
              <div>
                <span className="text-slate-400 block font-semibold text-[10px] uppercase">AI Confidence</span>
                <span className="font-mono font-bold text-emerald-700">{selectedReport.confidence}%</span>
              </div>
            </div>

            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
              <h4 className="font-bold text-emerald-950 text-sm mb-1">
                Provisional Diagnosis: {selectedReport.provisionalDiagnosis}
              </h4>
              <p className="text-emerald-900 leading-relaxed">
                Biomarker findings & symptoms: {selectedReport.symptomsObserved}
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
              <span className="font-bold text-slate-700 block uppercase text-[10px]">Vitals Telemetry:</span>
              <p className="font-mono text-slate-800">{selectedReport.vitalsSummary}</p>
            </div>

            <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-1">
              <span className="font-bold text-amber-900 block uppercase text-[10px]">Prescribed Clinical Protocol:</span>
              <p className="text-amber-950 leading-relaxed">{selectedReport.recommendationSummary}</p>
            </div>
          </div>
        </Modal>
      )}

      {/* New Report Form Modal */}
      {showGenerateModal && (
        <Modal
          isOpen={showGenerateModal}
          onClose={() => setShowGenerateModal(false)}
          title="Create New Veterinary Examination Report"
          subtitle="File clinical evaluation and record official diagnosis"
          maxWidth="max-w-xl"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowGenerateModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  showToast('Simulation: Diagnostic report committed to central veterinary ledger.');
                  setShowGenerateModal(false);
                }}
              >
                Commit Report
              </Button>
            </>
          }
        >
          <div className="space-y-3.5 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Livestock Tag ID *</label>
              <input
                type="text"
                placeholder="e.g. TAG-8821"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Attending Veterinarian</label>
                <input
                  type="text"
                  defaultValue="Dr. Arvind Verma, DAHD"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Risk Classification</label>
                <select className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white">
                  <option>CRITICAL</option>
                  <option>HIGH</option>
                  <option>MODERATE</option>
                  <option>LOW</option>
                </select>
              </div>
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Diagnosis</label>
              <input
                type="text"
                placeholder="e.g. Bovine Respiratory Disease Complex"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Treatment Protocol & Notes</label>
              <textarea
                rows={3}
                placeholder="Enter therapeutic actions, quarantine orders, follow-up dates..."
                className="w-full px-3 py-2 border border-slate-300 rounded-lg"
              />
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
