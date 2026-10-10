import React from 'react';

const variantClasses = {
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-500/20',
  warning: 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-500/20',
  danger: 'bg-rose-50 text-rose-700 border-rose-200 ring-rose-500/20',
  critical: 'bg-rose-100 text-rose-800 border-rose-300 ring-rose-500/30',
  info: 'bg-sky-50 text-sky-700 border-sky-200 ring-sky-500/20',
  indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200 ring-indigo-500/20',
  neutral: 'bg-slate-100 text-slate-700 border-slate-200 ring-slate-400/20',
};

const dotColors = {
  success: 'bg-emerald-500',
  warning: 'bg-amber-500',
  danger: 'bg-rose-500',
  critical: 'bg-rose-600',
  info: 'bg-sky-500',
  indigo: 'bg-indigo-500',
  neutral: 'bg-slate-400',
};

export default function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  pulse = false,
  className = '',
  icon: Icon
}) {
  const chosenVariant = variantClasses[variant] || variantClasses.neutral;
  const dotColor = dotColors[variant] || dotColors.neutral;

  const sizeClass = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ring-1 ring-inset ${chosenVariant} ${sizeClass} ${className}`}
    >
      {pulse && (
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${dotColor}`}></span>
          <span className={`relative inline-flex rounded-full h-2 w-2 ${dotColor}`}></span>
        </span>
      )}
      {Icon && <Icon className="w-3 h-3 flex-shrink-0" />}
      <span>{children}</span>
    </span>
  );
}
