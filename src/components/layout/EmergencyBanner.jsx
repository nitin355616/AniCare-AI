import React, { useState } from 'react';
import { AlertTriangle, X, ShieldAlert, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function EmergencyBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="bg-gradient-to-r from-amber-600 via-amber-700 to-rose-700 text-white text-xs sm:text-sm px-4 py-2 shadow-inner">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 overflow-hidden">
          <span className="flex-shrink-0 inline-flex items-center gap-1 bg-white/20 px-2 py-0.5 rounded font-mono text-[11px] font-bold uppercase tracking-wider">
            <Sparkles className="w-3 h-3 text-amber-200" />
            SIH 2026 DEMO
          </span>
          <p className="truncate font-medium">
            <span className="hidden sm:inline">Active Surveillance Alert: </span>
            <span className="font-semibold text-amber-100">7 clustered Lumpy Skin Disease cases</span> reported in Anand radius. Early containment protocol active.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <Link
            to="/alerts"
            className="text-xs font-semibold underline underline-offset-2 hover:text-amber-100 whitespace-nowrap"
          >
            Review Geofence &rarr;
          </Link>
          <button
            onClick={() => setDismissed(true)}
            className="text-white/80 hover:text-white p-0.5 rounded"
            title="Dismiss notification"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
