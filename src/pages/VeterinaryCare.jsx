import React, { useState, useEffect } from 'react';
import {
  ShieldPlus,
  PhoneCall,
  Video,
  Calendar,
  Clock,
  Award,
  CheckCircle2,
  AlertTriangle,
  Building,
  UserCheck,
  MapPin,
  ExternalLink,
  ShieldCheck,
  Activity,
  Syringe,
  Filter,
  Pill,
  FileText,
  AlertCircle,
  HelpCircle,
  Stethoscope,
  ChevronRight,
  Plus,
  Trash2,
  RefreshCw,
  Lock,
  Check,
  History,
  FileCheck2,
  X,
  Droplets,
  Languages,
  ShieldAlert,
  Info
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import {
  MOCK_VETS,
  MOCK_VET_CASES,
  MOCK_MEDICINES,
  CURRENT_USER
} from '../data/mockData';
import veterinaryService from '../services/api/veterinaryService';
import animalService from '../services/api/animalService';
import reminderService from '../services/api/reminderService';

export default function VeterinaryCare() {
  const [activeTab, setActiveTab] = useState('cases'); // 'cases' | 'medicines' | 'vets' | 'reminders' | 'quarantine'
  const [cases, setCases] = useState([]);

  // Reminders State
  const [reminders, setReminders] = useState([]);
  const [remindersLoading, setRemindersLoading] = useState(false);
  const [reminderFilter, setReminderFilter] = useState('ALL'); // 'ALL' | 'PENDING' | 'COMPLETED' | 'OVERDUE'
  const [showAddReminderModal, setShowAddReminderModal] = useState(false);
  const [newReminderForm, setNewReminderForm] = useState({
    title: '',
    animal_id: '',
    species: 'Cattle (Bovine)',
    due_date: new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0],
    reminder_type: 'VACCINATION',
    priority: 'HIGH',
    notes: '',
  });

  // Nearby Services State
  const [locatingUser, setLocatingUser] = useState(false);
  const [userLocationText, setUserLocationText] = useState('Anand Cluster #12, Gujarat (Default Farm Coordinates)');
  const [selectedDistrict, setSelectedDistrict] = useState('Anand');
  const [stats, setStats] = useState({
    pending_reviews: 0,
    high_critical_cases: 0,
    active_treatments: 0,
    follow_ups_due: 0,
    closed_cases: 0,
    total_cases: 0,
    vaccinations_due: 0,
    withdrawal_restrictions: 0,
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState('all');

  // Selected case and modal workflow states
  const [selectedCase, setSelectedCase] = useState(null);
  const [caseModalOpen, setCaseModalOpen] = useState(false);
  const [workflowTab, setWorkflowTab] = useState('overview');
  const [farmerLang, setFarmerLang] = useState('en'); // 'en' | 'hi'

  // Review Form State
  const [reviewForm, setReviewForm] = useState({
    decision: 'AI_ASSESSMENT_ACCEPTED',
    attending_vet_name: CURRENT_USER.name || 'Dr. Arvind Verma',
    vet_license_number: 'VET-REG-2024-88402',
    clinical_notes: '',
    confirmed_condition: '',
  });

  // Treatment Form State (Multi-Medicine)
  const [medicinesList, setMedicinesList] = useState([
    {
      medicine_name: 'Meloxicam Injection 5mg/ml',
      formulation: 'Injectable Solution',
      dosage: '0.5 mg/kg',
      frequency: 'Once Daily',
      duration: '3 days',
      route: 'Subcutaneous (SC)',
      instructions: 'Administer under aseptic conditions.',
    },
  ]);
  const [treatmentForm, setTreatmentForm] = useState({
    prescribing_vet_name: CURRENT_USER.name || 'Dr. Arvind Verma',
    prescribing_vet_license: 'VET-REG-2024-88402',
    supportive_care: 'Antiseptic lesion wash twice daily; maintain electrolyte rehydration.',
    isolation_required: true,
    isolation_instructions: 'Separate into insect-proof quarantine enclosure.',
    farmer_instructions: 'Provide clean drinking water. Do not modify drug doses without veterinary approval.',
  });

  // Prevention Plan Form State
  const [preventionForm, setPreventionForm] = useState({
    isolation_required: true,
    isolation_duration_days: 14,
    isolation_instructions: 'Quarantine in fly-barrier isolation pen.',
    hygiene_guidance: 'Disinfect feed troughs daily with 2% sodium hypochlorite solution.',
    vector_control: 'Apply synthetic pyrethroid spray on outer perimeter twice weekly.',
    animal_separation: 'Strict physical segregation from lactating cows and young calves.',
    monitoring_protocol: 'Record body temperature at 07:00 and 17:00 daily; log feed intake.',
    farmer_instructions: 'Observe daily feed intake and report any fresh skin eruptions immediately.',
  });

  // Withdrawal Period Form State
  const [withdrawalForm, setWithdrawalForm] = useState({
    withdrawal_type: 'milk',
    withdrawal_days: 5,
    withdrawal_start_date: new Date().toISOString().split('T')[0],
    source: 'Statutory Veterinary Prescription Formulary',
    verified: true,
  });

  // Vaccination Form State
  const [vaccinationsList, setVaccinationsList] = useState([]);
  const [vaccinationForm, setVaccinationForm] = useState({
    vaccine_name: 'Goat Pox Attenuated Vaccine',
    disease_target: 'Lumpy Skin Disease (Heterologous Protection)',
    date_administered: new Date().toISOString().split('T')[0],
    next_due_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    batch_number: 'BATCH-LSD-2026-09',
    administered_by: CURRENT_USER.name || 'Dr. Arvind Verma',
    notes: 'Administered 1ml SC lateral neck fold.',
  });

  // Follow-Up Form State
  const [followUpForm, setFollowUpForm] = useState({
    scheduled_date: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    notes: 'Re-evaluate skin nodule resolution and verify temperature stabilization.',
  });

  // Close Case Form State
  const [closeForm, setCloseForm] = useState({
    closing_notes: 'Full clinical recovery confirmed. Nodules resolved, appetite normal.',
    follow_up_completed: true,
  });

  // Consult Modal
  const [showConsultModal, setShowConsultModal] = useState(false);
  const [consultVet, setConsultVet] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg, isError = false) => {
    setToastMessage({ text: msg, isError });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const loadData = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const statsRes = await veterinaryService.getStats();
      if (statsRes) {
        setStats(statsRes);
      }

      const params = {};
      if (statusFilter !== 'all') params.status = statusFilter;
      if (riskFilter !== 'all') params.risk = riskFilter;
      const casesRes = await veterinaryService.getCases(params);
      if (casesRes && casesRes.data) {
        setCases(casesRes.data);
      }
    } catch (err) {
      console.error('Error fetching veterinary data:', err);
      showToast('Could not sync with live backend; displaying cached demo records.', true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadReminders = async () => {
    setRemindersLoading(true);
    try {
      const res = await reminderService.getReminders();
      if (res && res.items) {
        setReminders(res.items);
      } else if (Array.isArray(res)) {
        setReminders(res);
      }
    } catch (err) {
      console.warn('Failed to load reminders:', err);
    } finally {
      setRemindersLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'reminders') {
      loadReminders();
    }
  }, [activeTab]);

  const handleCreateReminder = async () => {
    if (!newReminderForm.title || !newReminderForm.animal_id) {
      showToast('Please enter both title and animal tag ID.', true);
      return;
    }
    setActionLoading(true);
    try {
      await reminderService.createReminder(newReminderForm);
      showToast('Vaccination/health reminder created successfully!');
      setShowAddReminderModal(false);
      setNewReminderForm({
        title: '',
        animal_id: '',
        species: 'Cattle (Bovine)',
        due_date: new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0],
        reminder_type: 'VACCINATION',
        priority: 'HIGH',
        notes: '',
      });
      loadReminders();
    } catch (err) {
      console.error('Error creating reminder:', err);
      showToast('Failed to create reminder: ' + err.message, true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteReminder = async (id) => {
    try {
      await reminderService.updateReminder(id, { status: 'COMPLETED' });
      showToast('Reminder marked as completed.');
      loadReminders();
    } catch (err) {
      console.error('Error updating reminder:', err);
      showToast('Could not update reminder: ' + err.message, true);
    }
  };

  const handleDeleteReminder = async (id) => {
    try {
      await reminderService.deleteReminder(id);
      showToast('Reminder deleted.');
      loadReminders();
    } catch (err) {
      console.error('Error deleting reminder:', err);
      showToast('Could not delete reminder: ' + err.message, true);
    }
  };

  const handleDetectLocation = () => {
    if (!navigator.geolocation) {
      showToast('Geolocation is not supported by your browser.', true);
      return;
    }
    setLocatingUser(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocatingUser(false);
        const lat = pos.coords.latitude.toFixed(4);
        const lon = pos.coords.longitude.toFixed(4);
        setUserLocationText(`Lat: ${lat}, Lon: ${lon} (Device GPS Acquired)`);
        showToast(`Device GPS locked (${lat}, ${lon}). Nearby hospitals updated.`);
      },
      (err) => {
        setLocatingUser(false);
        showToast('Location permission denied or unavailable. Using manual district selection.', true);
      },
      { timeout: 8000 }
    );
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, riskFilter]);

  const handleOpenCaseModal = async (c) => {
    setSelectedCase(c);
    setWorkflowTab('overview');

    const condition = c.ai_assessment?.condition || c.aiCondition || 'Bovine Cutaneous Lesions';
    setReviewForm({
      decision: c.vet_review?.decision || 'AI_ASSESSMENT_ACCEPTED',
      attending_vet_name: c.vet_review?.reviewed_by || c.attendingVet || CURRENT_USER.name || 'Dr. Arvind Verma',
      vet_license_number: c.vet_review?.vet_license || 'VET-REG-2024-88402',
      clinical_notes: c.vet_review?.clinical_notes || c.vetNotes || '',
      confirmed_condition: c.vet_review?.differential_diagnosis || condition,
    });

    if (c.treatment_plan?.medicines && c.treatment_plan.medicines.length > 0) {
      setMedicinesList(c.treatment_plan.medicines);
    } else if (c.treatments && c.treatments.length > 0) {
      setMedicinesList(
        c.treatments.map((t) => ({
          medicine_name: t.medicine || t.medicine_name || 'Prescribed Drug',
          formulation: 'Injectable Solution',
          dosage: t.dosage || 'Standard dose',
          frequency: 'Daily',
          duration: t.duration || '3 days',
          route: 'Intramuscular (IM)',
          instructions: t.instructions || '',
        }))
      );
    }

    setTreatmentForm({
      prescribing_vet_name: c.treatment_plan?.prescribed_by || CURRENT_USER.name || 'Dr. Arvind Verma',
      prescribing_vet_license: c.treatment_plan?.prescription_license || 'VET-REG-2024-88402',
      supportive_care: c.treatment_plan?.supportive_care || 'Antiseptic wound care and vector barrier isolation.',
      isolation_required: c.treatment_plan?.isolation_required ?? true,
      isolation_instructions: c.treatment_plan?.isolation_instructions || 'Quarantine in isolated pen.',
      farmer_instructions: c.treatment_plan?.farmer_instructions || 'Follow veterinarian instructions carefully.',
    });

    if (c.prevention_plan) {
      setPreventionForm({
        isolation_required: c.prevention_plan.isolation_required ?? true,
        isolation_duration_days: c.prevention_plan.isolation_duration_days || 14,
        isolation_instructions: c.prevention_plan.isolation_instructions || '',
        hygiene_guidance: c.prevention_plan.hygiene_guidance || '',
        vector_control: c.prevention_plan.vector_control || '',
        animal_separation: c.prevention_plan.animal_separation || '',
        monitoring_protocol: c.prevention_plan.monitoring_protocol || '',
        farmer_instructions: c.prevention_plan.farmer_instructions || '',
      });
    }

    if (c.withdrawal_information) {
      setWithdrawalForm({
        withdrawal_type: c.withdrawal_information.withdrawal_type || 'milk',
        withdrawal_days: c.withdrawal_information.withdrawal_days ?? 5,
        withdrawal_start_date: c.withdrawal_information.withdrawal_start_date || new Date().toISOString().split('T')[0],
        source: c.withdrawal_information.source || 'Statutory Veterinary Prescription Formulary',
        verified: c.withdrawal_information.verified ?? true,
      });
    }

    if (c.follow_up?.scheduled_date || c.followUpDate) {
      const dateVal = c.follow_up?.scheduled_date
        ? new Date(c.follow_up.scheduled_date).toISOString().split('T')[0]
        : new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      setFollowUpForm({
        scheduled_date: dateVal,
        notes: c.follow_up?.notes || 'Post-treatment physical assessment.',
      });
    }

    // Load vaccinations for this animal
    try {
      const animId = c.animal_id || c.animalTag;
      const vacs = await animalService.getVaccinations(animId);
      setVaccinationsList(vacs || []);
    } catch {
      setVaccinationsList([]);
    }

    setCaseModalOpen(true);
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.reviewCase(caseId, {
        decision: reviewForm.decision,
        attending_vet_name: reviewForm.attending_vet_name,
        vet_license_number: reviewForm.vet_license_number,
        clinical_notes: reviewForm.clinical_notes || 'Physical examination completed.',
        confirmed_condition: reviewForm.confirmed_condition,
      });
      showToast(`Case ${caseId} reviewed successfully! Status updated to REVIEWED.`);
      setSelectedCase(res);
      await loadData(true);
      setWorkflowTab('treatment');
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to submit clinical review.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAddMedicine = () => {
    setMedicinesList([
      ...medicinesList,
      {
        medicine_name: '',
        formulation: 'Injectable Solution',
        dosage: '',
        frequency: 'Daily',
        duration: '3 days',
        route: 'Intramuscular (IM)',
        instructions: '',
      },
    ]);
  };

  const handleRemoveMedicine = (idx) => {
    setMedicinesList(medicinesList.filter((_, i) => i !== idx));
  };

  const handleUpdateMedicine = (idx, field, val) => {
    const updated = [...medicinesList];
    updated[idx][field] = val;
    setMedicinesList(updated);
  };

  const handleTreatmentSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.prescribeTreatment(caseId, {
        prescribing_vet_name: treatmentForm.prescribing_vet_name,
        prescribing_vet_license: treatmentForm.prescribing_vet_license,
        medicines: medicinesList.filter((m) => m.medicine_name.trim() !== ''),
        supportive_care: treatmentForm.supportive_care,
        isolation_required: treatmentForm.isolation_required,
        isolation_instructions: treatmentForm.isolation_instructions,
        farmer_instructions: treatmentForm.farmer_instructions,
        withdrawal_type: withdrawalForm.withdrawal_type,
        withdrawal_days: Number(withdrawalForm.withdrawal_days),
        withdrawal_verified: withdrawalForm.verified,
        withdrawal_source: withdrawalForm.source,
      });
      showToast(`Treatment regimen prescribed for Case ${caseId}! Status: TREATMENT_ACTIVE.`);
      setSelectedCase(res);
      await loadData(true);
      setWorkflowTab('prevention');
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to prescribe treatment.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handlePreventionSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.updatePrevention(caseId, {
        isolation_required: preventionForm.isolation_required,
        isolation_duration_days: Number(preventionForm.isolation_duration_days),
        isolation_instructions: preventionForm.isolation_instructions,
        hygiene_guidance: preventionForm.hygiene_guidance,
        vector_control: preventionForm.vector_control,
        animal_separation: preventionForm.animal_separation,
        monitoring_protocol: preventionForm.monitoring_protocol,
        farmer_instructions: preventionForm.farmer_instructions,
      });
      showToast(`Biosecurity prevention plan updated for Case ${caseId}!`);
      setSelectedCase(res);
      await loadData(true);
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to update prevention plan.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleWithdrawalSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.updateWithdrawal(caseId, {
        withdrawal_type: withdrawalForm.withdrawal_type,
        withdrawal_days: Number(withdrawalForm.withdrawal_days),
        withdrawal_start_date: withdrawalForm.withdrawal_start_date,
        source: withdrawalForm.source,
        verified: withdrawalForm.verified,
      });
      showToast(`Food-safety withdrawal restriction logged for Case ${caseId}!`);
      setSelectedCase(res);
      await loadData(true);
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to update withdrawal period.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleVaccinationSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const animId = selectedCase.animal_id || selectedCase.animalTag;
      const caseId = selectedCase.case_id || selectedCase.id;
      const newVac = await animalService.addVaccination(animId, {
        ...vaccinationForm,
        case_id: caseId,
      });
      showToast(`Vaccination ${newVac.vaccine_name} recorded successfully!`);
      setVaccinationsList([newVac, ...vaccinationsList]);
      await loadData(true);
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to record vaccination.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleScheduleFollowUp = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.scheduleFollowUp(caseId, {
        scheduled_date: new Date(followUpForm.scheduled_date).toISOString(),
        notes: followUpForm.notes,
      });
      showToast(`Follow-up scheduled for Case ${caseId}! Status: FOLLOW_UP.`);
      setSelectedCase(res);
      await loadData(true);
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to schedule follow up.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCloseCase = async (e) => {
    e.preventDefault();
    if (!selectedCase) return;
    setActionLoading(true);
    try {
      const caseId = selectedCase.case_id || selectedCase.id;
      const res = await veterinaryService.closeCase(caseId, {
        closing_notes: closeForm.closing_notes,
        follow_up_completed: closeForm.follow_up_completed,
      });
      showToast(`Case ${caseId} has been formally CLOSED!`);
      setSelectedCase(res);
      await loadData(true);
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to close case.', true);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (statusStr) => {
    const s = (statusStr || '').toUpperCase().replace(/ /g, '_');
    switch (s) {
      case 'PENDING_REVIEW':
      case 'PENDING':
        return <Badge variant="warning" pulse>Pending Review</Badge>;
      case 'REVIEWED':
        return <Badge variant="indigo">Reviewed</Badge>;
      case 'TREATMENT_ACTIVE':
      case 'UNDER_TREATMENT':
        return <Badge variant="info">Treatment Active</Badge>;
      case 'FOLLOW_UP':
        return <Badge variant="warning">Follow-Up Due</Badge>;
      case 'CLOSED':
      case 'RESOLVED':
        return <Badge variant="success">Closed</Badge>;
      default:
        return <Badge variant="neutral">{statusStr || 'Unknown'}</Badge>;
    }
  };

  const getRiskBadge = (riskStr) => {
    const r = (riskStr || '').toUpperCase();
    switch (r) {
      case 'CRITICAL':
        return <Badge variant="critical">CRITICAL RISK</Badge>;
      case 'HIGH':
        return <Badge variant="danger">HIGH RISK</Badge>;
      case 'MODERATE':
      case 'MEDIUM':
        return <Badge variant="warning">MODERATE RISK</Badge>;
      case 'LOW':
        return <Badge variant="success">LOW RISK</Badge>;
      default:
        return <Badge variant="neutral">{riskStr}</Badge>;
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-200">
      {/* Toast Alert */}
      {toastMessage && (
        <div
          className={`fixed bottom-6 right-6 z-50 text-white text-sm px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 border animate-in slide-in-from-bottom-3 ${
            toastMessage.isError
              ? 'bg-rose-950 border-rose-700 text-rose-100'
              : 'bg-slate-900 border-slate-700 text-slate-100'
          }`}
        >
          {toastMessage.isError ? (
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          )}
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* Page Header */}
      <PageHeader
        title="Veterinary Care & Decision Support Workflow"
        subtitle="End-to-end clinical triage: AI screening review, multi-medicine plans, biosecurity prevention, vaccination tracking, and withdrawal safeguards."
        badge={
          <Badge variant="success" pulse>
            Veterinary Decision Support Active
          </Badge>
        }
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              icon={RefreshCw}
              loading={refreshing}
              onClick={() => loadData(true)}
            >
              Refresh Data
            </Button>
            <Button
              variant="danger"
              size="sm"
              icon={PhoneCall}
              onClick={() => showToast('Dispatching emergency mobile polyclinic ambulance (Simulated)...')}
            >
              Emergency Polyclinic Dispatch
            </Button>
          </div>
        }
      />

      {/* Real-time Dynamic Statistics Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Pending Reviews</span>
          <p className="text-2xl font-extrabold text-amber-600 mt-1">{stats.pending_reviews}</p>
          <span className="text-[10px] text-amber-700 font-medium">Awaiting Vet Validation</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Active Treatments</span>
          <p className="text-2xl font-extrabold text-sky-600 mt-1">{stats.active_treatments}</p>
          <span className="text-[10px] text-sky-700 font-medium">Multi-Medicine Regimen</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Follow-ups Due</span>
          <p className="text-2xl font-extrabold text-indigo-600 mt-1">{stats.follow_ups_due}</p>
          <span className="text-[10px] text-indigo-700 font-medium">Scheduled Checkups</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Vaccinations Due</span>
          <p className="text-2xl font-extrabold text-emerald-600 mt-1">{stats.vaccinations_due}</p>
          <span className="text-[10px] text-emerald-700 font-medium">Boosters Required</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Withdrawal Active</span>
          <p className="text-2xl font-extrabold text-rose-600 mt-1">{stats.withdrawal_restrictions}</p>
          <span className="text-[10px] text-rose-700 font-medium">Milk / Meat Withholding</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Total Pipeline</span>
          <p className="text-2xl font-extrabold text-slate-900 mt-1">{stats.total_cases}</p>
          <span className="text-[10px] text-slate-500 font-medium">Active Mongo Database</span>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto pb-1 text-xs">
        {[
          { id: 'cases', label: 'Clinical Cases & Decision Support', icon: Stethoscope },
          { id: 'medicines', label: 'Pharmaceuticals & Regimens', icon: Pill },
          { id: 'vets', label: 'Veterinary Directory & Nearby Care', icon: UserCheck },
          { id: 'reminders', label: 'Vaccination Schedules & Reminders', icon: Calendar },
          { id: 'quarantine', label: 'Isolation & Quarantine Wards', icon: ShieldPlus },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-2.5 rounded-t-xl font-bold transition-all flex items-center gap-2 whitespace-nowrap ${
                isActive
                  ? 'border-b-2 border-emerald-600 text-emerald-900 bg-emerald-50/70 shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Active Cases & High-Risk Animals */}
      {activeTab === 'cases' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Filter Bar */}
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-bold text-slate-500 flex items-center gap-1">
                <Filter className="w-3.5 h-3.5" /> Filter by Status:
              </span>
              {[
                { id: 'all', label: 'All Cases' },
                { id: 'PENDING_REVIEW', label: 'Pending Review' },
                { id: 'REVIEWED', label: 'Reviewed' },
                { id: 'TREATMENT_ACTIVE', label: 'Treatment Active' },
                { id: 'FOLLOW_UP', label: 'Follow-Up Due' },
                { id: 'CLOSED', label: 'Closed' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setStatusFilter(f.id)}
                  className={`px-2.5 py-1 rounded-lg font-semibold transition-all ${
                    statusFilter === f.id
                      ? 'bg-slate-900 text-white shadow-2xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-500">Risk:</span>
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1 font-semibold text-slate-700 focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="all">All Risks</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MODERATE">Moderate</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          {/* Cases List */}
          {loading ? (
            <div className="p-12 text-center bg-white rounded-xl border border-slate-200 space-y-3">
              <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mx-auto" />
              <p className="text-sm font-semibold text-slate-600">Loading live veterinary case files from database...</p>
            </div>
          ) : cases.length === 0 ? (
            <div className="p-12 text-center bg-white rounded-xl border border-slate-200 space-y-2">
              <Stethoscope className="w-10 h-10 text-slate-300 mx-auto" />
              <p className="text-base font-bold text-slate-800">No veterinary cases found</p>
              <p className="text-xs text-slate-500">Try adjusting your status or risk filters to view other cases.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cases.map((c) => {
                const caseId = c.case_id || c.id;
                const animalTag = c.animal_id || c.animalTag || 'Unknown Tag';
                const condition = c.ai_assessment?.condition || c.aiCondition || 'Bovine Cutaneous Evaluation';
                const confidence = c.ai_assessment?.confidence ?? c.confidence ?? 0;
                const risk = c.risk_level || c.riskLevel || 'MODERATE';
                const status = c.case_status || c.caseStatus || 'PENDING_REVIEW';
                const vetDecision = c.vet_review?.decision || c.decision;
                const attendingVet = c.vet_review?.reviewed_by || c.attendingVet;
                const followUpDate = c.follow_up?.scheduled_date
                  ? new Date(c.follow_up.scheduled_date).toLocaleDateString()
                  : c.followUpDate;
                const withdrawal = c.withdrawal_information;

                return (
                  <div
                    key={caseId}
                    className="p-5 rounded-xl bg-white border border-slate-200 hover:border-slate-300 shadow-xs space-y-4 transition-all"
                  >
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                          {caseId}
                        </span>
                        <h3 className="font-bold text-base text-slate-900">
                          {c.animalName || `Animal ${animalTag}`} ({animalTag})
                        </h3>
                        <span className="text-xs text-slate-500">
                          &bull; {c.species || 'Cattle (Bovine)'} &bull; {c.location || 'Herd Sector A'}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        {withdrawal?.status === 'ACTIVE' && (
                          <Badge variant="danger" pulse>
                            WITHDRAWAL: {withdrawal.days_remaining}d LEFT
                          </Badge>
                        )}
                        {getRiskBadge(risk)}
                        {getStatusBadge(status)}
                      </div>
                    </div>

                    {/* AI Assessment & Vet Notes Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      {/* Left: AI Assessment */}
                      <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-400 uppercase text-[10px] tracking-wider">
                            AI Screening Assessment
                          </span>
                          <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                            Decision Support
                          </span>
                        </div>
                        <p className="font-bold text-slate-900 text-sm">{condition}</p>
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-slate-200 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-emerald-500 h-2 rounded-full"
                              style={{ width: `${Math.min(100, Math.round(confidence))}%` }}
                            />
                          </div>
                          <span className="text-emerald-700 font-mono font-bold text-[11px]">
                            {Math.round(confidence)}% confidence
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-500 italic">
                          Hypothesis only. Physical validation required.
                        </p>
                      </div>

                      {/* Right: Vet Review & Decision */}
                      <div className="p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200/80 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-emerald-950 uppercase text-[10px] tracking-wider">
                            Veterinary Decision & Assessment
                          </span>
                          {vetDecision && (
                            <Badge variant="success" size="sm">
                              {vetDecision.replace(/_/g, ' ')}
                            </Badge>
                          )}
                        </div>
                        {attendingVet ? (
                          <>
                            <p className="text-xs font-bold text-slate-800">
                              Attending: {attendingVet}
                            </p>
                            <p className="text-slate-700 line-clamp-2 text-xs">
                              {c.vet_review?.clinical_notes || c.vetNotes || 'Physical examination recorded.'}
                            </p>
                          </>
                        ) : (
                          <div className="text-slate-500 italic py-1 flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5 text-amber-500" />
                            Awaiting examination & sign-off by Veterinary Medical Officer.
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Regimen & Follow-up Row */}
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-3 border-t border-slate-100 text-xs">
                      <div className="space-y-1">
                        <span className="font-bold text-slate-500 uppercase tracking-wider text-[10px]">
                          Approved Treatment Plan:
                        </span>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {c.treatment_plan?.medicines?.length > 0 ? (
                            c.treatment_plan.medicines.map((m, i) => (
                              <span
                                key={i}
                                className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium text-[11px] border border-slate-200"
                              >
                                {m.medicine_name} ({m.dosage})
                              </span>
                            ))
                          ) : c.treatments?.length > 0 ? (
                            c.treatments.map((t, i) => (
                              <span
                                key={i}
                                className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium text-[11px] border border-slate-200"
                              >
                                {t.medicine || t.medicine_name} ({t.dosage})
                              </span>
                            ))
                          ) : (
                            <span className="text-slate-400 italic text-[11px]">No active prescription yet</span>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-4 flex-shrink-0">
                        {followUpDate && (
                          <div>
                            <span className="text-[10px] text-slate-400 block uppercase font-bold">Follow-Up:</span>
                            <span className="font-semibold text-slate-800">{followUpDate}</span>
                          </div>
                        )}
                        <Button
                          variant="primary"
                          size="sm"
                          icon={Stethoscope}
                          onClick={() => handleOpenCaseModal(c)}
                        >
                          Review & Manage Case
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Medicine / Treatment Section with Prominent Warning */}
      {activeTab === 'medicines' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Statutory Legal Notice */}
          <div className="bg-rose-50 border-2 border-rose-300 rounded-xl p-4 sm:p-5 flex items-start gap-3.5 shadow-xs">
            <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1 text-xs text-rose-950">
              <h4 className="font-bold uppercase tracking-wider text-rose-900">
                Statutory Veterinary Oversight & Antimicrobial Stewardship Notice
              </h4>
              <p className="leading-relaxed">
                All pharmaceutical preparations, antimicrobials, and therapeutic regimens listed below are clinical reference formulations for authorized veterinarians. <strong>Under veterinary statutory regulations and ICAR antimicrobial stewardship guidelines, medicines MUST NOT be administered without physical examination and explicit prescription from a certified Veterinary Medical Officer.</strong>
              </p>
            </div>
          </div>

          {/* Medicine Catalog Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {MOCK_MEDICINES.map((med) => (
              <div
                key={med.id}
                className="bg-white rounded-xl border border-slate-200 p-5 space-y-3.5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="font-mono text-xs text-slate-400 font-bold">{med.id}</span>
                      <h4 className="font-bold text-base text-slate-900 mt-0.5">{med.name}</h4>
                    </div>
                    <Badge variant={med.requiresVetApproval ? 'danger' : 'success'} size="sm">
                      {med.requiresVetApproval ? 'Prescription Required' : 'OTC Supportive'}
                    </Badge>
                  </div>
                  <p className="text-xs text-emerald-800 font-semibold">{med.category}</p>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs space-y-1">
                    <p><strong className="text-slate-800">Standard Clinical Dosage:</strong> {med.standardDosage}</p>
                    <p><strong className="text-slate-800">Clinical Indications:</strong> {med.indications}</p>
                    <p className="text-slate-500"><strong className="text-slate-700">Contraindications:</strong> {med.contraindications}</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
                  <span className="text-rose-700 font-semibold">{med.approvalNotice}</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => showToast(`Doctor prescription protocol required for ${med.name}.`)}
                  >
                    View Guidelines
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Veterinarian Directory & Nearby Care */}
      {activeTab === 'vets' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Emergency Response & Nearby Infrastructure Locator */}
          <div className="bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-950 rounded-2xl p-6 text-white border border-emerald-800/40 shadow-xl space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Badge variant="success" size="sm" pulse>24x7 Emergency Network</Badge>
                  <span className="text-xs text-emerald-300 font-medium">National Livestock Medical Registry</span>
                </div>
                <h3 className="text-xl font-extrabold text-white mt-1">
                  Nearby Veterinary Hospitals & Emergency Dispatch
                </h3>
                <p className="text-xs text-slate-300 max-w-2xl mt-1">
                  Locate verified State Animal Husbandry Department clinics, mobile ambulances, and referral polyclinics nearest to your livestock herd.
                </p>
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2.5 flex-wrap">
                <Button
                  variant="primary"
                  size="sm"
                  icon={MapPin}
                  isLoading={locatingUser}
                  onClick={handleDetectLocation}
                  className="shadow-lg shadow-emerald-700/30"
                >
                  {locatingUser ? 'Acquiring GPS Fix...' : 'Detect Device Location'}
                </Button>
                <div className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
                  <span className="text-slate-400">District:</span>
                  <select
                    value={selectedDistrict}
                    onChange={(e) => setSelectedDistrict(e.target.value)}
                    className="bg-transparent text-white font-semibold outline-none cursor-pointer"
                  >
                    <option value="Anand" className="bg-slate-900">Anand (Gujarat)</option>
                    <option value="Vadodara" className="bg-slate-900">Vadodara (Gujarat)</option>
                    <option value="Kheda" className="bg-slate-900">Kheda (Gujarat)</option>
                    <option value="Mehsana" className="bg-slate-900">Mehsana (Gujarat)</option>
                    <option value="Karnal" className="bg-slate-900">Karnal (Haryana)</option>
                    <option value="Meerut" className="bg-slate-900">Meerut (UP)</option>
                    <option value="Bareilly" className="bg-slate-900">Bareilly (UP)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Current Coordinates Banner */}
            <div className="p-3 bg-white/5 rounded-xl border border-white/10 flex items-center justify-between text-xs text-slate-300">
              <span className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-emerald-400" />
                <span>Active Location: <strong>{userLocationText}</strong></span>
              </span>
              <span className="text-[11px] text-slate-400">
                Verified DAHD Registry &bull; Real-time GPS Triage
              </span>
            </div>

            {/* Emergency Hotlines Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div className="p-4 bg-rose-950/40 border border-rose-700/50 rounded-xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-300">
                    National Emergency Helpline
                  </span>
                  <p className="text-2xl font-black text-white font-mono mt-0.5">1962</p>
                  <p className="text-[11px] text-rose-200">Pashu Sanjeevani & Mobile Veterinary Units (Toll-Free)</p>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  icon={PhoneCall}
                  onClick={() => showToast('Simulating call to 1962 National Animal Ambulance...')}
                >
                  Emergency Call
                </Button>
              </div>

              <div className="p-4 bg-emerald-950/40 border border-emerald-700/50 rounded-xl flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-300">
                    Kisan Livestock Advisory
                  </span>
                  <p className="text-2xl font-black text-white font-mono mt-0.5">1800-180-1551</p>
                  <p className="text-[11px] text-emerald-200">Department of Animal Husbandry & Dairying (DAHD)</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  icon={PhoneCall}
                  onClick={() => showToast('Simulating call to 1800-180-1551 Kisan Desk...')}
                  className="text-white border-white/20 hover:bg-white/10"
                >
                  Call Help Desk
                </Button>
              </div>
            </div>

            {/* Verified Nearby Facilities */}
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Verified Veterinary Infrastructure within 25 km:
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 text-xs text-slate-800">
                <div className="bg-white rounded-xl p-4 space-y-2 border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between">
                      <span className="font-bold text-slate-900 text-sm">District Veterinary Polyclinic</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">2.4 km</span>
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">Near Amul Dairy Campus, Anand</p>
                    <div className="mt-2 text-[11px] space-y-1 text-slate-600">
                      <p>&bull; 24x7 Emergency Triage & Surgery</p>
                      <p>&bull; Mobile Ambulatory Van on-standby</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-emerald-700 font-semibold text-[11px]">Open 24 Hours</span>
                    <Button
                      variant="outline"
                      size="sm"
                      icon={PhoneCall}
                      onClick={() => showToast('Connecting to Anand District Polyclinic: +91 2692 254101')}
                    >
                      Call Desk
                    </Button>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-4 space-y-2 border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between">
                      <span className="font-bold text-slate-900 text-sm">AAU Veterinary Teaching Hospital</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">4.1 km</span>
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">Hadgood Campus, Anand Agricultural University</p>
                    <div className="mt-2 text-[11px] space-y-1 text-slate-600">
                      <p>&bull; Advanced Radiology & Blood Pathology</p>
                      <p>&bull; Specialist Large Animal Surgery Unit</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-slate-700 font-semibold text-[11px]">08:00 - 20:00 Daily</span>
                    <Button
                      variant="outline"
                      size="sm"
                      icon={PhoneCall}
                      onClick={() => showToast('Connecting to AAU Veterinary Hospital: +91 2692 261486')}
                    >
                      Call Hospital
                    </Button>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-4 space-y-2 border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between">
                      <span className="font-bold text-slate-900 text-sm">Govt Veterinary Dispensary Mogar</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">7.8 km</span>
                    </div>
                    <p className="text-slate-500 text-[11px] mt-0.5">National Highway 8, Mogar Block</p>
                    <div className="mt-2 text-[11px] space-y-1 text-slate-600">
                      <p>&bull; Routine Vaccination & Deworming</p>
                      <p>&bull; Artificial Insemination (AI) Center</p>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-slate-700 font-semibold text-[11px]">09:00 - 17:00 (Mon-Sat)</span>
                    <Button
                      variant="outline"
                      size="sm"
                      icon={PhoneCall}
                      onClick={() => showToast('Connecting to Mogar Dispensary: +91 2692 281220')}
                    >
                      Call Clinic
                    </Button>
                  </div>
                </div>
              </div>
            </div>

            {/* Statutory Transparency Disclaimer */}
            <div className="text-[11px] text-slate-400 bg-white/5 p-3 rounded-lg border border-white/5 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-400 flex-shrink-0" />
              <span>
                <strong>Directory Notice:</strong> Facility listings reflect verified State Animal Husbandry Department registries. Live visual map rendering requires Mapbox/Google Maps API tokens. Distances are computed from acquired device coordinates.
              </span>
            </div>
          </div>

          {/* Veterinarians Section Header */}
          <div className="flex items-center justify-between pt-2">
            <div>
              <h4 className="text-base font-bold text-slate-900">Registered Attending Veterinary Specialists</h4>
              <p className="text-xs text-slate-500">Certified veterinary medical officers available for direct tele-consultation</p>
            </div>
            <Badge variant="neutral">{MOCK_VETS.length} Registered Officers</Badge>
          </div>

          {/* Existing Vet Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {MOCK_VETS.map((vet) => (
              <div
                key={vet.id}
                className="bg-white rounded-xl border border-slate-200 hover:border-slate-300 hover:shadow-md transition-all p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start gap-4">
                    <img
                      src={vet.avatar}
                      alt={vet.name}
                      className="w-16 h-16 rounded-xl object-cover border border-slate-200 flex-shrink-0"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-1">
                        <h3 className="font-bold text-base text-slate-900 truncate">{vet.name}</h3>
                        <Badge variant={vet.availableToday ? 'success' : 'neutral'} size="sm">
                          {vet.availableToday ? 'Available Today' : 'On Leave'}
                        </Badge>
                      </div>
                      <p className="text-xs font-semibold text-emerald-700 mt-0.5 truncate">{vet.designation}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5 truncate">{vet.institution}</p>
                    </div>
                  </div>

                  <div className="mt-4 p-3 bg-slate-50 rounded-lg text-xs space-y-1 border border-slate-100">
                    <p><strong className="text-slate-800">Specialization:</strong> {vet.specialization}</p>
                    <p className="text-slate-500 text-[11px]"><strong className="text-slate-700">Credentials:</strong> {vet.qualifications}</p>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1 font-bold text-slate-700">
                      <Award className="w-4 h-4 text-amber-500" />
                      Rating: {vet.rating} / 5.0
                    </span>
                    <span>{vet.casesHandled}+ cases</span>
                    <span className="text-slate-400">{vet.experience}</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    {vet.nextAvailableSlot}
                  </span>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      icon={PhoneCall}
                      onClick={() => showToast(`Simulating dial to ${vet.contactPhone}...`)}
                    >
                      Direct Call
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      icon={Video}
                      onClick={() => {
                        setConsultVet(vet);
                        setShowConsultModal(true);
                      }}
                    >
                      Tele-Consult
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 4: Vaccination Schedules & Health Reminders */}
      {activeTab === 'reminders' && (
        <div className="space-y-6 animate-in fade-in">
          {/* Top Bar with Filters and Create Button */}
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-slate-400 uppercase">Status Filter:</span>
              {['ALL', 'PENDING', 'COMPLETED', 'OVERDUE'].map((st) => (
                <button
                  key={st}
                  onClick={() => setReminderFilter(st)}
                  className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-colors ${
                    reminderFilter === st
                      ? 'bg-slate-900 text-white font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                icon={RefreshCw}
                isLoading={remindersLoading}
                onClick={loadReminders}
              >
                Refresh
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={Plus}
                onClick={() => setShowAddReminderModal(true)}
              >
                Add Schedule / Reminder
              </Button>
            </div>
          </div>

          {/* Notice Banner */}
          <div className="p-3.5 bg-blue-50/70 border border-blue-200 rounded-xl text-xs text-blue-900 flex items-start gap-2.5">
            <Calendar className="w-4 h-4 text-blue-700 flex-shrink-0 mt-0.5" />
            <div>
              <strong>Livestock Vaccination & Preventive Care Schedule:</strong> Scheduled reminders sync with local farm records and central veterinary records. Doses must be administered in adherence with national FMD-CP (Foot-and-Mouth Disease Control Programme) and Brucellosis-CP guidelines.
            </div>
          </div>

          {/* Reminders List Grid */}
          {remindersLoading ? (
            <div className="py-16 text-center text-slate-500">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto text-emerald-600 mb-2" />
              <p className="text-sm font-semibold">Loading Health Reminders from Backend Database...</p>
            </div>
          ) : (
            (() => {
              const filtered = reminders.filter((r) => {
                if (reminderFilter === 'ALL') return true;
                return (r.status || 'PENDING').toUpperCase() === reminderFilter;
              });

              if (filtered.length === 0) {
                return (
                  <div className="p-12 text-center bg-white rounded-xl border border-slate-200 space-y-3">
                    <Calendar className="w-10 h-10 text-slate-300 mx-auto" />
                    <h3 className="text-base font-bold text-slate-800">No Reminders in Selected View</h3>
                    <p className="text-xs text-slate-500 max-w-sm mx-auto">
                      All tasks for this filter have been addressed or no entries have been scheduled yet.
                    </p>
                    <Button
                      variant="primary"
                      size="sm"
                      icon={Plus}
                      onClick={() => setShowAddReminderModal(true)}
                    >
                      Create First Reminder
                    </Button>
                  </div>
                );
              }

              return (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {filtered.map((rem) => {
                    const isCompleted = (rem.status || '').toUpperCase() === 'COMPLETED';
                    const isOverdue = (rem.status || '').toUpperCase() === 'OVERDUE';

                    return (
                      <div
                        key={rem.reminder_id || rem.id}
                        className={`bg-white rounded-xl border transition-all p-5 flex flex-col justify-between shadow-2xs ${
                          isCompleted
                            ? 'border-emerald-200 bg-emerald-50/20'
                            : isOverdue
                            ? 'border-rose-300 bg-rose-50/20'
                            : 'border-slate-200 hover:border-slate-300 hover:shadow-sm'
                        }`}
                      >
                        <div className="space-y-3">
                          {/* Header with Priority & Type */}
                          <div className="flex items-start justify-between gap-2">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700">
                              {rem.reminder_type || 'CARE'}
                            </span>
                            <div className="flex items-center gap-1.5">
                              <Badge
                                variant={
                                  rem.priority === 'URGENT'
                                    ? 'critical'
                                    : rem.priority === 'HIGH'
                                    ? 'danger'
                                    : rem.priority === 'MEDIUM'
                                    ? 'warning'
                                    : 'neutral'
                                }
                                size="sm"
                              >
                                {rem.priority || 'NORMAL'}
                              </Badge>
                              <Badge
                                variant={
                                  isCompleted ? 'success' : isOverdue ? 'critical' : 'warning'
                                }
                                size="sm"
                              >
                                {rem.status || 'PENDING'}
                              </Badge>
                            </div>
                          </div>

                          {/* Title & Animal */}
                          <div>
                            <h4 className="font-bold text-sm text-slate-900 leading-snug">
                              {rem.title}
                            </h4>
                            <p className="text-xs text-slate-500 font-mono mt-0.5">
                              {rem.animal_id} &bull; {rem.species}
                            </p>
                          </div>

                          {/* Due Date */}
                          <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100 flex items-center justify-between text-xs">
                            <span className="text-slate-500 flex items-center gap-1.5">
                              <Calendar className="w-3.5 h-3.5 text-slate-400" />
                              Due Date:
                            </span>
                            <span className="font-bold text-slate-800 font-mono">
                              {rem.due_date ? rem.due_date.split('T')[0] : 'N/A'}
                            </span>
                          </div>

                          {/* Notes */}
                          {rem.notes && (
                            <p className="text-xs text-slate-600 line-clamp-2 bg-white p-2 rounded border border-slate-100">
                              {rem.notes}
                            </p>
                          )}
                        </div>

                        {/* Action buttons */}
                        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2 text-xs">
                          <button
                            onClick={() => handleDeleteReminder(rem.reminder_id || rem.id)}
                            className="text-rose-600 hover:text-rose-800 p-1 rounded hover:bg-rose-50 transition-colors flex items-center gap-1"
                            title="Delete reminder"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span className="text-[11px]">Delete</span>
                          </button>

                          {!isCompleted && (
                            <Button
                              variant="outline"
                              size="sm"
                              icon={Check}
                              onClick={() => handleCompleteReminder(rem.reminder_id || rem.id)}
                              className="text-emerald-700 border-emerald-300 hover:bg-emerald-50"
                            >
                              Mark Completed
                            </Button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })()
          )}
        </div>
      )}

      {/* Tab 4: Isolation & Quarantine Wards */}
      {activeTab === 'quarantine' && (
        <div className="space-y-6 animate-in fade-in">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase">Isolation Ward A (Shed 04)</span>
                <Badge variant="critical" size="sm" pulse>Quarantine Enforced</Badge>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">7 / 10</span>
                <span className="text-xs text-slate-500">Occupied Pens</span>
              </div>
              <p className="text-xs text-rose-600 font-medium">
                FMD Suspects &bull; Bio-Footbath Station Active
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase">Isolation Ward B (Shed 06)</span>
                <Badge variant="warning" size="sm">Vector Mesh Active</Badge>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">12 / 15</span>
                <span className="text-xs text-slate-500">Occupied Pens</span>
              </div>
              <p className="text-xs text-amber-700 font-medium">
                Lumpy Skin Disease Cases &bull; Fly Nets On
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-400 uppercase">Mobile Vet Ambulances</span>
                <Badge variant="success" size="sm">2 on Patrol</Badge>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">2 / 3</span>
                <span className="text-xs text-slate-500">Active Units</span>
              </div>
              <p className="text-xs text-emerald-700 font-medium">
                Cold-Chain Vaccine Box: 4.1°C
              </p>
            </div>
          </div>
        </div>
      )}

      {/* COMPREHENSIVE DECISION SUPPORT WORKFLOW MODAL */}
      {caseModalOpen && selectedCase && (
        <Modal
          isOpen={caseModalOpen}
          onClose={() => setCaseModalOpen(false)}
          title={`Clinical Case File: ${selectedCase.case_id || selectedCase.id}`}
          subtitle={`Patient: ${selectedCase.animal_id || selectedCase.animalTag} • Status: ${selectedCase.case_status || selectedCase.caseStatus}`}
          maxWidth="max-w-4xl"
          footer={
            <div className="flex items-center justify-between w-full text-xs">
              <div className="flex items-center gap-2">
                {getStatusBadge(selectedCase.case_status || selectedCase.caseStatus)}
                {getRiskBadge(selectedCase.risk_level || selectedCase.riskLevel)}
                {selectedCase.withdrawal_information?.status === 'ACTIVE' && (
                  <Badge variant="danger">Withdrawal Active</Badge>
                )}
              </div>
              <Button variant="outline" size="sm" onClick={() => setCaseModalOpen(false)}>
                Close Window
              </Button>
            </div>
          }
        >
          <div className="space-y-5">
            {/* Workflow Navigation Sub-tabs inside modal */}
            <div className="flex items-center gap-1 border-b border-slate-200 pb-2 text-xs overflow-x-auto">
              {[
                { id: 'overview', label: '1. AI Assessment & Vitals', icon: Activity },
                { id: 'review', label: '2. Veterinary Review', icon: Stethoscope },
                { id: 'treatment', label: '3. Multi-Medicine Plan', icon: Pill },
                { id: 'prevention', label: '4. Prevention & Biosecurity', icon: ShieldPlus },
                { id: 'withdrawal', label: '5. Withdrawal Safety', icon: Droplets },
                { id: 'vaccination', label: '6. Vaccination Tracking', icon: Syringe },
                { id: 'farmer', label: '7. Farmer Guidance', icon: Languages },
                { id: 'followup', label: '8. Follow-Up & Close', icon: Calendar },
                { id: 'history', label: 'Audit Timeline', icon: History },
              ].map((step) => {
                const Icon = step.icon;
                const isActive = workflowTab === step.id;
                return (
                  <button
                    key={step.id}
                    onClick={() => setWorkflowTab(step.id)}
                    className={`px-3 py-2 rounded-lg font-bold transition-all flex items-center gap-1.5 whitespace-nowrap ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-xs'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{step.label}</span>
                  </button>
                );
              })}
            </div>

            {/* TAB 1: AI Assessment & Triage Overview */}
            {workflowTab === 'overview' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                {/* AI Safety Disclaimer Box */}
                <div className="bg-amber-50 border border-amber-300 rounded-xl p-3.5 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div className="space-y-0.5 text-amber-950">
                    <h5 className="font-bold text-amber-900 uppercase tracking-wide text-[11px]">
                      AI Decision Support Safeguard — Not a Confirmed Diagnosis
                    </h5>
                    <p className="text-[11px] leading-relaxed">
                      Artificial Intelligence model outputs provide screening probabilities and lesion localization to aid clinical triage. Under Indian Veterinary Council regulations, pharmaceutical interventions, quarantine orders, and official diagnoses must be authorized by a licensed veterinarian.
                    </p>
                  </div>
                </div>

                {/* Patient Information & AI Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2.5">
                    <h4 className="font-bold text-slate-800 text-sm flex items-center gap-1.5">
                      <Building className="w-4 h-4 text-slate-500" /> Patient Demographics
                    </h4>
                    <div className="space-y-1.5 text-slate-600">
                      <div className="flex justify-between">
                        <span className="font-medium text-slate-500">Animal Tag / ID:</span>
                        <span className="font-mono font-bold text-slate-900">
                          {selectedCase.animal_id || selectedCase.animalTag}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-slate-500">Species:</span>
                        <span className="font-semibold text-slate-800">
                          {selectedCase.species || 'Bovine (Bos indicus / Bos taurus)'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-slate-500">Location:</span>
                        <span className="font-semibold text-slate-800">
                          {selectedCase.location || 'Cluster Anand Shed 04'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="font-medium text-slate-500">Current Status:</span>
                        <span>{getStatusBadge(selectedCase.case_status || selectedCase.caseStatus)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-emerald-50/50 border border-emerald-200/80 space-y-2.5">
                    <h4 className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                      <Activity className="w-4 h-4 text-emerald-600" /> AI Vision Screening Output
                    </h4>
                    <div className="space-y-1.5">
                      <div className="flex justify-between items-baseline">
                        <span className="font-medium text-slate-500">Suggested Condition:</span>
                        <span className="font-bold text-slate-900 text-xs">
                          {selectedCase.ai_assessment?.condition || selectedCase.aiCondition}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-slate-500">Confidence Score:</span>
                        <span className="font-mono font-bold text-emerald-700">
                          {Math.round(selectedCase.ai_assessment?.confidence ?? selectedCase.confidence ?? 0)}%
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-slate-500">Priority Level:</span>
                        <span>{getRiskBadge(selectedCase.risk_level || selectedCase.riskLevel)}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 pt-1 leading-relaxed">
                        {selectedCase.ai_assessment?.explanation ||
                          'Cutaneous nodular lesions detected consistent with circumscribed cutaneous eruption.'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <Button
                    variant="primary"
                    size="sm"
                    icon={ChevronRight}
                    onClick={() => setWorkflowTab('review')}
                  >
                    Proceed to Veterinary Review
                  </Button>
                </div>
              </div>
            )}

            {/* TAB 2: Veterinary Review */}
            {workflowTab === 'review' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                <form onSubmit={handleReviewSubmit} className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <Stethoscope className="w-4 h-4 text-emerald-600" />
                      Veterinary Medical Officer Clinical Validation
                    </h4>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Clinical Decision *</label>
                        <select
                          value={reviewForm.decision}
                          onChange={(e) => setReviewForm({ ...reviewForm, decision: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 font-semibold text-slate-800 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
                        >
                          <option value="AI_ASSESSMENT_ACCEPTED">AI Assessment Accepted (Confirmed)</option>
                          <option value="AI_ASSESSMENT_MODIFIED">AI Assessment Modified (Differential)</option>
                          <option value="FURTHER_EXAMINATION_REQUIRED">Further Examination Required (Biopsy/PCR)</option>
                          <option value="URGENT_VETERINARY_ATTENTION">Urgent Veterinary In-Patient Attention</option>
                        </select>
                      </div>

                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Confirmed Condition / Assessment *</label>
                        <input
                          type="text"
                          required
                          value={reviewForm.confirmed_condition}
                          onChange={(e) => setReviewForm({ ...reviewForm, confirmed_condition: e.target.value })}
                          placeholder="e.g. Lumpy Skin Disease (Circumscribed Stage)"
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 font-medium"
                        />
                      </div>

                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Attending Vet Name *</label>
                        <input
                          type="text"
                          required
                          value={reviewForm.attending_vet_name}
                          onChange={(e) => setReviewForm({ ...reviewForm, attending_vet_name: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 font-medium"
                        />
                      </div>

                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Veterinary Council License # *</label>
                        <input
                          type="text"
                          required
                          value={reviewForm.vet_license_number}
                          onChange={(e) => setReviewForm({ ...reviewForm, vet_license_number: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 font-mono"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Clinical Notes & Physical Findings *</label>
                      <textarea
                        rows={3}
                        required
                        value={reviewForm.clinical_notes}
                        onChange={(e) => setReviewForm({ ...reviewForm, clinical_notes: e.target.value })}
                        placeholder="Document lesions, body temperature, lymph nodes, mucosal membranes..."
                        className="w-full bg-white border border-slate-300 rounded-lg p-2.5 text-slate-800"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-slate-500 italic text-[11px]">
                      Transitions case from PENDING_REVIEW to REVIEWED.
                    </span>
                    <Button variant="primary" size="sm" icon={CheckCircle2} loading={actionLoading}>
                      Save Clinical Review
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 3: Multi-Medicine Treatment Plan */}
            {workflowTab === 'treatment' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                <form onSubmit={handleTreatmentSubmit} className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                          <Pill className="w-4 h-4 text-sky-600" />
                          Prescribe Pharmaceutical & Supportive Regimen
                        </h4>
                        <p className="text-slate-500 text-xs mt-0.5">
                          Specify medicines, formulations, routes, and instructions under statutory license.
                        </p>
                      </div>
                      <Button type="button" variant="outline" size="sm" icon={Plus} onClick={handleAddMedicine}>
                        Add Medicine
                      </Button>
                    </div>

                    {/* Multi-Medicine List */}
                    <div className="space-y-3 pt-2">
                      {medicinesList.map((m, idx) => (
                        <div
                          key={idx}
                          className="p-3.5 bg-white rounded-lg border border-slate-200 space-y-2 shadow-2xs"
                        >
                          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Medicine Name *</label>
                              <input
                                type="text"
                                required
                                value={m.medicine_name}
                                onChange={(e) => handleUpdateMedicine(idx, 'medicine_name', e.target.value)}
                                placeholder="e.g. Meloxicam 5mg/ml"
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              />
                            </div>
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Formulation</label>
                              <select
                                value={m.formulation || 'Injectable Solution'}
                                onChange={(e) => handleUpdateMedicine(idx, 'formulation', e.target.value)}
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              >
                                <option value="Injectable Solution">Injectable Solution</option>
                                <option value="Bolus">Bolus / Tablet</option>
                                <option value="Oral Suspension">Oral Suspension</option>
                                <option value="Topical Ointment">Topical Ointment / Spray</option>
                                <option value="Intramammary Infusion">Intramammary Infusion</option>
                              </select>
                            </div>
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Dosage *</label>
                              <input
                                type="text"
                                required
                                value={m.dosage}
                                onChange={(e) => handleUpdateMedicine(idx, 'dosage', e.target.value)}
                                placeholder="e.g. 0.5 mg/kg"
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              />
                            </div>
                          </div>

                          <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 items-end">
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Route</label>
                              <input
                                type="text"
                                value={m.route}
                                onChange={(e) => handleUpdateMedicine(idx, 'route', e.target.value)}
                                placeholder="e.g. Subcutaneous (SC)"
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              />
                            </div>
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Frequency</label>
                              <input
                                type="text"
                                value={m.frequency}
                                onChange={(e) => handleUpdateMedicine(idx, 'frequency', e.target.value)}
                                placeholder="e.g. Once Daily"
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              />
                            </div>
                            <div>
                              <label className="font-semibold text-slate-600 text-[10px] block">Duration</label>
                              <input
                                type="text"
                                value={m.duration}
                                onChange={(e) => handleUpdateMedicine(idx, 'duration', e.target.value)}
                                placeholder="e.g. 3 days"
                                className="w-full bg-slate-50 border border-slate-300 rounded px-2 py-1 text-xs"
                              />
                            </div>
                            <div className="flex items-center justify-end">
                              {medicinesList.length > 1 && (
                                <button
                                  type="button"
                                  onClick={() => handleRemoveMedicine(idx)}
                                  className="p-1 text-rose-500 hover:bg-rose-50 rounded flex items-center gap-1 text-[11px]"
                                >
                                  <Trash2 className="w-3.5 h-3.5" /> Remove
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Prescribing Vet Name *</label>
                        <input
                          type="text"
                          required
                          value={treatmentForm.prescribing_vet_name}
                          onChange={(e) => setTreatmentForm({ ...treatmentForm, prescribing_vet_name: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 text-xs"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Veterinary Council License # *</label>
                        <input
                          type="text"
                          required
                          value={treatmentForm.prescribing_vet_license}
                          onChange={(e) => setTreatmentForm({ ...treatmentForm, prescribing_vet_license: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 text-xs font-mono"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Supportive Care & Husbandry Instructions</label>
                      <textarea
                        rows={2}
                        value={treatmentForm.supportive_care}
                        onChange={(e) => setTreatmentForm({ ...treatmentForm, supportive_care: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 text-xs"
                      />
                    </div>

                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Farmer-Facing Treatment Instructions</label>
                      <textarea
                        rows={2}
                        value={treatmentForm.farmer_instructions}
                        onChange={(e) => setTreatmentForm({ ...treatmentForm, farmer_instructions: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 text-xs"
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-slate-500 italic text-[11px]">
                      Requires certified license. Transitions status to TREATMENT_ACTIVE.
                    </span>
                    <Button variant="primary" size="sm" icon={Syringe} loading={actionLoading}>
                      Prescribe & Activate Treatment
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 4: Prevention Plan */}
            {workflowTab === 'prevention' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                <form onSubmit={handlePreventionSubmit} className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <ShieldPlus className="w-4 h-4 text-emerald-600" />
                      Biosecurity & Herd Prevention Protocols
                    </h4>
                    <p className="text-slate-500 text-xs">
                      Enforce isolation, hygiene controls, vector management, and surveillance protocols to contain spread.
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                      <div className="flex items-center gap-2 p-3 bg-white rounded-lg border border-slate-200">
                        <input
                          type="checkbox"
                          id="prev_iso"
                          checked={preventionForm.isolation_required}
                          onChange={(e) => setPreventionForm({ ...preventionForm, isolation_required: e.target.checked })}
                          className="rounded text-emerald-600 focus:ring-emerald-500"
                        />
                        <label htmlFor="prev_iso" className="font-bold text-slate-800 cursor-pointer">
                          Enforce Ward Isolation
                        </label>
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Isolation Duration (Days)</label>
                        <input
                          type="number"
                          min="0"
                          value={preventionForm.isolation_duration_days}
                          onChange={(e) => setPreventionForm({ ...preventionForm, isolation_duration_days: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Isolation Instructions</label>
                      <input
                        type="text"
                        value={preventionForm.isolation_instructions}
                        onChange={(e) => setPreventionForm({ ...preventionForm, isolation_instructions: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                      />
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Hygiene & Disinfection</label>
                        <textarea
                          rows={2}
                          value={preventionForm.hygiene_guidance}
                          onChange={(e) => setPreventionForm({ ...preventionForm, hygiene_guidance: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Vector Control (Flies / Ticks)</label>
                        <textarea
                          rows={2}
                          value={preventionForm.vector_control}
                          onChange={(e) => setPreventionForm({ ...preventionForm, vector_control: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Animal Separation Protocol</label>
                        <textarea
                          rows={2}
                          value={preventionForm.animal_separation}
                          onChange={(e) => setPreventionForm({ ...preventionForm, animal_separation: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Daily Monitoring Protocol</label>
                        <textarea
                          rows={2}
                          value={preventionForm.monitoring_protocol}
                          onChange={(e) => setPreventionForm({ ...preventionForm, monitoring_protocol: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <Button variant="primary" size="sm" icon={ShieldCheck} loading={actionLoading}>
                      Save Prevention Plan
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 5: Withdrawal Safety */}
            {workflowTab === 'withdrawal' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                <form onSubmit={handleWithdrawalSubmit} className="space-y-4">
                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <Droplets className="w-4 h-4 text-rose-600" />
                      Food Safety & Drug Withdrawal Period Regulation
                    </h4>
                    <p className="text-slate-500 text-xs">
                      Enforce withholding of milk and meat products to prevent antimicrobial residues in human food chains.
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Withdrawal Commodity *</label>
                        <select
                          value={withdrawalForm.withdrawal_type}
                          onChange={(e) => setWithdrawalForm({ ...withdrawalForm, withdrawal_type: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 font-semibold text-slate-800"
                        >
                          <option value="milk">Milk Withholding</option>
                          <option value="meat">Meat Withholding</option>
                          <option value="both">Both Milk & Meat</option>
                          <option value="none">No Restriction</option>
                        </select>
                      </div>

                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Withdrawal Days *</label>
                        <input
                          type="number"
                          min="0"
                          required
                          value={withdrawalForm.withdrawal_days}
                          onChange={(e) => setWithdrawalForm({ ...withdrawalForm, withdrawal_days: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800 font-bold"
                        />
                      </div>

                      <div>
                        <label className="font-bold text-slate-700 block mb-1">Start Date</label>
                        <input
                          type="date"
                          value={withdrawalForm.withdrawal_start_date}
                          onChange={(e) => setWithdrawalForm({ ...withdrawalForm, withdrawal_start_date: e.target.value })}
                          className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Regulatory Data Source</label>
                      <input
                        type="text"
                        value={withdrawalForm.source}
                        onChange={(e) => setWithdrawalForm({ ...withdrawalForm, source: e.target.value })}
                        placeholder="e.g. Manufacturer Label / Statutory Veterinary Formulary"
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                      />
                    </div>

                    <div className="flex items-center gap-2 p-3 bg-white rounded-lg border border-slate-200">
                      <input
                        type="checkbox"
                        id="with_ver"
                        checked={withdrawalForm.verified}
                        onChange={(e) => setWithdrawalForm({ ...withdrawalForm, verified: e.target.checked })}
                        className="rounded text-emerald-600 focus:ring-emerald-500"
                      />
                      <label htmlFor="with_ver" className="font-bold text-slate-800 cursor-pointer">
                        Formally Verified from Manufacturer or Statutory Formulary
                      </label>
                    </div>

                    {/* Active withdrawal badge indicator */}
                    {selectedCase.withdrawal_information && (
                      <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center justify-between">
                        <div>
                          <span className="font-bold text-rose-900 block">
                            Current Status: {selectedCase.withdrawal_information.status}
                          </span>
                          <span className="text-[11px] text-rose-700">
                            {selectedCase.withdrawal_information.safety_notice}
                          </span>
                        </div>
                        {selectedCase.withdrawal_information.days_remaining > 0 && (
                          <Badge variant="danger" size="lg">
                            {selectedCase.withdrawal_information.days_remaining} Days Left
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex justify-end pt-1">
                    <Button variant="primary" size="sm" icon={Droplets} loading={actionLoading}>
                      Update Withdrawal Restriction
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 6: Vaccination Tracking */}
            {workflowTab === 'vaccination' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                {/* Vaccination History List */}
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                  <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                    <Syringe className="w-4 h-4 text-indigo-600" />
                    Vaccination Records & Booster Schedule
                  </h4>

                  {vaccinationsList.length > 0 ? (
                    <div className="space-y-2">
                      {vaccinationsList.map((v, i) => (
                        <div key={i} className="p-3 bg-white rounded-lg border border-slate-200 flex items-center justify-between">
                          <div>
                            <span className="font-bold text-slate-900 block">{v.vaccine_name}</span>
                            <span className="text-slate-500 text-[11px]">
                              Target: {v.disease_target} &bull; Administered: {v.date_administered} &bull; Next Due: {v.next_due_date}
                            </span>
                            {v.batch_number && <span className="block text-slate-400 font-mono text-[10px]">Batch: {v.batch_number}</span>}
                          </div>
                          <Badge variant={v.status === 'Completed' ? 'success' : 'warning'}>
                            {v.status || 'Active'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400 italic">No previous vaccination records logged for this animal.</p>
                  )}
                </div>

                {/* Add Vaccination Form */}
                <form onSubmit={handleVaccinationSubmit} className="bg-indigo-50/50 p-4 rounded-xl border border-indigo-200 space-y-3">
                  <h5 className="font-bold text-indigo-950 text-xs uppercase tracking-wide">
                    Log Official Vaccine Administration
                  </h5>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Vaccine Formulation *</label>
                      <input
                        type="text"
                        required
                        value={vaccinationForm.vaccine_name}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, vaccine_name: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Disease Target *</label>
                      <input
                        type="text"
                        required
                        value={vaccinationForm.disease_target}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, disease_target: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Administered Date *</label>
                      <input
                        type="date"
                        required
                        value={vaccinationForm.date_administered}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, date_administered: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Next Due Date *</label>
                      <input
                        type="date"
                        required
                        value={vaccinationForm.next_due_date}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, next_due_date: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Batch Number</label>
                      <input
                        type="text"
                        value={vaccinationForm.batch_number}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, batch_number: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800 font-mono"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Administered By</label>
                      <input
                        type="text"
                        value={vaccinationForm.administered_by}
                        onChange={(e) => setVaccinationForm({ ...vaccinationForm, administered_by: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded p-2 text-slate-800"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end pt-1">
                    <Button variant="primary" size="sm" icon={Syringe} loading={actionLoading}>
                      Record Vaccination
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 7: Bilingual Farmer Guidance */}
            {workflowTab === 'farmer' && (
              <div className="space-y-4 text-xs animate-in fade-in">
                {/* Language Switcher */}
                <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                  <span className="font-bold text-slate-700 flex items-center gap-1.5">
                    <Languages className="w-4 h-4 text-emerald-600" />
                    Farmer Advisory Language:
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setFarmerLang('en')}
                      className={`px-3 py-1 rounded-lg font-bold transition-all ${
                        farmerLang === 'en' ? 'bg-slate-900 text-white shadow-2xs' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      English
                    </button>
                    <button
                      onClick={() => setFarmerLang('hi')}
                      className={`px-3 py-1 rounded-lg font-bold transition-all ${
                        farmerLang === 'hi' ? 'bg-slate-900 text-white shadow-2xs' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      हिंदी (Hindi)
                    </button>
                  </div>
                </div>

                {/* English Guidance */}
                {farmerLang === 'en' && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2">
                      <h4 className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" /> What to Do (Recommendations)
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-slate-700 text-xs">
                        <li>Keep the animal under regular observation in a well-ventilated, dry pen.</li>
                        <li>Follow the attending veterinarian's approved medication schedule strictly.</li>
                        <li>Maintain separate feeding and drinking buckets to prevent cross-contamination.</li>
                        <li>Keep suspected animals isolated behind insect-repellent fly mesh.</li>
                        <li>Immediately report any spike in body temperature or fresh cutaneous lesions.</li>
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 space-y-2">
                      <h4 className="font-bold text-rose-950 text-sm flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-rose-600" /> What NOT to Do (Safety Prohibitions)
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-slate-700 text-xs">
                        <li>Do NOT alter medication dosages or discontinue treatment early.</li>
                        <li>Do NOT administer unverified antibiotics without veterinary prescription.</li>
                        <li>Do NOT move high-risk animals across herd boundaries or common grazing pastures.</li>
                        <li>Do NOT harvest or sell milk or meat during active statutory withdrawal periods.</li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Hindi Guidance */}
                {farmerLang === 'hi' && (
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 space-y-2">
                      <h4 className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" /> क्या करें (पशुपालक के लिए आवश्यक निर्देश)
                      </h4>
                      <ul className="list-disc list-inside space-y-1.5 text-slate-800 text-xs">
                        <li>पशु को हवादार, साफ और सूखे बाड़े में निरंतर निगरानी में रखें।</li>
                        <li>पशु चिकित्सक द्वारा निर्धारित दवाओं और खुराक का समय पर पूर्ण पालन करें।</li>
                        <li>संक्रमण रोकने के लिए पानी और चारे के बर्तन अन्य पशुओं से बिल्कुल अलग रखें।</li>
                        <li>मक्खियों और कीड़ों से बचाव के लिए मच्छरदानी या जाली का उपयोग करें।</li>
                        <li>पशु को तेज बुखार या नई गांठें दिखने पर तुरंत पशु चिकित्सक को सूचित करें।</li>
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 space-y-2">
                      <h4 className="font-bold text-rose-950 text-sm flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-rose-600" /> क्या न करें (सुरक्षा सावधानियां)
                      </h4>
                      <ul className="list-disc list-inside space-y-1.5 text-slate-800 text-xs">
                        <li>दवा की खुराक अपने आप कभी न बदलें और इलाज बीच में बंद न करें।</li>
                        <li>बिना पशु चिकित्सक के पर्चे के कोई भी एंटीबायोटिक या दवा न दें।</li>
                        <li>संक्रमित पशु को साझा चरागाह या स्वस्थ पशुओं के बीच न ले जाएं।</li>
                        <li>दवा के विथड्रॉल (निकासी) समय के दौरान दूध या मांस का उपयोग या बिक्री न करें।</li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Vet Approved Specific Instructions */}
                {selectedCase.treatment_plan?.farmer_instructions && (
                  <div className="p-3.5 bg-slate-100 rounded-xl border border-slate-300 space-y-1">
                    <span className="font-bold text-slate-700 uppercase text-[10px] block">
                      Specific Attending Veterinarian Instructions:
                    </span>
                    <p className="text-slate-800 font-medium">
                      {selectedCase.treatment_plan.farmer_instructions}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* TAB 8: Follow-up & Case Closure */}
            {workflowTab === 'followup' && (
              <div className="space-y-5 text-xs animate-in fade-in">
                <form onSubmit={handleScheduleFollowUp} className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                  <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-indigo-600" />
                    Schedule Clinical Follow-Up Examination
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Follow-Up Date *</label>
                      <input
                        type="date"
                        required
                        value={followUpForm.scheduled_date}
                        onChange={(e) => setFollowUpForm({ ...followUpForm, scheduled_date: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                      />
                    </div>
                    <div>
                      <label className="font-bold text-slate-700 block mb-1">Follow-Up Objectives</label>
                      <input
                        type="text"
                        value={followUpForm.notes}
                        onChange={(e) => setFollowUpForm({ ...followUpForm, notes: e.target.value })}
                        className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <Button variant="primary" size="sm" icon={Calendar} loading={actionLoading}>
                      Set Follow-Up (Status: FOLLOW_UP)
                    </Button>
                  </div>
                </form>

                <form onSubmit={handleCloseCase} className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-200/80 space-y-3">
                  <h4 className="font-bold text-emerald-950 text-sm flex items-center gap-1.5">
                    <FileCheck2 className="w-4 h-4 text-emerald-700" />
                    Formal Case Resolution & Discharge
                  </h4>
                  <div>
                    <label className="font-bold text-slate-700 block mb-1">Discharge & Resolution Summary</label>
                    <textarea
                      rows={2}
                      required
                      value={closeForm.closing_notes}
                      onChange={(e) => setCloseForm({ ...closeForm, closing_notes: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg p-2 text-slate-800"
                    />
                  </div>
                  <div className="flex justify-end pt-1">
                    <Button variant="success" size="sm" icon={Check} loading={actionLoading}>
                      Formally Close Case (Status: CLOSED)
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* TAB 9: Audit Timeline History */}
            {workflowTab === 'history' && (
              <div className="space-y-3 text-xs animate-in fade-in">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                  <History className="w-4 h-4 text-slate-600" />
                  Chronological Regulatory Audit Timeline
                </h4>
                {selectedCase.audit_trail?.length > 0 ? (
                  <div className="space-y-2 border-l-2 border-slate-200 pl-4 ml-2">
                    {selectedCase.audit_trail.map((item, idx) => (
                      <div key={idx} className="relative pb-3">
                        <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-emerald-600 ring-4 ring-white" />
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900">{item.action}</span>
                          <span className="text-slate-400 font-mono text-[10px]">
                            {new Date(item.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-slate-600 font-medium text-[11px] mt-0.5">
                          Operator: {item.performed_by || item.user_id || 'System'}
                        </p>
                        {item.details && <p className="text-slate-500 mt-0.5">{item.details}</p>}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400 italic">No audit timeline entries recorded yet.</p>
                )}
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Tele-Consultation Modal */}
      {/* Add Reminder Modal */}
      {showAddReminderModal && (
        <Modal
          isOpen={showAddReminderModal}
          onClose={() => setShowAddReminderModal(false)}
          title="Schedule Health Reminder / Vaccination"
          subtitle="Record upcoming preventive veterinary or husbandry tasks"
          maxWidth="max-w-lg"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowAddReminderModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={Calendar}
                isLoading={actionLoading}
                onClick={handleCreateReminder}
              >
                Save Schedule
              </Button>
            </>
          }
        >
          <div className="space-y-3.5 text-xs">
            <div>
              <label className="font-bold text-slate-700 block mb-1">Reminder Title *</label>
              <input
                type="text"
                required
                placeholder="e.g. FMD Bi-Annual Booster Dose"
                value={newReminderForm.title}
                onChange={(e) => setNewReminderForm({ ...newReminderForm, title: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-800"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Animal Tag ID *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. TAG-8821"
                  value={newReminderForm.animal_id}
                  onChange={(e) => setNewReminderForm({ ...newReminderForm, animal_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono text-slate-800"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Species</label>
                <select
                  value={newReminderForm.species}
                  onChange={(e) => setNewReminderForm({ ...newReminderForm, species: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white text-slate-800"
                >
                  <option value="Cattle (Bovine)">Cattle (Bovine)</option>
                  <option value="Buffalo (Bubaline)">Buffalo (Bubaline)</option>
                  <option value="Goat (Caprine)">Goat (Caprine)</option>
                  <option value="Sheep (Ovine)">Sheep (Ovine)</option>
                  <option value="Poultry (Avian)">Poultry (Avian)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Due Date *</label>
                <input
                  type="date"
                  required
                  value={newReminderForm.due_date}
                  onChange={(e) => setNewReminderForm({ ...newReminderForm, due_date: e.target.value })}
                  className="w-full px-2.5 py-2 border border-slate-300 rounded-lg text-slate-800"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Category</label>
                <select
                  value={newReminderForm.reminder_type}
                  onChange={(e) => setNewReminderForm({ ...newReminderForm, reminder_type: e.target.value })}
                  className="w-full px-2.5 py-2 border border-slate-300 rounded-lg bg-white text-slate-800"
                >
                  <option value="VACCINATION">Vaccination</option>
                  <option value="MEDICATION">Medication</option>
                  <option value="CHECKUP">Checkup</option>
                  <option value="DEWORMING">Deworming</option>
                  <option value="HYGIENE">Hygiene</option>
                </select>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Priority</label>
                <select
                  value={newReminderForm.priority}
                  onChange={(e) => setNewReminderForm({ ...newReminderForm, priority: e.target.value })}
                  className="w-full px-2.5 py-2 border border-slate-300 rounded-lg bg-white text-slate-800"
                >
                  <option value="URGENT">Urgent</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>
            </div>

            <div>
              <label className="font-bold text-slate-700 block mb-1">Instructions / Clinical Notes</label>
              <textarea
                rows={2}
                placeholder="Dosage specifics, temperature check requirements, or quarantine instructions..."
                value={newReminderForm.notes}
                onChange={(e) => setNewReminderForm({ ...newReminderForm, notes: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-slate-800"
              />
            </div>
          </div>
        </Modal>
      )}

      {showConsultModal && consultVet && (
        <Modal
          isOpen={showConsultModal}
          onClose={() => setShowConsultModal(false)}
          title={`Tele-Veterinary Consultation: ${consultVet.name}`}
          subtitle={`${consultVet.designation} • ${consultVet.institution}`}
          maxWidth="max-w-lg"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowConsultModal(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={Video}
                onClick={() => {
                  showToast(`Simulated: Secure encrypted video consultation launched with ${consultVet.name}.`);
                  setShowConsultModal(false);
                }}
              >
                Launch Encrypted Room
              </Button>
            </>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
              <p className="font-semibold text-slate-800">Assigned Patient Case:</p>
              <p className="text-slate-600 font-mono">TAG-8821 (Ganga - Suspected FMD Vesicular Stage)</p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
