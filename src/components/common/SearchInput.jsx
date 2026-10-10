import React from 'react';
import { Search, X } from 'lucide-react';

export default function SearchInput({
  value,
  onChange,
  placeholder = 'Search by tag, breed, or location...',
  className = '',
  onClear
}) {
  return (
    <div className={`relative flex items-center ${className}`}>
      <Search className="absolute left-3 w-4 h-4 text-slate-400 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full pl-9 pr-9 py-2 text-sm bg-white border border-slate-300 rounded-lg shadow-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-600 transition-colors"
      />
      {value && (
        <button
          type="button"
          onClick={onClear || (() => onChange({ target: { value: '' } }))}
          className="absolute right-3 p-0.5 rounded text-slate-400 hover:text-slate-600"
          title="Clear search"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
