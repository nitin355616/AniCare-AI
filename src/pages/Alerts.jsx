import React, { useState, useMemo } from 'react';
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  PhoneCall,
  Send,
  ShieldAlert,
  Radio,
  MapPin,
  Clock,
  Filter,
  Check,
  Share2,
  MessageSquare,
  Syringe,
  History,
  Activity,
  Layers
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import { MOCK_ALERTS } from '../data/mockData';

export default function Alerts() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS);
  const [selectedType, setSelectedType] = useState('All');
  const [selectedSeverity, setSelectedSeverity] = useState('All');
  const [showBroadcastModal, setShowBroadcastModal] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const alertCategories = [
    'All',
    'Critical Alert',
    'Disease-Risk Alert',
    'Follow-up Reminder',
    'Vaccination Reminder',
    'Preventive Alert'
  ];

  const severityLevels = ['All', 'Critical', 'High', 'Medium', 'Low'];

  const filteredAlerts = useMemo(() => {
    return alerts.filter((alert) => {
      const matchType = selectedType === 'All' || alert.alertType === selectedType;
      const matchSeverity = selectedSeverity === 'All' || alert.severity === selectedSeverity;
      return matchType && matchSeverity;
    });
  }, [alerts, selectedType, selectedSeverity]);

  const handleAcknowledge = (id) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: 'Acknowledged' } : a))
    );
    showToast(`Alert ${id} acknowledged and logged in surveillance ledger.`);
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
        title="Epizootic Early-Warning & Alerts Desk"
        subtitle="Automated syndromic anomaly alerts, bio-containment geofence breach triggers, vaccination reminders, and farmer broadcasts."
        badge={
          <Badge variant="danger" pulse>
            {alerts.filter((a) => a.severity === 'Critical').length} Critical Unresolved
          </Badge>
        }
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              icon={Check}
              onClick={() => {
                setAlerts((prev) => prev.map((a) => ({ ...a, status: 'Acknowledged' })));
                showToast('All active alerts marked as acknowledged.');
              }}
            >
              Acknowledge All
            </Button>
            <Button
              variant="danger"
              size="sm"
              icon={Radio}
              onClick={() => setShowBroadcastModal(true)}
            >
              Broadcast Farmer Advisory
            </Button>
          </>
        }
      />

      {/* Category Pills & Severity Filter Card */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
        {/* Category filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <span className="font-bold text-slate-400 uppercase mr-1">Alert Type:</span>
          {alertCategories.map((type) => {
            const count =
              type === 'All'
                ? alerts.length
                : alerts.filter((a) => a.alertType === type).length;
            const isSelected = selectedType === type;
            return (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors whitespace-nowrap flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-slate-900 text-white font-bold shadow-xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                <span>{type}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                    isSelected ? 'bg-slate-700 text-white' : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Severity filters */}
        <div className="flex items-center justify-between gap-3 pt-2.5 border-t border-slate-100 flex-wrap text-xs">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-slate-400 uppercase">Severity Level:</span>
            {severityLevels.map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                  selectedSeverity === sev
                    ? 'bg-emerald-600 text-white font-bold'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>

          <span className="text-slate-400 font-medium">
            Showing {filteredAlerts.length} of {alerts.length} incidents
          </span>
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-4">
        {filteredAlerts.map((alert) => {
          const isCritical = alert.severity === 'Critical';
          const isHigh = alert.severity === 'High';
          const isMed = alert.severity === 'Medium';

          return (
            <div
              key={alert.id}
              className={`bg-white rounded-xl border p-5 shadow-xs transition-all duration-200 ${
                isCritical
                  ? 'border-rose-300 ring-1 ring-rose-500/20 bg-rose-50/10'
                  : isHigh
                  ? 'border-rose-200'
                  : isMed
                  ? 'border-amber-200'
                  : 'border-slate-200'
              }`}
            >
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="flex items-start gap-3.5 min-w-0">
                  <div
                    className={`p-2.5 rounded-xl flex-shrink-0 mt-0.5 ${
                      isCritical
                        ? 'bg-rose-100 text-rose-700 border border-rose-200'
                        : isHigh
                        ? 'bg-rose-50 text-rose-600 border border-rose-200'
                        : isMed
                        ? 'bg-amber-50 text-amber-600 border border-amber-200'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    <AlertTriangle className="w-5 h-5" />
                  </div>

                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {alert.id}
                      </span>
                      <h3 className="font-bold text-base text-slate-900">
                        {alert.title}
                      </h3>
                      <Badge
                        variant={isCritical ? 'critical' : isHigh ? 'danger' : isMed ? 'warning' : 'neutral'}
                        size="sm"
                        pulse={isCritical}
                      >
                        {alert.severity} Severity
                      </Badge>
                      <Badge variant="neutral" size="sm">
                        {alert.alertType || alert.category}
                      </Badge>
                    </div>

                    <p className="text-xs sm:text-sm text-slate-600 mt-1.5 leading-relaxed">
                      {alert.description}
                    </p>

                    {/* Metadata chips */}
                    <div className="mt-2.5 flex items-center gap-3 text-xs text-slate-500 flex-wrap">
                      <span className="flex items-center gap-1 font-semibold text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {alert.location}
                      </span>
                      <span>&bull;</span>
                      <span className="font-mono font-medium text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded">
                        Target: {alert.affectedTag}
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1 text-slate-400">
                        <Clock className="w-3.5 h-3.5" />
                        {alert.timestamp}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Status & Action Buttons */}
                <div className="flex flex-col sm:flex-row items-end sm:items-center gap-2.5 flex-shrink-0 w-full md:w-auto pt-3 md:pt-0 border-t md:border-t-0 border-slate-100">
                  <div className="text-right sm:text-left mr-2">
                    <span className="text-[10px] font-bold text-slate-400 block uppercase">
                      Action State
                    </span>
                    <span className="text-xs font-bold text-emerald-700">
                      {alert.dispatchStatus}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {alert.status !== 'Acknowledged' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAcknowledge(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                    <Button
                      variant={isCritical ? 'danger' : 'primary'}
                      size="sm"
                      onClick={() => {
                        showToast(`Simulated Intervention: Protocol enacted for ${alert.id}.`);
                      }}
                    >
                      Enact Protocol
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Broadcast Modal to Farmers */}
      {showBroadcastModal && (
        <Modal
          isOpen={showBroadcastModal}
          onClose={() => setShowBroadcastModal(false)}
          title="Simulate WhatsApp & SMS Farmer Broadcast"
          subtitle="Direct bio-containment advisory broadcast to dairy cooperative members"
          maxWidth="max-w-lg"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowBroadcastModal(false)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                icon={Send}
                onClick={() => {
                  showToast('Simulation: Advisory broadcast dispatched to 142 registered cooperative members.');
                  setShowBroadcastModal(false);
                }}
              >
                Dispatch Mass Advisory
              </Button>
            </>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800">
              <p className="font-bold text-rose-950 uppercase text-[11px]">
                Target Bio-Safety Geofence:
              </p>
              <p className="text-xs mt-0.5">
                Sector 04, Anand District &bull; 142 Cooperative Livestock Owners &bull; Est. 1,420 heads
              </p>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Advisory Template:
              </label>
              <select className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white">
                <option>Lumpy Skin Disease Cluster Alert & Vector Spray Advisory</option>
                <option>FMD Suspect Ring Quarantine & Disinfection Instructions</option>
                <option>Preventive Brucellosis Vaccination Drive Alert</option>
              </select>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Advisory Message Preview (Multilingual Auto-Translate):
              </label>
              <div className="p-3 bg-slate-50 border border-slate-300 rounded-lg font-mono text-[11px] text-slate-700 leading-relaxed">
                "[AniCare Alert] ALERT: Lumpy Skin cases detected within 10km. Please inspect cattle for skin nodules and fever. Restrict cattle movement to local mandi. Mobile Vet #02 on duty at 1800-419-8800."
              </div>
            </div>

            <div className="flex items-center gap-2 text-slate-500">
              <MessageSquare className="w-4 h-4 text-emerald-600" />
              <span>Channels: SMS Gateway &bull; WhatsApp Business API &bull; IVR Voice Call</span>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
