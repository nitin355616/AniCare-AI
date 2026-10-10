import React from 'react';
import { Activity } from 'lucide-react';

export default function LoadingSpinner({
  message = 'Loading telemetry & records...',
  subtext = 'Connecting to AniCare secure node',
  fullPage = false,
  className = ''
}) {
  const content = (
    <div className={`flex flex-col items-center justify-center text-center p-8 ${className}`}>
      <div className="relative flex items-center justify-center w-14 h-14 mb-4">
        <div className="absolute inset-0 rounded-full border-4 border-emerald-100 border-t-emerald-600 animate-spin" />
        <Activity className="w-6 h-6 text-emerald-600 animate-pulse" />
      </div>
      <p className="text-sm font-semibold text-slate-800">{message}</p>
      {subtext && <p className="text-xs text-slate-500 mt-1">{subtext}</p>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
}
