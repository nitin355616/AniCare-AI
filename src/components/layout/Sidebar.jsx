import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  PawPrint,
  ScanEye,
  FileText,
  ShieldPlus,
  AlertTriangle,
  BarChart3,
  X,
  Settings,
  LogOut,
  Building2,
  CheckCircle2,
  Shield,
  Bell,
  Cpu,
  Info,
  Radio,
  Activity,
  UserCheck,
  Compass,
  ShieldAlert,
  Sparkles,
  Award,
  ShieldCheck,
  HelpCircle,
  Database
} from 'lucide-react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { CURRENT_USER } from '../../data/mockData';

const sihNavItems = [
  {
    name: 'SIH Live Demo',
    to: '/sih-demo',
    icon: Sparkles,
    badge: '10 Stages',
    badgeType: 'vet',
  },
  {
    name: 'Executive Pitch',
    to: '/sih-dashboard',
    icon: Award,
    badge: 'National',
    badgeType: 'ai',
  },
  {
    name: 'AI Validation',
    to: '/ai-validation',
    icon: ShieldCheck,
    badge: '92.75%',
    badgeType: 'ai',
  },
  {
    name: 'Jury Q&A Defense',
    to: '/jury-qa',
    icon: HelpCircle,
    badge: '8 Qs',
    badgeType: 'alert',
  },
  {
    name: 'SIH Matrix',
    to: '/sih-mapping',
    icon: FileText,
    badge: 'Audit',
    badgeType: 'neutral',
  },
];

const navItems = [
  {
    name: 'Dashboard',
    to: '/',
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: 'Animals',
    to: '/animals',
    icon: PawPrint,
    badge: '1.4k',
    badgeType: 'neutral',
  },
  {
    name: 'Disease Detection',
    to: '/disease-detection',
    icon: ScanEye,
    badge: 'AI Active',
    badgeType: 'ai',
  },
  {
    name: 'Dataset Explorer',
    to: '/dataset-explorer',
    icon: Database,
    badge: '5 Sets',
    badgeType: 'ai',
  },
  {
    name: 'Health Reports',
    to: '/reports',
    icon: FileText,
    badge: null,
  },
  {
    name: 'Veterinary Care',
    to: '/veterinary',
    icon: ShieldPlus,
    badge: '4 Duty',
    badgeType: 'vet',
  },
  {
    name: 'Alerts',
    to: '/alerts',
    icon: AlertTriangle,
    badge: '9',
    badgeType: 'alert',
  },
  {
    name: 'Outbreak Intel',
    to: '/outbreaks',
    icon: Radio,
    badge: 'Early Warn',
    badgeType: 'ai',
  },
  {
    name: 'Farmer Portal',
    to: '/farmer',
    icon: UserCheck,
    badge: 'Hindi/EN',
    badgeType: 'vet',
  },
  {
    name: 'AI Monitoring',
    to: '/ai-monitoring',
    icon: Activity,
    badge: 'Continuous',
    badgeType: 'ai',
  },
  {
    name: 'Geospatial Intel',
    to: '/geospatial',
    icon: Compass,
    badge: 'Risk Map',
    badgeType: 'ai',
  },
  {
    name: 'Response Command',
    to: '/response',
    icon: ShieldAlert,
    badge: 'Govt Action',
    badgeType: 'alert',
  },
  {
    name: 'Analytics',
    to: '/analytics',
    icon: BarChart3,
    badge: null,
  },
];


export default function Sidebar({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showAboutModal, setShowAboutModal] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [settingsTab, setSettingsTab] = useState('profile'); // 'profile' | 'telemetry'
  const [telemetryFrequency, setTelemetryFrequency] = useState('5m');
  const [alertTone, setAlertTone] = useState(true);
  const [farmerProfile, setFarmerProfile] = useState({
    name: 'Ramesh Patel',
    phone: '+91 98765 43210',
    village: 'Mogar, Anand District, Gujarat',
    herdSize: '14 Cattle & Buffaloes',
    lang: 'hi',
  });

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-40 w-72 bg-slate-950 text-slate-200 border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-lg shadow-emerald-950/60 border border-emerald-400/20">
              <PawPrint className="w-5 h-5 transform -rotate-12" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-bold text-white tracking-tight">AniCare</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-extrabold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  AI
                </span>
              </div>
              <p className="text-[11px] font-medium text-slate-400">
                SIH 2026 National Platform
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
            aria-label="Close navigation"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Live IoT Node Telemetry Status */}
        <div className="px-4 py-2.5 bg-slate-900/70 border-b border-slate-800/60 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-slate-300 font-medium text-[11px]">IoT Gateway: Connected</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/40">
            Node #GJ-04
          </span>
        </div>

        {/* Main Navigation List */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {/* SIH Jury & Evaluation Section */}
          <div className="px-3 pb-2 pt-1 text-[10px] font-bold text-emerald-400 uppercase tracking-wider flex items-center justify-between">
            <span>SIH 2026 Evaluation</span>
            <span className="px-1.5 py-0.2 rounded text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Jury Ready</span>
          </div>

          {sihNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => {
                  if (window.innerWidth < 1024) onClose();
                }}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2 rounded-xl text-xs font-semibold transition-all group ${
                    isActive
                      ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-950/50'
                      : 'text-slate-300 hover:bg-slate-900/90 hover:text-white'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-2.5">
                      <Icon
                        className={`w-4 h-4 transition-colors ${
                          isActive
                            ? 'text-white'
                            : 'text-emerald-400 group-hover:text-emerald-300'
                        }`}
                      />
                      <span>{item.name}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[9px] px-2 py-0.5 rounded-full font-bold transition-colors ${
                          isActive
                            ? 'bg-emerald-800 text-emerald-100'
                            : item.badgeType === 'alert'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : item.badgeType === 'ai'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : item.badgeType === 'vet'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}

          <div className="my-2 border-t border-slate-800/80" />

          <div className="px-3 pb-2 pt-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
            Surveillance & Clinical Care
          </div>

          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => {
                  if (window.innerWidth < 1024) onClose();
                }}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/50 font-semibold'
                      : 'text-slate-300 hover:bg-slate-900/90 hover:text-white'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3">
                      <Icon
                        className={`w-4 h-4 sm:w-5 sm:h-5 transition-colors ${
                          isActive
                            ? 'text-white'
                            : 'text-slate-400 group-hover:text-emerald-400'
                        }`}
                      />
                      <span>{item.name}</span>
                    </div>

                    {item.badge && (
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-bold transition-colors ${
                          isActive
                            ? 'bg-emerald-700 text-emerald-100'
                            : item.badgeType === 'alert'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : item.badgeType === 'ai'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                            : item.badgeType === 'vet'
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* User Profile, Settings & Logout Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950">
          {/* User profile card */}
          <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <img
                src={CURRENT_USER.avatar}
                alt={CURRENT_USER.name}
                className="w-9 h-9 rounded-full object-cover ring-2 ring-emerald-500/40 flex-shrink-0"
              />
              <div className="min-w-0">
                <p className="text-xs font-bold text-white truncate">
                  {CURRENT_USER.name}
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {CURRENT_USER.role.split(' ')[0]} &bull; DAHD Govt
                </p>
              </div>
            </div>
          </div>

          {/* Settings, About & Logout Action Buttons */}
          <div className="grid grid-cols-3 gap-1 pt-1">
            <button
              onClick={() => setShowAboutModal(true)}
              className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              <Info className="w-3.5 h-3.5 text-slate-400" />
              <span>About</span>
            </button>
            <button
              onClick={() => setShowSettingsModal(true)}
              className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              <Settings className="w-3.5 h-3.5 text-slate-400" />
              <span>Settings</span>
            </button>
            <button
              onClick={() => setShowLogoutModal(true)}
              className="flex items-center justify-center gap-1 px-2 py-1.5 rounded-lg text-xs font-medium text-rose-300 hover:text-rose-200 hover:bg-rose-950/40 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5 text-rose-400" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Settings Modal (Farmer Profile & System Telemetry) */}
      {showSettingsModal && (
        <Modal
          isOpen={showSettingsModal}
          onClose={() => setShowSettingsModal(false)}
          title="Farmer Profile & System Settings"
          subtitle="Manage farm identity, regional language, and edge sensor telemetry"
          maxWidth="max-w-lg"
          footer={
            <Button variant="primary" size="sm" onClick={() => setShowSettingsModal(false)}>
              Save Preferences
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            {/* Tabs switcher */}
            <div className="flex border-b border-slate-200 gap-2">
              <button
                onClick={() => setSettingsTab('profile')}
                className={`pb-2 px-3 font-bold text-xs border-b-2 transition-colors ${
                  settingsTab === 'profile'
                    ? 'border-emerald-600 text-emerald-800'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Farmer Profile & Identity
              </button>
              <button
                onClick={() => setSettingsTab('telemetry')}
                className={`pb-2 px-3 font-bold text-xs border-b-2 transition-colors ${
                  settingsTab === 'telemetry'
                    ? 'border-emerald-600 text-emerald-800'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                IoT Telemetry & Edge Polling
              </button>
            </div>

            {settingsTab === 'profile' ? (
              <div className="space-y-3 pt-1">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Farmer / Owner Name</label>
                  <input
                    type="text"
                    value={farmerProfile.name}
                    onChange={(e) => setFarmerProfile({ ...farmerProfile, name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Mobile Contact</label>
                    <input
                      type="text"
                      value={farmerProfile.phone}
                      onChange={(e) => setFarmerProfile({ ...farmerProfile, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono"
                    />
                  </div>
                  <div>
                    <label className="font-semibold text-slate-700 block mb-1">Preferred Language</label>
                    <select
                      value={farmerProfile.lang}
                      onChange={(e) => setFarmerProfile({ ...farmerProfile, lang: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                    >
                      <option value="hi">हिंदी (Hindi)</option>
                      <option value="en">English (Official)</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Village & District</label>
                  <input
                    type="text"
                    value={farmerProfile.village}
                    onChange={(e) => setFarmerProfile({ ...farmerProfile, village: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Registered Herd Size</label>
                  <input
                    type="text"
                    value={farmerProfile.herdSize}
                    onChange={(e) => setFarmerProfile({ ...farmerProfile, herdSize: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-4 pt-1 text-slate-600">
                <div>
                  <label className="font-semibold text-slate-800 block mb-1">
                    Telemetry Synchronization Interval:
                  </label>
                  <select
                    value={telemetryFrequency}
                    onChange={(e) => setTelemetryFrequency(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-white"
                  >
                    <option value="1m">Real-time Stream (Every 1 min)</option>
                    <option value="5m">Standard Edge Interval (Every 5 mins) [Recommended]</option>
                    <option value="15m">Low-Power IoT Mode (Every 15 mins)</option>
                  </select>
                </div>

                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <div>
                    <p className="font-bold text-slate-800">Critical Audio Siren / Beeper</p>
                    <p className="text-[11px] text-slate-500">Play alert chime for Epizootic Class A anomalies</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={alertTone}
                    onChange={(e) => setAlertTone(e.target.checked)}
                    className="w-4 h-4 accent-emerald-600"
                  />
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-500 space-y-1">
                  <p className="font-semibold text-slate-700">Connected Hub Information:</p>
                  <p>Node Gateway: #GJ-04 &bull; Firmware: v1.4.2-Prod</p>
                  <p>Cloud Relay: Western Regional Veterinary Data Server</p>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* About AniCare AI Modal */}
      {showAboutModal && (
        <Modal
          isOpen={showAboutModal}
          onClose={() => setShowAboutModal(false)}
          title="About AniCare AI"
          subtitle="AI-Powered Animal Health & Disease Early Warning System (SIH 2026)"
          maxWidth="max-w-xl"
          footer={
            <Button variant="primary" size="sm" onClick={() => setShowAboutModal(false)}>
              Got It
            </Button>
          }
        >
          <div className="space-y-3.5 text-xs text-slate-600 leading-relaxed">
            <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-950 space-y-1">
              <h4 className="font-bold text-sm">Empowering Smallholder Livestock Farmers</h4>
              <p>
                AniCare AI bridges the critical gap between rural livestock farmers and veterinary healthcare systems through edge-compatible multimodal AI triage, disease early warning, and statutory-compliant veterinary workflows.
              </p>
            </div>

            <div className="space-y-2">
              <h5 className="font-bold text-slate-800 uppercase text-[11px]">System Capabilities & Specifications:</h5>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-800 block">AI Vision Engine:</strong>
                  <span>EfficientNet-B0 ONNX Runtime with frozen diagnostic threshold &tau; = 0.50</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-800 block">Multilingual UX:</strong>
                  <span>Bilingual (Hindi / English) with Web Speech API audio synthesis</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-800 block">Offline-First Architecture:</strong>
                  <span>IndexedDB local queue with idempotent background sync</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                  <strong className="text-slate-800 block">Statutory Compliance:</strong>
                  <span>Strict human-in-the-loop: Zero autonomous prescription. DAHD & OIE standards</span>
                </div>
              </div>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-[11px] space-y-1 text-slate-500">
              <p><strong>Developed For:</strong> Smart India Hackathon (SIH 2026)</p>
              <p><strong>Stack:</strong> React 18, Vite, Tailwind CSS, FastAPI, MongoDB, ONNX Runtime</p>
              <p><strong>Version:</strong> v1.4.0 Production Build</p>
            </div>
          </div>
        </Modal>
      )}

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <Modal
          isOpen={showLogoutModal}
          onClose={() => setShowLogoutModal(false)}
          title="Sign Out of AniCare Surveillance Hub"
          subtitle="Confirm termination of active surveillance session"
          maxWidth="max-w-sm"
          footer={
            <>
              <Button variant="outline" size="sm" onClick={() => setShowLogoutModal(false)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  setShowLogoutModal(false);
                  alert("Simulation: Session terminated. In production, this redirects to the National SSO authentication gateway.");
                }}
              >
                Confirm Sign Out
              </Button>
            </>
          }
        >
          <p className="text-xs text-slate-600 leading-relaxed">
            You are signed in as <strong>{CURRENT_USER.name}</strong> ({CURRENT_USER.role}). Any uncommitted manual diagnostic notes will remain stored in local offline browser cache.
          </p>
        </Modal>
      )}
    </>
  );
}
