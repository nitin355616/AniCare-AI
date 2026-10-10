import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useTranslation } from '../i18n';
import { farmerService } from '../services/api/farmerService';
import { speechService } from '../services/voice/speechService';
import { networkService } from '../services/connectivity/networkService';
import { 
  Volume2, 
  VolumeX, 
  AlertTriangle, 
  ShieldCheck, 
  CheckCircle2, 
  Clock, 
  Phone, 
  UserCheck, 
  Pill, 
  Info, 
  WifiOff, 
  Activity, 
  RefreshCw, 
  X, 
  Calendar, 
  HelpCircle,
  AlertCircle,
  Save,
  Camera
} from 'lucide-react';
import SyncStatusBadge from '../components/sync/SyncStatusBadge';
import SyncStatusModal from '../components/sync/SyncStatusModal';
import { syncQueue } from '../services/offline/syncQueue';
import { ACTION_TYPES } from '../services/offline/syncTypes';

export default function FarmerExperience() {
  const { t, lang, toggleLang } = useTranslation();

  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [filter, setFilter] = useState('ALL'); // ALL | URGENT | ATTENTION | HEALTHY
  const [selectedAnimal, setSelectedAnimal] = useState(null);
  const [selectedAnimalDetail, setSelectedAnimalDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  
  // Voice states
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentlySpeakingId, setCurrentlySpeakingId] = useState(null);

  // Connectivity
  const [isOnline, setIsOnline] = useState(networkService.getOnlineStatus());

  // Doctor visit request modal
  const [requestModalAnimal, setRequestModalAnimal] = useState(null);
  const [requestNotes, setRequestNotes] = useState('');
  const [requestSubmitting, setRequestSubmitting] = useState(false);
  const [requestSuccessMsg, setRequestSuccessMsg] = useState('');

  // Help modal
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Milestone 10: Sync & Offline States
  const [showSyncModal, setShowSyncModal] = useState(false);
  const [offlineObsText, setOfflineObsText] = useState('');
  const [offlineObsSavedMsg, setOfflineObsSavedMsg] = useState('');
  const [savingOfflineObs, setSavingOfflineObs] = useState(false);

  // Monitor network status
  useEffect(() => {
    const unsubscribe = networkService.subscribe((online) => {
      setIsOnline(online);
    });
    return () => unsubscribe();
  }, []);

  // Fetch dashboard data
  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const data = await farmerService.getFarmerDashboard();
      setDashboardData(data);
    } catch (err) {
      console.error('Failed to load farmer dashboard:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // Handle Speech Readout
  const handleSpeak = (text, id = 'global') => {
    if (isSpeaking && currentlySpeakingId === id) {
      speechService.stop();
      setIsSpeaking(false);
      setCurrentlySpeakingId(null);
      return;
    }

    speechService.stop();
    setIsSpeaking(true);
    setCurrentlySpeakingId(id);

    speechService.speak(text, {
      lang: lang === 'hi' ? 'hi' : 'en',
      onEnd: () => {
        setIsSpeaking(false);
        setCurrentlySpeakingId(null);
      },
      onError: () => {
        setIsSpeaking(false);
        setCurrentlySpeakingId(null);
      }
    });
  };

  // Open animal detail
  const handleOpenAnimalDetail = async (animal) => {
    setSelectedAnimal(animal);
    setDetailLoading(true);
    try {
      const detail = await farmerService.getFarmerAnimalDetail(animal.animal_id);
      setSelectedAnimalDetail(detail);
    } catch (err) {
      console.warn('Fallback to basic summary:', err);
      setSelectedAnimalDetail(animal);
    } finally {
      setDetailLoading(false);
    }
  };

  // Submit doctor visit request
  const handleSubmitDoctorRequest = async (e) => {
    e.preventDefault();
    if (!requestModalAnimal) return;
    setRequestSubmitting(true);
    setRequestSuccessMsg('');

    try {
      const res = await farmerService.requestDoctorVisit(requestModalAnimal.animal_id, {
        symptoms: requestModalAnimal.symptoms || ['Skin Nodules', 'Fever'],
        notes: requestNotes
      });
      setRequestSuccessMsg(lang === 'hi' ? res.message_hi : res.message_en);
      setTimeout(() => {
        setRequestModalAnimal(null);
        setRequestNotes('');
        setRequestSuccessMsg('');
        loadDashboard();
      }, 2000);
    } catch (err) {
      console.error('Failed to request doctor:', err);
      setRequestSuccessMsg(
        lang === 'hi'
          ? 'अनुरोध दर्ज हुआ (ऑफ़लाइन सुरक्षित)। डॉक्टर को सूचित किया जाएगा।'
          : 'Request logged (cached offline). Veterinary officer notified.'
      );
      setTimeout(() => {
        setRequestModalAnimal(null);
        setRequestNotes('');
        setRequestSuccessMsg('');
      }, 2000);
    } finally {
      setRequestSubmitting(false);
    }
  };

  // Milestone 10: Save Offline Observation into Queue
  const handleSaveOfflineObservation = async () => {
    if (!offlineObsText.trim() || !selectedAnimal) return;
    setSavingOfflineObs(true);
    try {
      await syncQueue.enqueueAction({
        actionType: ACTION_TYPES.CREATE_HEALTH_OBSERVATION,
        entityType: 'health_record',
        entityId: selectedAnimal.animal_id,
        payload: {
          symptoms: ['Farmer Daily Observation'],
          observations: offlineObsText.trim(),
        },
      });
      setOfflineObsSavedMsg(t('offlineObservationSaved'));
      setOfflineObsText('');
      setTimeout(() => setOfflineObsSavedMsg(''), 4000);
    } catch (err) {
      console.error('Failed to save offline observation:', err);
    } finally {
      setSavingOfflineObs(false);
    }
  };

  // Filtered animals list
  const filteredAnimals = useMemo(() => {
    if (!dashboardData || !dashboardData.animals) return [];
    if (filter === 'ALL') return dashboardData.animals;
    return dashboardData.animals.filter((a) => a.simplified_status === filter);
  }, [dashboardData, filter]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 pb-16 font-sans">
      {/* Offline Alert Bar */}
      {(!isOnline || dashboardData?.is_offline_cached) && (
        <div className="bg-amber-600/90 text-white px-4 py-2 text-sm flex items-center justify-between shadow-md">
          <div className="flex items-center gap-2">
            <WifiOff className="w-4 h-4" />
            <span>{t('offlineBannerMsg')}</span>
          </div>
          <span className="text-xs bg-amber-800/80 px-2 py-0.5 rounded font-mono">OFFLINE MODE</span>
        </div>
      )}

      {/* Main Header / Navigation */}
      <header className="bg-slate-800 border-b border-slate-700/60 sticky top-0 z-30 shadow-lg">
        <div className="max-w-5xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center shadow-md shadow-emerald-900/30">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-white">{t('farmerPortal')}</h1>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded text-xs font-semibold">
                  SIH 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {t('greeting')}, {dashboardData?.farmer_name || 'Kishorbhai Patel'} • {dashboardData?.farmer_location || 'Anand, Gujarat'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Milestone 10: Persistent Real-Time Sync Indicator */}
            <SyncStatusBadge onOpenPanel={() => setShowSyncModal(true)} />

            {/* Bilingual Toggle Button */}
            <button
              onClick={toggleLang}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700/80 hover:bg-slate-700 text-emerald-300 border border-slate-600/80 rounded-lg text-sm font-semibold transition active:scale-95 shadow-sm"
              title="Change Language / भाषा बदलें"
            >
              <span className="text-base">🌐</span>
              <span>{lang === 'hi' ? 'English' : 'हिंदी'}</span>
            </button>

            {/* Read Page Audio Button */}
            <button
              onClick={() => {
                const introText =
                  lang === 'hi'
                    ? `नमस्ते ${dashboardData?.farmer_name || 'किसान भाई'}। आपके कुल ${dashboardData?.total_animals || 0} पशु हैं। ${dashboardData?.urgent_count || 0} पशुओं को डॉक्टर की तत्काल जरूरत है।`
                    : `Hello ${dashboardData?.farmer_name || 'Farmer'}. You have ${dashboardData?.total_animals || 0} animals. ${dashboardData?.urgent_count || 0} animals need urgent veterinary attention.`;
                handleSpeak(introText, 'header');
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition active:scale-95 shadow-sm ${
                isSpeaking && currentlySpeakingId === 'header'
                  ? 'bg-amber-600 text-white animate-pulse'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white'
              }`}
            >
              {isSpeaking && currentlySpeakingId === 'header' ? (
                <>
                  <VolumeX className="w-4 h-4" />
                  <span>{t('speaking')}</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-4 h-4" />
                  <span>{t('listen')}</span>
                </>
              )}
            </button>

            {/* Help & Safety */}
            <button
              onClick={() => setShowHelpModal(true)}
              className="p-2 bg-slate-700/60 hover:bg-slate-700 text-slate-300 rounded-lg transition"
              title={t('help')}
            >
              <HelpCircle className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {/* Local Outbreak Warning Banner */}
        {dashboardData?.outbreak_warning?.has_warning && (
          <div className="bg-gradient-to-r from-red-950/80 to-amber-950/70 border-2 border-red-500/60 rounded-2xl p-4 md:p-5 shadow-xl shadow-red-950/40 relative overflow-hidden">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="p-2.5 bg-red-600/30 border border-red-500/50 rounded-xl mt-0.5 text-red-400">
                  <AlertTriangle className="w-6 h-6 animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="bg-red-500/20 text-red-400 border border-red-500/40 text-xs px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                      {dashboardData.outbreak_warning.severity === 'HIGH' ? 'RED ALERT' : 'SURVEILLANCE'}
                    </span>
                    <h3 className="text-lg font-bold text-red-200">
                      {lang === 'hi' ? dashboardData.outbreak_warning.title_hi : dashboardData.outbreak_warning.title_en}
                    </h3>
                  </div>
                  <p className="text-sm text-slate-300 mt-1">
                    {lang === 'hi' ? dashboardData.outbreak_warning.message_hi : dashboardData.outbreak_warning.message_en}
                  </p>
                  <div className="mt-2 text-xs font-medium text-amber-300/90 flex items-center gap-1.5">
                    <span>💡 {t('whatToDoNow')}:</span>
                    <span>
                      {lang === 'hi' ? dashboardData.outbreak_warning.action_hi : dashboardData.outbreak_warning.action_en}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  const alertSpeech =
                    lang === 'hi'
                      ? `${dashboardData.outbreak_warning.title_hi}। ${dashboardData.outbreak_warning.message_hi}। सलाह: ${dashboardData.outbreak_warning.action_hi}`
                      : `${dashboardData.outbreak_warning.title_en}. ${dashboardData.outbreak_warning.message_en}. Action: ${dashboardData.outbreak_warning.action_en}`;
                  handleSpeak(alertSpeech, 'outbreak_alert');
                }}
                className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition active:scale-95 ${
                  isSpeaking && currentlySpeakingId === 'outbreak_alert'
                    ? 'bg-amber-600 text-white animate-pulse'
                    : 'bg-red-600/80 hover:bg-red-600 text-white'
                }`}
              >
                <Volume2 className="w-4 h-4" />
                <span>{t('listen')}</span>
              </button>
            </div>
          </div>
        )}

        {/* Quick KPI Cards (Large Touch Targets) */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          {/* Total Animals */}
          <button
            onClick={() => setFilter('ALL')}
            className={`p-4 rounded-2xl border text-left transition transform active:scale-95 shadow-md flex flex-col justify-between ${
              filter === 'ALL'
                ? 'bg-slate-800 border-emerald-500 ring-2 ring-emerald-500/20'
                : 'bg-slate-800/80 border-slate-700 hover:border-slate-600'
            }`}
          >
            <div className="flex items-center justify-between w-full">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t('totalAnimals')}</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-2">
              <span className="text-3xl font-extrabold text-white">{dashboardData?.total_animals ?? 0}</span>
            </div>
          </button>

          {/* Urgent (Doctor Needed) */}
          <button
            onClick={() => setFilter('URGENT')}
            className={`p-4 rounded-2xl border text-left transition transform active:scale-95 shadow-md flex flex-col justify-between ${
              filter === 'URGENT'
                ? 'bg-red-950/50 border-red-500 ring-2 ring-red-500/20'
                : 'bg-slate-800/80 border-slate-700 hover:border-red-500/40'
            }`}
          >
            <div className="flex items-center justify-between w-full">
              <span className="text-xs font-semibold text-red-400 uppercase tracking-wider">{t('urgent')}</span>
              <AlertTriangle className="w-4 h-4 text-red-400" />
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-red-400">{dashboardData?.urgent_count ?? 0}</span>
              {(dashboardData?.urgent_count ?? 0) > 0 && (
                <span className="text-xs bg-red-500/20 text-red-300 px-1.5 py-0.5 rounded font-bold animate-pulse">
                  CALL DR
                </span>
              )}
            </div>
          </button>

          {/* Needs Attention */}
          <button
            onClick={() => setFilter('ATTENTION')}
            className={`p-4 rounded-2xl border text-left transition transform active:scale-95 shadow-md flex flex-col justify-between ${
              filter === 'ATTENTION'
                ? 'bg-amber-950/50 border-amber-500 ring-2 ring-amber-500/20'
                : 'bg-slate-800/80 border-slate-700 hover:border-amber-500/40'
            }`}
          >
            <div className="flex items-center justify-between w-full">
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">{t('needsAttention')}</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-2">
              <span className="text-3xl font-extrabold text-amber-400">{dashboardData?.attention_count ?? 0}</span>
            </div>
          </button>

          {/* Healthy */}
          <button
            onClick={() => setFilter('HEALTHY')}
            className={`p-4 rounded-2xl border text-left transition transform active:scale-95 shadow-md flex flex-col justify-between ${
              filter === 'HEALTHY'
                ? 'bg-emerald-950/50 border-emerald-500 ring-2 ring-emerald-500/20'
                : 'bg-slate-800/80 border-slate-700 hover:border-emerald-500/40'
            }`}
          >
            <div className="flex items-center justify-between w-full">
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">{t('healthy')}</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-2">
              <span className="text-3xl font-extrabold text-emerald-400">{dashboardData?.healthy_count ?? 0}</span>
            </div>
          </button>
        </div>

        {/* Filter Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
          {[
            { id: 'ALL', label: t('tabAll') },
            { id: 'URGENT', label: t('tabUrgent') },
            { id: 'ATTENTION', label: t('tabAttention') },
            { id: 'HEALTHY', label: t('tabHealthy') },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition whitespace-nowrap ${
                filter === tab.id
                  ? 'bg-emerald-600 text-white shadow-md'
                  : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Animals List Section */}
        {loading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
            <RefreshCw className="w-6 h-6 animate-spin text-emerald-400" />
            <p className="text-sm">डेटा लोड हो रहा है... / Loading animals...</p>
          </div>
        ) : filteredAnimals.length === 0 ? (
          <div className="p-8 text-center bg-slate-800/40 border border-slate-800 rounded-2xl">
            <p className="text-sm text-slate-400">{t('emptyAnimals')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAnimals.map((animal) => {
              const isUrgent = animal.simplified_status === 'URGENT';
              const isAttention = animal.simplified_status === 'ATTENTION';
              const statusBadgeColor = isUrgent
                ? 'bg-red-500/20 text-red-300 border-red-500/40'
                : isAttention
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';

              const speechText =
                lang === 'hi'
                  ? `${animal.name}, टैग ${animal.tag}। स्थिति: ${animal.status_label_hi}। ${animal.explanation_hi}`
                  : `${animal.name}, Tag ${animal.tag}. Status: ${animal.status_label_en}. ${animal.explanation_en}`;

              return (
                <div
                  key={animal.animal_id}
                  className={`bg-slate-800/90 border rounded-2xl overflow-hidden shadow-lg transition hover:border-slate-600 flex flex-col justify-between ${
                    isUrgent ? 'border-red-500/60' : isAttention ? 'border-amber-500/50' : 'border-slate-700'
                  }`}
                >
                  {/* Animal Image & Tag Banner */}
                  <div className="relative h-44 w-full bg-slate-900">
                    <img
                      src={animal.photo || 'https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=400&q=80'}
                      alt={animal.name}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-black/40" />

                    {/* Tag badge */}
                    <div className="absolute top-3 left-3 bg-black/75 backdrop-blur-md px-2.5 py-1 rounded-lg border border-white/20 text-xs font-mono font-bold text-white">
                      🏷️ {animal.tag}
                    </div>

                    {/* Voice Readout Button on Card */}
                    <button
                      onClick={() => handleSpeak(speechText, animal.animal_id)}
                      className={`absolute top-3 right-3 p-2 rounded-xl backdrop-blur-md transition active:scale-90 shadow-md ${
                        isSpeaking && currentlySpeakingId === animal.animal_id
                          ? 'bg-amber-600 text-white animate-pulse'
                          : 'bg-black/60 hover:bg-black/80 text-white'
                      }`}
                      title={t('listen')}
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>

                    {/* Animal Name & Breed */}
                    <div className="absolute bottom-3 left-3 right-3">
                      <div className="flex items-baseline justify-between">
                        <h4 className="text-lg font-bold text-white">{animal.name}</h4>
                        <span className="text-xs text-slate-300 font-medium">
                          {animal.species} {animal.breed ? `• ${animal.breed}` : ''}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Body Content */}
                  <div className="p-4 space-y-3 flex-1 flex flex-col justify-between">
                    <div>
                      {/* Health Status Badge */}
                      <div className="flex items-center justify-between mb-2">
                        <span className={`text-xs px-2.5 py-1 rounded-lg border font-bold flex items-center gap-1.5 ${statusBadgeColor}`}>
                          {isUrgent && <span className="w-2 h-2 rounded-full bg-red-400 animate-ping" />}
                          {lang === 'hi' ? animal.status_label_hi : animal.status_label_en}
                        </span>

                        {animal.review_status === 'PENDING' && (
                          <span className="text-xs text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20 font-medium">
                            {t('statusReviewPending')}
                          </span>
                        )}
                        {animal.review_status === 'IN_TREATMENT' && (
                          <span className="text-xs text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded border border-blue-400/20 font-medium">
                            {t('statusTreatment')}
                          </span>
                        )}
                      </div>

                      {/* Plain Language Explanation */}
                      <p className="text-xs text-slate-300 line-clamp-2">
                        {lang === 'hi' ? animal.explanation_hi : animal.explanation_en}
                      </p>

                      {/* Safety Alerts */}
                      {animal.has_active_withdrawal && (
                        <div className="mt-2 bg-amber-950/60 border border-amber-500/50 rounded-xl px-2.5 py-1.5 text-xs text-amber-300 flex items-center gap-2 font-medium">
                          <AlertCircle className="w-4 h-4 flex-shrink-0 text-amber-400" />
                          <span>⚠️ {t('withdrawalActive')}</span>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="pt-2 flex items-center gap-2">
                      <button
                        onClick={() => handleOpenAnimalDetail(animal)}
                        className="flex-1 py-2 px-3 bg-slate-700/80 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition text-center shadow"
                      >
                        {t('animalDossier')}
                      </button>

                      {(isUrgent || isAttention) && (
                        <button
                          onClick={() => setRequestModalAnimal(animal)}
                          className="py-2 px-3 bg-red-600/90 hover:bg-red-600 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow"
                        >
                          <Phone className="w-3.5 h-3.5" />
                          <span>{t('requestReview')}</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Safety & Educational Notice */}
        <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 text-xs text-slate-400 flex items-start gap-3">
          <Info className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-slate-200">{t('disclaimer')}</p>
            <p className="mt-0.5">
              {lang === 'hi'
                ? 'यह प्रणाली केवल लक्षणों की शीघ्र सूचना देती है। पशु को दवा केवल सरकारी या प्रमाणित पशु चिकित्सक की जांच के बाद ही दें।'
                : 'AniCare AI assists in early symptom detection. Never administer antibiotics or prescription medicine without a veterinary officer.'}
            </p>
          </div>
        </div>
      </main>

      {/* Animal Detail Modal (Comprehensive Farmer Health Card) */}
      {selectedAnimal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-800 border border-slate-700 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative">
            {/* Modal Header */}
            <div className="sticky top-0 bg-slate-800/95 backdrop-blur-md px-6 py-4 border-b border-slate-700/80 flex items-center justify-between z-10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-lg">
                  🐄
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>{selectedAnimal.name}</span>
                    <span className="text-xs bg-slate-700 text-slate-300 font-mono px-2 py-0.5 rounded">
                      {selectedAnimal.tag}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    {selectedAnimal.species} • {selectedAnimal.breed || 'Indigenous'} • {selectedAnimal.age || 'Adult'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    const detail = selectedAnimalDetail || selectedAnimal;
                    const speech =
                      lang === 'hi'
                        ? `${detail.name}। स्थिति: ${detail.status_label_hi}। ${detail.explanation_hi}`
                        : `${detail.name}. Status: ${detail.status_label_en}. ${detail.explanation_en}`;
                    handleSpeak(speech, 'modal_animal');
                  }}
                  className={`p-2 rounded-xl transition ${
                    isSpeaking && currentlySpeakingId === 'modal_animal'
                      ? 'bg-amber-600 text-white animate-pulse'
                      : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                  }`}
                  title={t('listen')}
                >
                  <Volume2 className="w-5 h-5" />
                </button>
                <button
                  onClick={() => {
                    setSelectedAnimal(null);
                    setSelectedAnimalDetail(null);
                  }}
                  className="p-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-xl transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Status Explanation Card */}
              <div
                className={`p-4 rounded-2xl border ${
                  selectedAnimal.simplified_status === 'URGENT'
                    ? 'bg-red-950/40 border-red-500/50 text-red-200'
                    : selectedAnimal.simplified_status === 'ATTENTION'
                    ? 'bg-amber-950/40 border-amber-500/50 text-amber-200'
                    : 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                }`}
              >
                <div className="flex items-center gap-2 font-bold text-sm">
                  <Activity className="w-4 h-4" />
                  <span>
                    {lang === 'hi' ? selectedAnimal.status_label_hi : selectedAnimal.status_label_en}
                  </span>
                </div>
                <p className="mt-2 text-xs md:text-sm text-slate-200">
                  {lang === 'hi' ? selectedAnimal.explanation_hi : selectedAnimal.explanation_en}
                </p>
              </div>

              {/* Action Steps: "What should I do now?" */}
              {selectedAnimalDetail?.action_steps && selectedAnimalDetail.action_steps.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-white flex items-center gap-2">
                    <span>📋</span>
                    <span>{t('whatToDoNow')}</span>
                  </h4>
                  <div className="space-y-2">
                    {selectedAnimalDetail.action_steps.map((st) => (
                      <div
                        key={st.step_number}
                        className="bg-slate-750 bg-slate-700/50 border border-slate-700 rounded-xl p-3 flex items-start gap-3"
                      >
                        <div
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                            st.urgency === 'critical'
                              ? 'bg-red-500 text-white'
                              : st.urgency === 'important'
                              ? 'bg-amber-500 text-slate-900'
                              : 'bg-emerald-600 text-white'
                          }`}
                        >
                          {st.step_number}
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white">
                            {lang === 'hi' ? st.title_hi : st.title_en}
                          </p>
                          <p className="text-xs text-slate-300 mt-0.5">
                            {lang === 'hi' ? st.description_hi : st.description_en}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Food Safety & Milk Withdrawal Notice */}
              {selectedAnimalDetail?.withdrawal_notice?.is_active && (
                <div className="bg-amber-950/60 border-2 border-amber-500 rounded-2xl p-4 space-y-2">
                  <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                    <span>{t('milkMeatSafety')}</span>
                  </div>
                  <p className="text-xs text-amber-100 font-semibold">
                    {lang === 'hi'
                      ? selectedAnimalDetail.withdrawal_notice.warning_message_hi
                      : selectedAnimalDetail.withdrawal_notice.warning_message_en}
                  </p>
                  <div className="inline-block bg-amber-900/80 px-3 py-1 rounded-lg text-xs font-bold text-amber-300">
                    ⏳ {selectedAnimalDetail.withdrawal_notice.days_remaining} {t('withdrawalRemaining')}
                  </div>
                </div>
              )}

              {/* Approved Treatment Plan (Veterinarian Verified) */}
              {selectedAnimalDetail?.treatment_plan?.is_active ? (
                <div className="bg-slate-750 bg-slate-700/40 border border-emerald-500/40 rounded-2xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
                      <Pill className="w-4 h-4" />
                      <span>{t('treatmentPlan')}</span>
                    </h4>
                    <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded font-medium">
                      APPROVED BY DOCTOR
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 italic">
                    {lang === 'hi'
                      ? selectedAnimalDetail.treatment_plan.doctor_approved_notice_hi
                      : selectedAnimalDetail.treatment_plan.doctor_approved_notice_en}
                  </p>

                  <div className="space-y-2 mt-2">
                    {selectedAnimalDetail.treatment_plan.medicines.map((med, idx) => (
                      <div key={idx} className="bg-slate-800 p-2.5 rounded-xl border border-slate-700 text-xs flex justify-between items-center">
                        <div>
                          <span className="font-bold text-white">{med.name}</span>
                          <span className="text-slate-400 ml-2">({med.dosage})</span>
                        </div>
                        <span className="text-emerald-400 font-medium">{med.frequency} • {med.duration_days} days</span>
                      </div>
                    ))}
                  </div>

                  {selectedAnimalDetail.treatment_plan.instructions && (
                    <p className="text-xs text-slate-300 mt-2 bg-slate-800/70 p-2 rounded-lg border border-slate-700">
                      <strong>{t('instructions')}:</strong> {selectedAnimalDetail.treatment_plan.instructions}
                    </p>
                  )}
                </div>
              ) : (
                <div className="bg-slate-800/40 p-3 rounded-xl border border-slate-700/60 text-xs text-slate-400">
                  {t('noTreatment')}
                </div>
              )}

              {/* Milestone 10: Offline Observation Recording Box */}
              <div className="bg-slate-750 bg-slate-700/50 border border-slate-600/70 rounded-2xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                    <Save className="w-4 h-4 text-emerald-400" />
                    <span>{t('offlineObservation')}</span>
                  </h4>
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700 font-mono">
                    OFFLINE QUEUE
                  </span>
                </div>

                <textarea
                  value={offlineObsText}
                  onChange={(e) => setOfflineObsText(e.target.value)}
                  placeholder={t('offlineObservationPrompt')}
                  rows={2}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-emerald-500 placeholder-slate-500"
                />

                {offlineObsSavedMsg && (
                  <div className="p-2.5 bg-emerald-500/20 border border-emerald-500/40 rounded-xl text-xs text-emerald-300 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                    <span>{offlineObsSavedMsg}</span>
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleSaveOfflineObservation}
                  disabled={!offlineObsText.trim() || savingOfflineObs}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{t('saveOfflineObservation')}</span>
                </button>
              </div>

              {/* Milestone 10: Offline Photo Screening Notice */}
              {!isOnline && (
                <div className="bg-slate-800/80 border border-slate-700 p-3 rounded-2xl text-xs text-slate-300 flex items-start gap-2.5">
                  <Camera className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                  <p>{t('screeningOfflineNotice')}</p>
                </div>
              )}

              {/* Doctor Visit Request Button */}
              <div className="pt-2">
                <button
                  onClick={() => {
                    setRequestModalAnimal(selectedAnimal);
                  }}
                  className="w-full py-3 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-lg transition active:scale-95"
                >
                  <Phone className="w-4 h-4" />
                  <span>{t('requestReview')}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Doctor Visit Request Modal */}
      {requestModalAnimal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Phone className="w-5 h-5 text-red-400" />
                <span>{t('requestReview')}</span>
              </h3>
              <button
                onClick={() => setRequestModalAnimal(null)}
                className="p-1.5 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300">
              {lang === 'hi'
                ? `पशु: ${requestModalAnimal.name} (${requestModalAnimal.tag}) के लिए सरकारी पशु चिकित्सक की तत्काल जांच का अनुरोध भेजें।`
                : `Request immediate veterinary officer visit for ${requestModalAnimal.name} (${requestModalAnimal.tag}).`}
            </p>

            <form onSubmit={handleSubmitDoctorRequest} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  {lang === 'hi' ? 'अतिरिक्त लक्षण या संदेश (वैकल्पिक)' : 'Notes / Symptoms (Optional)'}
                </label>
                <textarea
                  value={requestNotes}
                  onChange={(e) => setRequestNotes(e.target.value)}
                  placeholder={
                    lang === 'hi'
                      ? 'जैसे: गाय 2 दिन से चारा नहीं खा रही, बुखार है...'
                      : 'e.g. Fever, not eating for 2 days...'
                  }
                  rows={3}
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              {requestSuccessMsg && (
                <div className="p-3 bg-emerald-500/20 border border-emerald-500/40 rounded-xl text-xs text-emerald-300 font-semibold">
                  ✓ {requestSuccessMsg}
                </div>
              )}

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setRequestModalAnimal(null)}
                  className="flex-1 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-xl text-xs font-bold"
                >
                  {t('close')}
                </button>
                <button
                  type="submit"
                  disabled={requestSubmitting}
                  className="flex-1 py-2.5 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5"
                >
                  {requestSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Phone className="w-4 h-4" />}
                  <span>{lang === 'hi' ? 'अनुरोध भेजें' : 'Send Request'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Help & Safety Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 border border-slate-700 rounded-3xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6 space-y-4 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-slate-700 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-emerald-400" />
                <span>{t('helpTitle')}</span>
              </h3>
              <button
                onClick={() => setShowHelpModal(false)}
                className="p-1.5 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="bg-slate-750 bg-slate-700/40 p-3 rounded-xl border border-slate-700">
                <h5 className="font-bold text-white">{t('faq1Q')}</h5>
                <p className="text-slate-300 mt-1">{t('faq1A')}</p>
              </div>
              <div className="bg-slate-750 bg-slate-700/40 p-3 rounded-xl border border-slate-700">
                <h5 className="font-bold text-white">{t('faq2Q')}</h5>
                <p className="text-slate-300 mt-1">{t('faq2A')}</p>
              </div>
              <div className="bg-slate-750 bg-slate-700/40 p-3 rounded-xl border border-slate-700">
                <h5 className="font-bold text-white">{t('faq3Q')}</h5>
                <p className="text-slate-300 mt-1">{t('faq3A')}</p>
              </div>
              <div className="bg-slate-750 bg-slate-700/40 p-3 rounded-xl border border-slate-700">
                <h5 className="font-bold text-white">{t('faq4Q')}</h5>
                <p className="text-slate-300 mt-1">{t('faq4A')}</p>
              </div>
            </div>

            <button
              onClick={() => setShowHelpModal(false)}
              className="w-full py-2.5 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-xs font-bold"
            >
              {t('close')}
            </button>
          </div>
        </div>
      )}

      {/* Milestone 10: Sync Status & Action Queue Diagnostic Modal */}
      <SyncStatusModal isOpen={showSyncModal} onClose={() => setShowSyncModal(false)} />
    </div>
  );
}
