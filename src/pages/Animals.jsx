import React, { useState, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  PawPrint,
  Plus,
  Filter,
  Search,
  Eye,
  Thermometer,
  Heart,
  Wind,
  ShieldCheck,
  AlertCircle,
  FileText,
  Clock,
  Sparkles,
  Download,
  Share2,
  CheckCircle2,
  SlidersHorizontal,
  Table,
  LayoutGrid,
  Calendar,
  Syringe,
  Activity,
  History,
  ShieldAlert,
  X,
  Stethoscope,
  ChevronRight
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import EmptyState from '../components/common/EmptyState';
import SearchInput from '../components/common/SearchInput';
import { MOCK_ANIMALS } from '../data/mockData';

export default function Animals() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Search & filter states
  const initialTag = searchParams.get('tag') || '';
  const initialStatus = searchParams.get('status') || 'All';
  const [searchQuery, setSearchQuery] = useState(initialTag);
  const [selectedSpecies, setSelectedSpecies] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState(initialStatus);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'table'

  // Modal states
  const [selectedAnimal, setSelectedAnimal] = useState(
    initialTag ? MOCK_ANIMALS.find((a) => a.tag === initialTag) || null : null
  );
  const [activeProfileTab, setActiveProfileTab] = useState('overview'); // 'overview' | 'timeline' | 'treatments' | 'vaccines' | 'ai'
  const [showAddModal, setShowAddModal] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  // New Animal Form state
  const [newAnimal, setNewAnimal] = useState({
    tag: '',
    name: '',
    species: 'Cattle',
    breed: 'Gir',
    gender: 'Female',
    age: '3.0 years',
    weight: '420 kg',
    location: 'Shed 01',
    healthStatus: 'Healthy',
    notes: ''
  });

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const speciesList = ['All', 'Cattle', 'Buffalo', 'Goat', 'Sheep'];
  const statusList = ['All', 'Healthy', 'At Risk', 'Under Observation', 'Quarantine', 'Critical', 'Recovering'];

  // Filtered animals
  const filteredAnimals = useMemo(() => {
    return MOCK_ANIMALS.filter((animal) => {
      const matchSearch =
        animal.tag.toLowerCase().includes(searchQuery.toLowerCase()) ||
        animal.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        animal.breed.toLowerCase().includes(searchQuery.toLowerCase()) ||
        animal.location.toLowerCase().includes(searchQuery.toLowerCase());

      const matchSpecies = selectedSpecies === 'All' || animal.species === selectedSpecies;
      const matchStatus =
        selectedStatus === 'All' ||
        animal.healthStatus === selectedStatus ||
        (selectedStatus === 'At Risk' && (animal.healthStatus === 'At Risk' || animal.healthStatus === 'Under Observation'));

      return matchSearch && matchSpecies && matchStatus;
    });
  }, [searchQuery, selectedSpecies, selectedStatus]);

  const handleRegisterAnimal = (e) => {
    e.preventDefault();
    showToast(`Simulation: Animal ${newAnimal.tag || 'New Tag'} registered to central ledger.`);
    setShowAddModal(false);
  };

  const getStatusVariant = (status) => {
    switch (status) {
      case 'Healthy':
        return 'success';
      case 'At Risk':
      case 'Under Observation':
        return 'warning';
      case 'Quarantine':
      case 'Critical':
        return 'critical';
      case 'Recovering':
        return 'info';
      default:
        return 'neutral';
    }
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
        title="Livestock & Animal Registry"
        subtitle="Individual RFID biometric tracking, multi-parameter health scoring, clinical history, and isolation records."
        badge={
          <Badge variant="neutral">
            {MOCK_ANIMALS.length} Monitored Livestock Units
          </Badge>
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              icon={Download}
              onClick={() => showToast('Simulating National Livestock Passport CSV export...')}
            >
              Export Registry
            </Button>
            <Button
              variant="primary"
              size="sm"
              icon={Plus}
              onClick={() => setShowAddModal(true)}
            >
              Register Animal
            </Button>
          </>
        }
      />

      {/* Filter and Search Bar Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          <div className="flex-1 max-w-md">
            <SearchInput
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by tag (TAG-8821), name, breed, or shed..."
            />
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 self-end md:self-center">
            <span className="text-xs text-slate-400 font-medium hidden sm:inline">View Mode:</span>
            <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-1.5 rounded-md transition-all ${
                  viewMode === 'grid'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Grid cards view"
              >
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`p-1.5 rounded-md transition-all ${
                  viewMode === 'table'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
                title="Data table view"
              >
                <Table className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Species & Health-Status Filters */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-100">
          {/* Species filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            <span className="text-xs font-bold text-slate-400 uppercase mr-1">Species:</span>
            {speciesList.map((sp) => (
              <button
                key={sp}
                onClick={() => setSelectedSpecies(sp)}
                className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors whitespace-nowrap ${
                  selectedSpecies === sp
                    ? 'bg-emerald-600 text-white font-semibold shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {sp}
              </button>
            ))}
          </div>

          {/* Health status filters */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            <span className="text-xs font-bold text-slate-400 uppercase mr-1">Health:</span>
            {statusList.map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors whitespace-nowrap ${
                  selectedStatus === st
                    ? 'bg-slate-900 text-white font-semibold shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Animal Content */}
      {filteredAnimals.length === 0 ? (
        <EmptyState
          title="No livestock records matched"
          description={`No records found matching query "${searchQuery}" with selected species and status filters.`}
          actionLabel="Clear Filters"
          onAction={() => {
            setSearchQuery('');
            setSelectedSpecies('All');
            setSelectedStatus('All');
          }}
        />
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {filteredAnimals.map((animal) => (
            <div
              key={animal.id}
              onClick={() => {
                setSelectedAnimal(animal);
                setActiveProfileTab('overview');
              }}
              className="group bg-white rounded-xl border border-slate-200 hover:border-emerald-400 hover:shadow-lg transition-all duration-200 overflow-hidden cursor-pointer flex flex-col justify-between"
            >
              <div>
                {/* Photo & Tag Header */}
                <div className="relative h-44 overflow-hidden bg-slate-100">
                  <img
                    src={animal.avatar}
                    alt={animal.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2.5 left-2.5">
                    <span className="px-2 py-1 rounded-md bg-slate-900/80 backdrop-blur-md text-white text-xs font-mono font-bold">
                      {animal.tag}
                    </span>
                  </div>
                  <div className="absolute top-2.5 right-2.5">
                    <Badge variant={getStatusVariant(animal.healthStatus)} size="sm">
                      {animal.healthStatus}
                    </Badge>
                  </div>
                </div>

                {/* Details Content */}
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="font-bold text-base text-slate-900 group-hover:text-emerald-700 transition-colors">
                      {animal.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {animal.species} &bull; {animal.breed} &bull; {animal.gender}
                    </p>
                  </div>

                  {/* Vitals & Score Row */}
                  <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-xs">
                    <div className="flex items-center gap-1.5">
                      <Thermometer className="w-3.5 h-3.5 text-rose-500" />
                      <span className="text-slate-700 font-medium">{animal.temperature}</span>
                    </div>
                    <div className="text-right">
                      <span
                        className={`inline-block px-1.5 py-0.5 rounded text-[11px] font-bold ${
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

                  <div className="space-y-1 text-xs text-slate-500">
                    <p className="truncate">
                      <span className="font-semibold text-slate-700">Age:</span> {animal.age} &bull; <span className="font-semibold text-slate-700">Wt:</span> {animal.weight}
                    </p>
                    <p className="truncate">
                      <span className="font-semibold text-slate-700">Location:</span> {animal.location}
                    </p>
                  </div>

                  {animal.riskFactor && (
                    <div className="pt-2 border-t border-slate-100">
                      <p className="text-[11px] font-medium text-amber-800 bg-amber-50 px-2 py-1 rounded truncate">
                        {animal.riskFactor}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Card Footer */}
              <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  {animal.lastCheck}
                </span>
                <span className="text-emerald-700 font-semibold group-hover:underline flex items-center gap-0.5">
                  Inspect Profile &rarr;
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Table View */
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Animal ID & Name</th>
                  <th className="px-4 py-3">Species / Breed</th>
                  <th className="px-4 py-3">Age / Gender</th>
                  <th className="px-4 py-3">Health Status</th>
                  <th className="px-4 py-3">Risk Score</th>
                  <th className="px-4 py-3">Vitals (Temp)</th>
                  <th className="px-4 py-3">Last Check</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredAnimals.map((animal) => (
                  <tr
                    key={animal.id}
                    onClick={() => {
                      setSelectedAnimal(animal);
                      setActiveProfileTab('overview');
                    }}
                    className="hover:bg-slate-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <img
                          src={animal.avatar}
                          alt={animal.name}
                          className="w-10 h-10 rounded-lg object-cover flex-shrink-0"
                        />
                        <div>
                          <p className="font-bold text-slate-900">{animal.name}</p>
                          <p className="text-xs font-mono text-slate-500">{animal.tag}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-800">{animal.species}</p>
                      <p className="text-xs text-slate-400">{animal.breed}</p>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-700">
                      {animal.age} &bull; {animal.gender}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={getStatusVariant(animal.healthStatus)} size="sm">
                        {animal.healthStatus}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${
                          animal.riskScore >= 80
                            ? 'bg-rose-100 text-rose-700'
                            : animal.riskScore >= 50
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}
                      >
                        {animal.riskScore}/100
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold text-slate-800 text-xs">
                      {animal.temperature}
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {animal.lastCheck}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm">
                        View Profile
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Attractive Animal Profile Modal (Complete with Timeline, Symptoms, Reports, Treatments, Vaccines, AI History) */}
      {selectedAnimal && (
        <Modal
          isOpen={!!selectedAnimal}
          onClose={() => setSelectedAnimal(null)}
          title={`Animal Health Profile: ${selectedAnimal.name} (${selectedAnimal.tag})`}
          subtitle={`Registered ID: ${selectedAnimal.id} • ${selectedAnimal.farmUnit}`}
          maxWidth="max-w-4xl"
          footer={
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => showToast(`Simulated: Downloaded passport dossier for ${selectedAnimal.tag}`)}
              >
                Download Passport
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={Sparkles}
                onClick={() => {
                  const tag = selectedAnimal.tag;
                  setSelectedAnimal(null);
                  navigate(`/disease-detection?tag=${tag}`);
                }}
              >
                Scan with AI Triage
              </Button>
            </>
          }
        >
          <div className="space-y-5">
            {/* Top Snapshot Card */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <img
                src={selectedAnimal.avatar}
                alt={selectedAnimal.name}
                className="w-24 h-24 rounded-xl object-cover border border-slate-300 flex-shrink-0 shadow-xs"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-xl font-bold text-slate-900">{selectedAnimal.name}</h3>
                  <span className="font-mono text-xs bg-slate-200 px-2 py-0.5 rounded text-slate-800 font-bold">
                    {selectedAnimal.tag}
                  </span>
                  <Badge variant={getStatusVariant(selectedAnimal.healthStatus)}>
                    {selectedAnimal.healthStatus}
                  </Badge>
                  <span className="text-xs font-bold text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                    Risk Score: {selectedAnimal.riskScore}/100
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  {selectedAnimal.species} &bull; {selectedAnimal.breed} &bull; Gender: {selectedAnimal.gender} &bull; Age: {selectedAnimal.age} &bull; Weight: {selectedAnimal.weight}
                </p>
                <div className="mt-2 flex items-center gap-4 text-xs text-slate-600 flex-wrap">
                  <span><strong>Location:</strong> {selectedAnimal.location}</span>
                  <span><strong>Last Check:</strong> {selectedAnimal.lastCheck}</span>
                  <span><strong>Core Temp:</strong> {selectedAnimal.temperature}</span>
                </div>
              </div>
            </div>

            {/* Profile Tab Navigation */}
            <div className="flex items-center gap-1.5 border-b border-slate-200 overflow-x-auto pb-1 text-xs">
              {[
                { id: 'overview', label: 'Vitals & Symptoms', icon: Activity },
                { id: 'timeline', label: 'Health Timeline', icon: History },
                { id: 'treatments', label: 'Treatments & Rx', icon: Stethoscope },
                { id: 'vaccines', label: 'Vaccination Records', icon: Syringe },
                { id: 'ai', label: 'AI Analysis History', icon: Sparkles }
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeProfileTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveProfileTab(tab.id)}
                    className={`px-3 py-2 rounded-t-lg font-medium transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                      isActive
                        ? 'border-b-2 border-emerald-600 text-emerald-800 font-bold bg-emerald-50/50'
                        : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab 1: Vitals & Symptoms Overview */}
            {activeProfileTab === 'overview' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                {/* 4-Box Vitals Grid */}
                <div>
                  <h4 className="font-bold text-slate-500 uppercase tracking-wider mb-2">
                    IoT Ruminal & Parlor Telemetry (Last 24 Hours)
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    <div className="p-3 bg-white border border-slate-200 rounded-xl">
                      <span className="text-slate-400 block">Body Temperature</span>
                      <span className="text-base font-bold text-rose-600">{selectedAnimal.temperature}</span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">Norm: 101.5°F</span>
                    </div>
                    <div className="p-3 bg-white border border-slate-200 rounded-xl">
                      <span className="text-slate-400 block">Heart Rate</span>
                      <span className="text-base font-bold text-slate-900">{selectedAnimal.heartRate}</span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">Norm: 60-80 bpm</span>
                    </div>
                    <div className="p-3 bg-white border border-slate-200 rounded-xl">
                      <span className="text-slate-400 block">Rumination</span>
                      <span className="text-base font-bold text-slate-900">{selectedAnimal.ruminationTime}</span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">Target: 450+ min</span>
                    </div>
                    <div className="p-3 bg-white border border-slate-200 rounded-xl">
                      <span className="text-slate-400 block">Milk Yield / State</span>
                      <span className="text-base font-bold text-slate-900">{selectedAnimal.milkYield}</span>
                      <span className="text-[10px] text-slate-400 block mt-0.5">{selectedAnimal.appetite}</span>
                    </div>
                  </div>
                </div>

                {/* Detected Symptoms List */}
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
                  <h4 className="font-bold text-slate-800 uppercase tracking-wide">
                    Presenting Clinical Symptoms & Observations:
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {selectedAnimal.symptoms && selectedAnimal.symptoms.length > 0 ? (
                      selectedAnimal.symptoms.map((sym, i) => (
                        <div key={i} className="flex items-center gap-2 p-2 bg-white rounded-lg border border-slate-200 text-slate-700">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                          <span>{sym}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-400 italic">No adverse symptoms logged.</p>
                    )}
                  </div>
                </div>

                {/* Field Notes */}
                <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-xl text-amber-900">
                  <span className="font-bold block uppercase text-[10px]">Veterinary Examiner Notes:</span>
                  <p className="mt-1 leading-relaxed">{selectedAnimal.notes}</p>
                </div>
              </div>
            )}

            {/* Tab 2: Health Timeline */}
            {activeProfileTab === 'timeline' && (
              <div className="space-y-3 text-xs animate-in fade-in">
                <h4 className="font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Historical Chronology & Clinical Events
                </h4>
                {selectedAnimal.healthTimeline && selectedAnimal.healthTimeline.length > 0 ? (
                  <div className="relative pl-6 space-y-4 border-l-2 border-slate-200 ml-3">
                    {selectedAnimal.healthTimeline.map((item, idx) => (
                      <div key={idx} className="relative group">
                        <div className={`absolute -left-[31px] top-0 w-4 h-4 rounded-full border-2 border-white ${
                          item.severity === 'Critical' ? 'bg-rose-500' : item.severity === 'Warning' ? 'bg-amber-500' : 'bg-emerald-500'
                        }`} />
                        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{item.date}</span>
                            <Badge variant={item.severity === 'Critical' ? 'danger' : item.severity === 'Warning' ? 'warning' : 'success'} size="sm">
                              {item.severity}
                            </Badge>
                          </div>
                          <p className="text-slate-600 mt-1">{item.event}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No prior timeline events" description="This animal has a normal baseline history." />
                )}
              </div>
            )}

            {/* Tab 3: Treatments & Rx */}
            {activeProfileTab === 'treatments' && (
              <div className="space-y-3 text-xs animate-in fade-in">
                <h4 className="font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Administered Treatments & Medical Regimens
                </h4>
                {selectedAnimal.treatments && selectedAnimal.treatments.length > 0 ? (
                  <div className="space-y-2.5">
                    {selectedAnimal.treatments.map((tr, i) => (
                      <div key={i} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900 text-sm">{tr.medicine}</span>
                            <Badge variant={tr.status === 'Active' ? 'warning' : 'success'} size="sm">
                              {tr.status}
                            </Badge>
                          </div>
                          <p className="text-slate-600">
                            <strong>Dosage:</strong> {tr.dosage} &bull; <strong>Prescriber:</strong> {tr.prescribedBy}
                          </p>
                          {tr.requiresVetApproval && (
                            <p className="text-[10px] text-amber-700 font-semibold">
                              &bull; Verified Prescription: Requires licensed veterinary oversight.
                            </p>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-400">{tr.date}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No active treatments" description="No active or past medical treatments recorded for this animal." />
                )}
              </div>
            )}

            {/* Tab 4: Vaccination Records */}
            {activeProfileTab === 'vaccines' && (
              <div className="space-y-3 text-xs animate-in fade-in">
                <h4 className="font-bold text-slate-500 uppercase tracking-wider mb-2">
                  National Prophylaxis & NADCP Vaccine Records
                </h4>
                {selectedAnimal.vaccinations && selectedAnimal.vaccinations.length > 0 ? (
                  <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl overflow-hidden bg-white">
                    {selectedAnimal.vaccinations.map((vac, i) => (
                      <div key={i} className="p-3 flex items-center justify-between">
                        <div>
                          <p className="font-bold text-slate-800">{vac.name}</p>
                          <p className="text-[11px] text-slate-400 font-mono">Batch: {vac.batch} &bull; Date: {vac.date}</p>
                        </div>
                        <Badge variant={vac.status === 'Valid' ? 'success' : 'warning'} size="sm">
                          {vac.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No vaccination records" description="Vaccination records are pending synchronization with the NADCP portal." />
                )}
              </div>
            )}

            {/* Tab 5: AI Analysis History */}
            {activeProfileTab === 'ai' && (
              <div className="space-y-3 text-xs animate-in fade-in">
                <h4 className="font-bold text-slate-500 uppercase tracking-wider mb-2">
                  Historical AI Screening Runs
                </h4>
                {selectedAnimal.aiHistory && selectedAnimal.aiHistory.length > 0 ? (
                  <div className="space-y-2">
                    {selectedAnimal.aiHistory.map((ai, i) => (
                      <div key={i} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900">{ai.predictedCondition}</span>
                            <Badge variant={ai.risk === 'HIGH' ? 'danger' : 'success'} size="sm">
                              {ai.risk} RISK
                            </Badge>
                          </div>
                          <p className="text-slate-500 text-[11px] mt-0.5">
                            {ai.scanType} &bull; Date: {ai.date}
                          </p>
                        </div>
                        <div className="text-right">
                          <span className="font-mono font-bold text-emerald-700 text-sm">
                            {ai.confidence}%
                          </span>
                          <p className="text-[10px] text-slate-400">{ai.status}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <EmptyState title="No AI screenings logged" description="Click 'Scan with AI Triage' to perform the first multimodal evaluation." />
                )}
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Add Animal Registration Modal */}
      {showAddModal && (
        <Modal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          title="Register New Livestock Animal"
          subtitle="Enrol into National Animal Disease Surveillance Registry"
          maxWidth="max-w-xl"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleRegisterAnimal}>
                Save to Registry
              </Button>
            </>
          }
        >
          <form onSubmit={handleRegisterAnimal} className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  RFID / Ear Tag Number *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TAG-9988"
                  value={newAnimal.tag}
                  onChange={(e) => setNewAnimal({ ...newAnimal, tag: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Name / Identification Label
                </label>
                <input
                  type="text"
                  placeholder="e.g. Kamala"
                  value={newAnimal.name}
                  onChange={(e) => setNewAnimal({ ...newAnimal, name: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Species</label>
                <select
                  value={newAnimal.species}
                  onChange={(e) => setNewAnimal({ ...newAnimal, species: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                >
                  <option>Cattle</option>
                  <option>Buffalo</option>
                  <option>Goat</option>
                  <option>Sheep</option>
                </select>
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Breed</label>
                <input
                  type="text"
                  value={newAnimal.breed}
                  onChange={(e) => setNewAnimal({ ...newAnimal, breed: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Gender</label>
                <select
                  value={newAnimal.gender}
                  onChange={(e) => setNewAnimal({ ...newAnimal, gender: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                >
                  <option>Female</option>
                  <option>Male</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Age</label>
                <input
                  type="text"
                  value={newAnimal.age}
                  onChange={(e) => setNewAnimal({ ...newAnimal, age: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Weight</label>
                <input
                  type="text"
                  value={newAnimal.weight}
                  onChange={(e) => setNewAnimal({ ...newAnimal, weight: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Shed Location</label>
                <input
                  type="text"
                  value={newAnimal.location}
                  onChange={(e) => setNewAnimal({ ...newAnimal, location: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                />
              </div>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Initial Health Status</label>
              <select
                value={newAnimal.healthStatus}
                onChange={(e) => setNewAnimal({ ...newAnimal, healthStatus: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
              >
                <option>Healthy</option>
                <option>At Risk</option>
                <option>Under Observation</option>
                <option>Quarantine</option>
              </select>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
