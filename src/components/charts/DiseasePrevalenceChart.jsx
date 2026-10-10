import React, { useState } from 'react';
import { MOCK_ANALYTICS_DATA } from '../../data/mockData';

export default function DiseasePrevalenceChart() {
  const [selectedDisease, setSelectedDisease] = useState('all');
  const data = MOCK_ANALYTICS_DATA.monthlyPrevalence;
  const maxVal = 70; // scaling cap

  const diseaseKeys = [
    { key: 'lsd', label: 'Lumpy Skin Disease', color: '#f43f5e', bg: 'bg-rose-500' },
    { key: 'fmd', label: 'Foot & Mouth', color: '#f59e0b', bg: 'bg-amber-500' },
    { key: 'mastitis', label: 'Bovine Mastitis', color: '#0284c7', bg: 'bg-sky-500' },
    { key: 'respiratory', label: 'Respiratory (BRDC)', color: '#8b5cf6', bg: 'bg-purple-500' },
  ];

  return (
    <div className="w-full">
      {/* Selector pills */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setSelectedDisease('all')}
            className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors ${
              selectedDisease === 'all'
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Conditions
          </button>
          {diseaseKeys.map((d) => (
            <button
              key={d.key}
              onClick={() => setSelectedDisease(d.key)}
              className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-colors flex items-center gap-1.5 ${
                selectedDisease === d.key
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              <span className={`w-2 h-2 rounded-full ${d.bg}`} />
              {d.label}
            </button>
          ))}
        </div>

        <span className="text-[11px] text-slate-400 font-medium">
          Last 6 Months (May - Oct 2026)
        </span>
      </div>

      {/* Chart Canvas Graphic (Responsive SVG & Flex Bars) */}
      <div className="h-60 sm:h-64 flex items-end justify-between gap-2 sm:gap-4 pt-6 pb-2 px-2 border-b border-slate-200">
        {data.map((item) => {
          const totalCases = item.lsd + item.fmd + item.mastitis + item.respiratory;

          return (
            <div
              key={item.month}
              className="flex-1 flex flex-col items-center h-full justify-end group relative"
            >
              {/* Tooltip on hover */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-14 bg-slate-900 text-white text-[11px] py-1 px-2.5 rounded shadow-lg pointer-events-none z-20 whitespace-nowrap">
                <p className="font-bold">{item.month} Total: {totalCases} incidents</p>
                <p className="text-slate-300">
                  LSD: {item.lsd} | FMD: {item.fmd} | Mastitis: {item.mastitis}
                </p>
              </div>

              {/* Bar container */}
              <div className="w-full max-w-[42px] flex items-end justify-center h-48 gap-0.5">
                {selectedDisease === 'all' ? (
                  <div className="w-full flex flex-col-reverse rounded-t overflow-hidden bg-slate-100">
                    <div
                      style={{ height: `${(item.lsd / maxVal) * 100}%` }}
                      className="bg-rose-500 hover:opacity-90 transition-all"
                      title={`LSD: ${item.lsd}`}
                    />
                    <div
                      style={{ height: `${(item.fmd / maxVal) * 100}%` }}
                      className="bg-amber-500 hover:opacity-90 transition-all"
                      title={`FMD: ${item.fmd}`}
                    />
                    <div
                      style={{ height: `${(item.mastitis / maxVal) * 100}%` }}
                      className="bg-sky-500 hover:opacity-90 transition-all"
                      title={`Mastitis: ${item.mastitis}`}
                    />
                    <div
                      style={{ height: `${(item.respiratory / maxVal) * 100}%` }}
                      className="bg-purple-500 hover:opacity-90 transition-all"
                      title={`Respiratory: ${item.respiratory}`}
                    />
                  </div>
                ) : (
                  <div
                    style={{ height: `${(item[selectedDisease] / maxVal) * 100}%` }}
                    className={`w-full rounded-t transition-all duration-300 ${
                      diseaseKeys.find((d) => d.key === selectedDisease)?.bg
                    }`}
                  />
                )}
              </div>

              {/* X Axis Label */}
              <span className="mt-2 text-xs font-semibold text-slate-600 group-hover:text-slate-900">
                {item.month}
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-3 text-xs text-slate-500">
        {diseaseKeys.map((d) => (
          <div key={d.key} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded ${d.bg}`} />
            <span>{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
