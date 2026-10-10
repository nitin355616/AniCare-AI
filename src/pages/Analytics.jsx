import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Download,
  Calendar,
  Layers,
  CheckCircle2,
  Activity,
  ShieldCheck,
  Zap,
  Clock,
  Compass,
  ArrowUpRight,
  PieChart,
  Users,
  Award,
  Globe,
  Building2,
  FileSpreadsheet
} from 'lucide-react';
import PageHeader from '../components/common/PageHeader';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import StatCard from '../components/common/StatCard';
import DiseasePrevalenceChart from '../components/charts/DiseasePrevalenceChart';
import OutbreakGeoMap from '../components/charts/OutbreakGeoMap';
import { MOCK_ANALYTICS_DATA, MOCK_SUMMARY_METRICS } from '../data/mockData';

export default function Analytics() {
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const risk = MOCK_ANALYTICS_DATA.riskDistributionSummary;

  return (
    <div className="space-y-6 sm:space-y-8 animate-in fade-in duration-200">
      {/* Toast Alert */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white text-sm px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 border border-slate-700 animate-in slide-in-from-bottom-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Page Header */}
      <PageHeader
        title="Epidemiological Intelligence & National Analytics"
        subtitle="Government & administrative dashboard: disease trajectory modeling, species-wise distributions, treatment outcomes, and AI detection benchmarks."
        badge={
          <Badge variant="indigo">
            DAHD Government Analytics Engine
          </Badge>
        }
        actions={
          <Button
            variant="outline"
            size="sm"
            icon={Download}
            onClick={() => showToast('Simulating National Epizootic Dataset export (CSV/JSON)...')}
          >
            Export Comprehensive Dataset
          </Button>
        }
      />

      {/* Top Benchmark KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Avg. Early Warning Lead Time"
          value="3.5 Days"
          change="+48 hrs"
          changeType="up"
          changeLabel="vs manual triage"
          icon={Zap}
          theme="emerald"
          caption="Pre-symptomatic detection"
        />
        <StatCard
          title="AI Benchmark Accuracy"
          value={`${MOCK_ANALYTICS_DATA.aiDetectionStats.averageConfidence}%`}
          change="3.2% FPR"
          changeType="neutral"
          changeLabel="false positive rate"
          icon={Award}
          theme="indigo"
          caption="BioBERT + Vision Net"
        />
        <StatCard
          title="Clinical Recovery Rate"
          value="84.5%"
          change="+6.2%"
          changeType="up"
          changeLabel="ring efficacy"
          icon={ShieldCheck}
          theme="sky"
          caption="Early intervention impact"
        />
        <StatCard
          title="Scans Processed"
          value={MOCK_ANALYTICS_DATA.aiDetectionStats.totalScansConducted.toLocaleString()}
          change="+312 alerts"
          changeType="up"
          changeLabel="this quarter"
          icon={Activity}
          theme="amber"
          caption="Edge IoT + manual scans"
        />
      </div>

      {/* Model External Validation Status Indicator (Milestone 8A) */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-5 text-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center flex-shrink-0 text-indigo-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h4 className="text-sm font-bold text-white tracking-tight">
                Model External Validation
              </h4>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                PERMISSION_PENDING
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                Model: EfficientNet-B0 (τ = 0.50 Frozen)
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Dataset B Independent Benchmark: AAU Anand / ICAR-DFMD institutional DTA in review. Zero production images ingested. External validation metrics pending legal acquisition.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 self-stretch md:self-auto justify-end border-t border-slate-800/80 md:border-t-0 pt-3 md:pt-0">
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono uppercase tracking-wider">Independent Samples</span>
            <span className="text-xs font-bold text-slate-200 font-mono">N = 0 (Quarantined)</span>
          </div>
          <div className="h-7 w-px bg-slate-800 hidden sm:block" />
          <div className="text-right">
            <span className="text-[10px] text-slate-400 block font-mono uppercase tracking-wider">Dataset A Test Benchmark</span>
            <span className="text-xs font-bold text-emerald-400 font-mono">80.95% Recall / 97.92% Spec</span>
          </div>
        </div>
      </div>

      {/* 1. Disease Trends & Cases Over Time (Chart) */}
      <Card
        title="Disease Incidence Over Time (Cases Over Time)"
        subtitle="6-Month historical syndromic prevalence across all monitored dairy sheds"
        icon={TrendingUp}
      >
        <DiseasePrevalenceChart />
      </Card>

      {/* 2. Species-Wise Health Statistics & 3. Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Species-Wise Health Statistics (7 cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Species-Wise Livestock Health Statistics"
            subtitle="Categorical breakdown across major domesticated ruminant species"
            icon={Users}
            bodyClassName="p-0"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3">Species</th>
                    <th className="px-4 py-3">Population</th>
                    <th className="px-4 py-3">Healthy</th>
                    <th className="px-4 py-3">At Risk</th>
                    <th className="px-4 py-3">Critical</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {MOCK_ANALYTICS_DATA.speciesDistribution.map((sp) => (
                    <tr key={sp.species} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3.5 font-bold text-slate-900">
                        {sp.species}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="font-semibold text-slate-800">{sp.count}</span>
                        <span className="text-[10px] text-slate-400 block">({sp.percentage}%)</span>
                      </td>
                      <td className="px-4 py-3.5 text-emerald-700 font-bold">
                        {sp.healthy}
                      </td>
                      <td className="px-4 py-3.5 text-amber-700 font-bold">
                        {sp.atRisk}
                      </td>
                      <td className="px-4 py-3.5 text-rose-700 font-bold">
                        {sp.critical}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        {/* Risk Distribution Breakdown (5 cols) */}
        <div className="lg:col-span-5">
          <Card
            title="Herd Risk Distribution"
            subtitle="Current biosecurity stratification of the national herd"
            icon={PieChart}
          >
            <div className="space-y-4 text-xs">
              {/* Stacked visually clean progress bar */}
              <div className="h-4 rounded-full overflow-hidden flex w-full bg-slate-100">
                <div style={{ width: `${risk.healthyPercentage}%` }} className="bg-emerald-500" title="Healthy" />
                <div style={{ width: `${risk.atRiskPercentage}%` }} className="bg-amber-500" title="At Risk" />
                <div style={{ width: `${risk.criticalPercentage}%` }} className="bg-rose-500" title="Critical" />
              </div>

              {/* Legend & Stats */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-emerald-50/70 border border-emerald-100">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="font-bold text-slate-800">Healthy & Productive</span>
                  </div>
                  <span className="font-mono font-bold text-emerald-800">{risk.healthy} ({risk.healthyPercentage}%)</span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-lg bg-amber-50/70 border border-amber-100">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-amber-500" />
                    <span className="font-bold text-slate-800">At Risk / Subclinical</span>
                  </div>
                  <span className="font-mono font-bold text-amber-800">{risk.atRisk} ({risk.atRiskPercentage}%)</span>
                </div>

                <div className="flex items-center justify-between p-2.5 rounded-lg bg-rose-50/70 border border-rose-100">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-rose-500" />
                    <span className="font-bold text-slate-800">Critical / Quarantined</span>
                  </div>
                  <span className="font-mono font-bold text-rose-800">{risk.critical} ({risk.criticalPercentage}%)</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* 4. Treatment Outcomes & 5. Geographic / Outbreak Visualization Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Treatment Outcomes (5 cols) */}
        <div className="lg:col-span-5">
          <Card
            title="Clinical Treatment Outcomes"
            subtitle="Efficacy evaluation of early veterinary interventions"
            icon={ShieldCheck}
          >
            <div className="space-y-3 text-xs">
              {MOCK_ANALYTICS_DATA.treatmentOutcomes.map((outcome) => (
                <div key={outcome.category} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-800">{outcome.category}</span>
                    <span className="font-mono font-bold text-slate-900">{outcome.percentage}%</span>
                  </div>
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-emerald-600 h-full rounded-full"
                      style={{ width: `${outcome.percentage}%` }}
                    />
                  </div>
                  <span className="text-[10px] text-slate-400 block mt-1">
                    {outcome.count} confirmed cases
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Outbreak Visualization Placeholder (7 cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Geographic Outbreak Visualization & Bio-Containment"
            subtitle="Multi-district spatial risk radar and 10km ring quarantine tracking"
            icon={Globe}
          >
            <OutbreakGeoMap />
          </Card>
        </div>
      </div>

      {/* Government / Administrative Future Vision Card */}
      <div className="p-6 bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 rounded-2xl text-white border border-slate-800 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono text-[11px] font-bold uppercase border border-emerald-500/30">
              Government / Admin Scalability
            </span>
          </div>
          <h3 className="text-lg font-bold text-white">
            Ready for Integration with the National Animal Disease Reporting System (NADRS)
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            AniCare AI's analytics schema is built according to OIE terrestrial animal health standards and ICAR surveillance protocols, facilitating direct REST/GraphQL feeds to State Animal Husbandry Directorates.
          </p>
        </div>

        <Button
          variant="success"
          size="sm"
          icon={FileSpreadsheet}
          onClick={() => showToast('Simulating National Administrative Export...')}
        >
          Download Admin Briefing
        </Button>
      </div>
    </div>
  );
}
