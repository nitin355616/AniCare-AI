import React from 'react';
import { Loader2 } from 'lucide-react';

const variants = {
  primary: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm shadow-emerald-700/20 focus-visible:ring-emerald-500 border border-emerald-600',
  secondary: 'bg-slate-900 hover:bg-slate-800 text-white shadow-sm focus-visible:ring-slate-700 border border-slate-900',
  outline: 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-sm focus-visible:ring-slate-400',
  ghost: 'bg-transparent hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-transparent focus-visible:ring-slate-400',
  danger: 'bg-rose-600 hover:bg-rose-700 text-white shadow-sm shadow-rose-700/20 focus-visible:ring-rose-500 border border-rose-600',
  dangerOutline: 'bg-white hover:bg-rose-50 text-rose-600 border border-rose-200 hover:border-rose-300 focus-visible:ring-rose-500',
  success: 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm focus-visible:ring-emerald-500 border border-emerald-600',
};

const sizes = {
  sm: 'px-2.5 py-1.5 text-xs font-medium rounded-lg gap-1.5',
  md: 'px-3.5 py-2 text-sm font-medium rounded-lg gap-2',
  lg: 'px-4.5 py-2.5 text-base font-semibold rounded-xl gap-2.5',
};

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  icon: Icon,
  iconRight: IconRight,
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  const chosenVariant = variants[variant] || variants.primary;
  const chosenSize = sizes[size] || sizes.md;

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`inline-flex items-center justify-center transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none ${chosenVariant} ${chosenSize} ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
      ) : Icon ? (
        <Icon className="w-4 h-4 flex-shrink-0" />
      ) : null}
      
      <span>{children}</span>

      {!isLoading && IconRight && (
        <IconRight className="w-4 h-4 flex-shrink-0" />
      )}
    </button>
  );
}
