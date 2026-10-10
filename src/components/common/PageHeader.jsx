import React from 'react';

export default function PageHeader({
  title,
  subtitle,
  badge,
  actions,
  className = ''
}) {
  return (
    <div className={`mb-6 sm:mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 ${className}`}>
      <div className="space-y-1">
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
            {title}
          </h1>
          {badge}
        </div>
        {subtitle && (
          <p className="text-sm sm:text-base text-slate-500 max-w-3xl">
            {subtitle}
          </p>
        )}
      </div>

      {actions && (
        <div className="flex items-center gap-2.5 flex-wrap flex-shrink-0">
          {actions}
        </div>
      )}
    </div>
  );
}
