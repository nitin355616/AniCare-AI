import React from 'react';
import { HelpCircle } from 'lucide-react';
import Button from './Button';

export default function EmptyState({
  title = 'No records found',
  description = 'There is currently no data matching your query or filter criteria.',
  icon: Icon = HelpCircle,
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 sm:p-12 bg-white rounded-xl border border-dashed border-slate-300 ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 mb-4">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-slate-900 tracking-tight">
        {title}
      </h3>
      <p className="text-sm text-slate-500 max-w-md mt-1.5 mb-5">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="outline" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
