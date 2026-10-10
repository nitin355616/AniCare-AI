import React from 'react';

export default function HealthScoreGauge({
  score = 92.4,
  label = "Herd Health Index",
  subtitle = "High Overall Biosecurity Status"
}) {
  // SVG semi-circle gauge calculation
  const radius = 70;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-48 h-28 flex items-center justify-center">
        <svg className="w-48 h-48 -rotate-180 transform overflow-visible" viewBox="0 0 160 160">
          {/* Background track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset="0"
            strokeLinecap="round"
          />
          {/* Progress track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="url(#gauge-gradient)"
            strokeWidth="14"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
          />
          <defs>
            <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="70%" stopColor="#059669" />
              <stop offset="100%" stopColor="#047857" />
            </linearGradient>
          </defs>
        </svg>

        {/* Centered score text */}
        <div className="absolute bottom-2 flex flex-col items-center text-center">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {score}%
          </span>
          <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full mt-0.5 border border-emerald-200">
            Grade A1 Health
          </span>
        </div>
      </div>

      <div className="mt-3 text-center">
        <p className="text-sm font-semibold text-slate-800">{label}</p>
        <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
      </div>

      {/* Breakdown metrics */}
      <div className="grid grid-cols-3 gap-2 w-full mt-4 pt-4 border-t border-slate-100 text-center">
        <div>
          <p className="text-[10px] uppercase font-bold text-slate-400">Normal</p>
          <p className="text-xs font-bold text-emerald-600">92.8%</p>
        </div>
        <div>
          <p className="text-[10px] uppercase font-bold text-slate-400">Under Obs</p>
          <p className="text-xs font-bold text-amber-600">5.2%</p>
        </div>
        <div>
          <p className="text-[10px] uppercase font-bold text-slate-400">Isolated</p>
          <p className="text-xs font-bold text-rose-600">2.0%</p>
        </div>
      </div>
    </div>
  );
}
