import React from 'react';

export default function Card({
  title,
  subtitle,
  icon: Icon,
  badge,
  actions,
  children,
  className = '',
  bodyClassName = 'p-5 sm:p-6',
  headerClassName = 'px-5 py-4 sm:px-6 border-b border-slate-100',
  footer,
  footerClassName = 'px-5 py-3 sm:px-6 bg-slate-50/70 border-t border-slate-100 rounded-b-xl',
  onClick,
  hoverable = false
}) {
  const hasHeader = title || subtitle || Icon || badge || actions;

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl border border-slate-200/80 shadow-sm transition-all duration-200 ${
        hoverable ? 'hover:shadow-md hover:border-slate-300 cursor-pointer' : ''
      } ${className}`}
    >
      {hasHeader && (
        <div className={`flex flex-wrap items-center justify-between gap-3 ${headerClassName}`}>
          <div className="flex items-center gap-3 min-w-0">
            {Icon && (
              <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-100/60 flex-shrink-0">
                <Icon className="w-5 h-5" />
              </div>
            )}
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                {title && (
                  <h3 className="text-base font-semibold text-slate-900 tracking-tight truncate">
                    {title}
                  </h3>
                )}
                {badge}
              </div>
              {subtitle && (
                <p className="text-xs sm:text-sm text-slate-500 mt-0.5 truncate">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}

      <div className={bodyClassName}>{children}</div>

      {footer && <div className={footerClassName}>{footer}</div>}
    </div>
  );
}
