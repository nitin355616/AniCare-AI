import React, { useState } from 'react';
import {
  Menu,
  Bell,
  Search,
  PhoneCall,
  ShieldCheck,
  ChevronDown,
  User,
  HeartPulse,
  AlertTriangle,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';
import Button from '../common/Button';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import { MOCK_ALERTS } from '../../data/mockData';

export default function Topbar({ onOpenSidebar }) {
  const [showSosModal, setShowSosModal] = useState(false);
  const [showNotificationMenu, setShowNotificationMenu] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between gap-4">
          {/* Left: Mobile hamburger & breadcrumb/status */}
          <div className="flex items-center gap-3">
            <button
              onClick={onOpenSidebar}
              className="lg:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
              aria-label="Open sidebar navigation"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="hidden sm:flex items-center gap-2 text-xs">
              <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200 flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
                National Epi-Surveillance Feed Active
              </span>
              <span className="text-slate-300">/</span>
              <span className="text-slate-500 font-medium">Zone: Anand-Gujarat Dairy Cluster</span>
            </div>
          </div>

          {/* Right: Actions & User profile */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Quick SOS Emergency Action Button */}
            <Button
              variant="danger"
              size="sm"
              icon={PhoneCall}
              onClick={() => setShowSosModal(true)}
              className="shadow-sm shadow-rose-600/30 font-semibold"
            >
              <span className="hidden sm:inline">SOS Outbreak Triage</span>
              <span className="sm:hidden">SOS</span>
            </Button>

            {/* Notification bell dropdown button */}
            <div className="relative">
              <button
                onClick={() => setShowNotificationMenu(!showNotificationMenu)}
                className="relative p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-600 text-[10px] font-bold text-white ring-2 ring-white">
                  3
                </span>
              </button>

              {/* Notification Popover */}
              {showNotificationMenu && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="px-4 py-2 border-b border-slate-100 flex items-center justify-between">
                    <span className="font-semibold text-sm text-slate-900">
                      Recent High-Priority Alerts
                    </span>
                    <Link
                      to="/alerts"
                      onClick={() => setShowNotificationMenu(false)}
                      className="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
                    >
                      View All
                    </Link>
                  </div>
                  <div className="divide-y divide-slate-100 max-h-72 overflow-y-auto">
                    {MOCK_ALERTS.slice(0, 3).map((alert) => (
                      <Link
                        key={alert.id}
                        to="/alerts"
                        onClick={() => setShowNotificationMenu(false)}
                        className="p-3 hover:bg-slate-50 transition-colors flex items-start gap-3 block"
                      >
                        <div className={`p-1.5 rounded-lg flex-shrink-0 ${
                          alert.severity === 'Critical' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600'
                        }`}>
                          <AlertTriangle className="w-4 h-4" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs font-semibold text-slate-800 line-clamp-1">
                            {alert.title}
                          </p>
                          <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                            {alert.affectedTag} &bull; {alert.timestamp}
                          </p>
                        </div>
                      </Link>
                    ))}
                  </div>
                  <div className="px-4 py-2 border-t border-slate-100 bg-slate-50/70 text-center">
                    <span className="text-[11px] text-slate-500">
                      Simulated notification feed &bull; SIH 2026 Prototype
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Avatar & Info */}
            <div className="flex items-center gap-2.5 pl-2 sm:pl-3 border-l border-slate-200">
              <img
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80"
                alt="Dr. Arvind Verma"
                className="w-8 h-8 rounded-full object-cover ring-2 ring-emerald-500/30"
              />
              <div className="hidden md:block text-left">
                <p className="text-xs font-bold text-slate-900 leading-tight">
                  Dr. Arvind Verma
                </p>
                <p className="text-[11px] text-slate-500 leading-tight">
                  Field Epi-Officer &bull; DAHD
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* SOS Outbreak Modal */}
      <Modal
        isOpen={showSosModal}
        onClose={() => setShowSosModal(false)}
        title="Emergency Epizootic Outbreak Protocol (SOS)"
        subtitle="National Animal Disease Emergency Response — Simulated Trigger"
        maxWidth="max-w-xl"
        footer={
          <>
            <Button variant="outline" size="sm" onClick={() => setShowSosModal(false)}>
              Close
            </Button>
            <Button
              variant="danger"
              size="sm"
              icon={PhoneCall}
              onClick={() => {
                alert("Simulated Protocol: National Veterinary Emergency Network notified. In production, this dispatches real SMS/IVR to District Animal Husbandry Officers.");
                setShowSosModal(false);
              }}
            >
              Simulate Emergency Broadcast
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-sm text-slate-600">
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-600 mt-0.5" />
            <div>
              <p className="font-semibold text-xs uppercase tracking-wide text-rose-900">
                Outbreak Rapid Containment Procedure
              </p>
              <p className="text-xs mt-1 leading-relaxed">
                Triggering an SOS immediately flags all livestock within a 10km radius as a high-risk surveillance buffer under the Prevention and Control of Infectious and Contagious Diseases in Animals Act.
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-700 block">
              Suspected Contagion Classification:
            </label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 font-medium">
                Foot and Mouth Disease (FMD)
              </div>
              <div className="p-2.5 rounded-lg border border-emerald-500 bg-emerald-50 text-emerald-800 font-semibold">
                Lumpy Skin Disease (LSD) [Selected]
              </div>
              <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 font-medium">
                PPR (Peste des Petits Ruminants)
              </div>
              <div className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 font-medium">
                Avian Influenza / H5N1
              </div>
            </div>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1.5 border border-slate-200">
            <p className="font-medium text-slate-800">Simulated Automated Actions to be Executed:</p>
            <ul className="list-disc pl-4 space-y-1 text-slate-600">
              <li>Instant WhatsApp/SMS broadcast to 14 registered dairy farmers in Sector 04.</li>
              <li>Pre-alerting Anand District Polyclinic Mobile Emergency Unit #02.</li>
              <li>Freezing interstate livestock movement checkpoint e-passes for zone.</li>
            </ul>
          </div>
        </div>
      </Modal>
    </>
  );
}
