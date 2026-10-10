import React, { useState } from 'react';
import { AlertCircle, Search, Filter, ShieldCheck, ChevronRight, Stethoscope, Eye } from 'lucide-react';
import Badge from '../common/Badge';

export default function HotspotPriorityTable({
  hotspots = [],
  onSelectHotspot,
  selectedHotspotId = null
}) {
  const [search, setSearch] = useState('');
  const [tierFilter, setTierFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const filtered = hotspots.filter((h) => {
    const matchSearch =
      (h.village && h.village.toLowerCase().includes(search.toLowerCase())) ||
      (h.block && h.block.toLowerCase().includes(search.toLowerCase())) ||
      (h.district && h.district.toLowerCase().includes(search.toLowerCase()));
    const matchTier = tierFilter === 'ALL' || h.risk_tier === tierFilter;
    const matchPriority = priorityFilter === 'ALL' || h.priority === priorityFilter;
    return matchSearch && matchTier && matchPriority;
  });

  const getPriorityBadge = (p) => {
    switch (p) {
      case 'P1':
        return 'bg-rose-100 text-rose-800 border-rose-300 font-extrabold';
      case 'P2':
        return 'bg-amber-100 text-amber-800 border-amber-300 font-bold';
      case 'P3':
        return 'bg-blue-100 text-blue-800 border-blue-300 font-semibold';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300 font-medium';
    }
  };

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'CRITICAL':
        return 'bg-rose-50 text-rose-700 border border-rose-200';
      case 'HIGH':
        return 'bg-amber-50 text-amber-700 border border-amber-200';
      case 'MODERATE':
        return 'bg-blue-50 text-blue-700 border border-blue-200';
      default:
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-5">
        <div>
          <h3 className="text-base font-bold text-slate-900">Ranked Epidemiological Hotspot Registry</h3>
          <p className="text-xs text-slate-500">
            Multi-signal prioritization (P1 Critical $\to$ P4 Monitor) based on case volume, growth velocity, and herd density.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter Village or District..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs border rounded-lg focus:ring-1 focus:ring-indigo-500 outline-none w-48"
            />
          </div>

          <select
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs border rounded-lg bg-white text-slate-700 outline-none"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="CRITICAL">Critical Tier</option>
            <option value="HIGH">High Tier</option>
            <option value="MODERATE">Moderate Tier</option>
            <option value="LOW">Low Tier</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs border rounded-lg bg-white text-slate-700 outline-none"
          >
            <option value="ALL">All Priorities</option>
            <option value="P1">P1 Critical</option>
            <option value="P2">P2 High</option>
            <option value="P3">P3 Moderate</option>
            <option value="P4">P4 Monitor</option>
          </select>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-2.5 px-3">Priority</th>
              <th className="py-2.5 px-3">Location</th>
              <th className="py-2.5 px-3">Syndromic Signal</th>
              <th className="py-2.5 px-3">Risk Score</th>
              <th className="py-2.5 px-3">Cases</th>
              <th className="py-2.5 px-3">7d Growth</th>
              <th className="py-2.5 px-3">Herds</th>
              <th className="py-2.5 px-3">Status</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.length > 0 ? (
              filtered.map((item, idx) => {
                const isSelected = selectedHotspotId === item.hotspot_id;

                return (
                  <tr
                    key={item.hotspot_id || idx}
                    onClick={() => onSelectHotspot && onSelectHotspot(item.hotspot_id)}
                    className={`hover:bg-slate-50/70 cursor-pointer transition ${isSelected ? 'bg-indigo-50/40' : ''}`}
                  >
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded border text-[11px] font-mono ${getPriorityBadge(item.priority)}`}>
                        {item.priority}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-900">{item.village}</div>
                      <span className="text-[11px] text-slate-400">
                        {item.block}, {item.district}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-medium text-slate-800">
                      {item.condition_signal}
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex items-center space-x-1.5">
                        <span className="font-bold text-slate-900">{item.risk_score}</span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${getTierBadge(item.risk_tier)}`}>
                          {item.risk_tier}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-3 font-semibold text-slate-900">{item.cases}</td>
                    <td className="py-3 px-3 font-semibold text-indigo-700">{item.growth_label}</td>
                    <td className="py-3 px-3 text-slate-600">{item.affected_herds} herds</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.hotspot_status === 'ESCALATING' ? 'bg-rose-100 text-rose-800' :
                        item.hotspot_status === 'EMERGING' ? 'bg-amber-100 text-amber-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {item.hotspot_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectHotspot) onSelectHotspot(item.hotspot_id);
                        }}
                        className="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded text-xs font-semibold transition"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="9" className="py-6 text-center text-slate-400">
                  No hotspots match the current criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
