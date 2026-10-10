import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const colorThemes = {
  emerald: {
    iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    trendUp: 'text-emerald-700 bg-emerald-50',
    ring: 'focus:ring-emerald-500',
  },
  rose: {
    iconBg: 'bg-rose-50 text-rose-600 border-rose-100',
    trendUp: 'text-rose-700 bg-rose-50',
    ring: 'focus:ring-rose-500',
  },
  amber: {
    iconBg: 'bg-amber-50 text-amber-600 border-amber-100',
    trendUp: 'text-amber-700 bg-amber-50',
    ring: 'focus:ring-amber-500',
  },
  sky: {
    iconBg: 'bg-sky-50 text-sky-600 border-sky-100',
    trendUp: 'text-sky-700 bg-sky-50',
    ring: 'focus:ring-sky-500',
  },
  indigo: {
    iconBg: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    trendUp: 'text-indigo-700 bg-indigo-50',
    ring: 'focus:ring-indigo-500',
  },
};

export default function StatCard({
  title,
  value,
  change,
  changeType = 'up', // 'up' | 'down' | 'neutral'
  changeLabel,
  caption,
  icon: Icon,
  theme = 'emerald',
  className = '',
  onClick
}) {
  const t = colorThemes[theme] || colorThemes.emerald;

  return (
    <div
      onClick={onClick}
      className={`relative overflow-hidden bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm transition-all duration-200 hover:shadow-md hover:border-slate-300 ${
        onClick ? 'cursor-pointer' : ''
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <div className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
            {value}
          </div>
        </div>

        {Icon && (
          <div className={`p-2.5 rounded-xl border ${t.iconBg} flex-shrink-0`}>
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        )}
      </div>

      {(change || caption) && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          {change ? (
            <div className="flex items-center gap-1.5 font-medium">
              <span
                className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-semibold ${
                  changeType === 'up'
                    ? 'bg-emerald-50 text-emerald-700'
                    : changeType === 'down'
                    ? 'bg-rose-50 text-rose-700'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                {changeType === 'up' && <TrendingUp className="w-3 h-3" />}
                {changeType === 'down' && <TrendingDown className="w-3 h-3" />}
                {change}
              </span>
              {changeLabel && <span className="text-slate-500">{changeLabel}</span>}
            </div>
          ) : (
            <span />
          )}

          {caption && <span className="text-slate-400 truncate max-w-[150px]">{caption}</span>}
        </div>
      )}
    </div>
  );
}
