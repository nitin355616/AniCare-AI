import React, { useState, useEffect } from 'react';
import {
  Activity,
  Cpu,
  Layers,
  FlaskConical,
  Database,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Lock,
  RotateCcw,
  Stethoscope
} from 'lucide-react';
import { aiMonitoringService } from '../services/api/aiMonitoringService';
import ModelHealthCard from '../components/ai/ModelHealthCard';
import DriftStatusCard from '../components/ai/DriftStatusCard';
import FeedbackMetrics from '../components/ai/FeedbackMetrics';
import ModelRegistryTable from '../components/ai/ModelRegistryTable';
import ExperimentComparison from '../components/ai/ExperimentComparison';
import DataQualityCard from '../components/ai/DataQualityCard';
import PredictionMetrics from '../components/ai/PredictionMetrics';

export default function AIModelMonitoring() {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'drift' | 'registry' | 'experiments' | 'data'
  const [isSimulating, setIsSimulating] = useState(false);

  // State slices
  const [summary, setSummary] = useState(null);
  const [driftReport, setDriftReport] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [models, setModels] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [dataQuality, setDataQuality] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [sumRes, driftRes, predRes, fbRes, modelsRes, expRes, dqRes] = await Promise.all([
        aiMonitoringService.getSummary(),
        aiMonitoringService.getDriftReport(),
        aiMonitoringService.getPredictions({ limit: 10 }),
        aiMonitoringService.getFeedback({ limit: 10 }),
        aiMonitoringService.getModels(),
        aiMonitoringService.getExperiments(),
        aiMonitoringService.getDataQuality()
      ]);

      setSummary(sumRes);
      setDriftReport(driftRes);
      setPredictions(predRes?.items || []);
      setFeedbackList(fbRes?.items || []);
      setModels(modelsRes?.models || []);
      setExperiments(expRes?.items || []);
      setDataQuality(dqRes);
    } catch (err) {
      console.error('Error fetching AI monitoring telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSimulateDrift = async () => {
    setIsSimulating(true);
    try {
      const res = await aiMonitoringService.simulateDriftDemo();
      alert(`Drift simulation successful: PSI elevated to ${Number(res.psi_confidence).toFixed(4)} (${res.overall_status}).`);
      await fetchDashboardData();
    } catch (err) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleSubmitFeedback = async (formData) => {
    await aiMonitoringService.submitFeedback(formData);
    alert('Clinical feedback successfully logged to data curation pipeline!');
    await fetchDashboardData();
  };

  const handleRollback = async (reason) => {
    const res = await aiMonitoringService.rollback({ reason });
    alert(`Rollback successful: Reverted to model ${res.active_production_model}.`);
    await fetchDashboardData();
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl border border-indigo-100">
              <Activity className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold text-slate-900">AI Model Monitoring & Continuous Learning</h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  SIH Milestone 11 Active
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Closed-loop clinical monitoring, multi-signal drift detection, cryptographic registry, and continuous learning governance.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 pb-1">
        {[
          { id: 'overview', label: 'Overview & Health', icon: Cpu },
          { id: 'drift', label: 'Drift & Inference Stream', icon: Activity },
          { id: 'registry', label: 'Model Registry & Gates', icon: Layers },
          { id: 'experiments', label: 'Benchmark Experiments', icon: FlaskConical },
          { id: 'data', label: 'Data Provenance & Curation', icon: Database }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <ModelHealthCard
            productionModel={summary?.production_model}
            isHealthy={summary?.is_healthy}
          />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DriftStatusCard
              driftData={driftReport || summary?.drift}
              onSimulateDrift={handleSimulateDrift}
              onRefresh={fetchDashboardData}
              isSimulating={isSimulating}
            />

            <FeedbackMetrics
              feedbackSummary={summary?.feedback_summary}
              feedbackList={feedbackList}
              onSubmitFeedback={handleSubmitFeedback}
            />
          </div>

          <DataQualityCard dataQuality={dataQuality || summary?.curation_pipeline} />
        </div>
      )}

      {activeTab === 'drift' && (
        <div className="space-y-6">
          <DriftStatusCard
            driftData={driftReport || summary?.drift}
            onSimulateDrift={handleSimulateDrift}
            onRefresh={fetchDashboardData}
            isSimulating={isSimulating}
          />

          <PredictionMetrics
            predictions={predictions}
            total={predictions.length}
            onRefresh={fetchDashboardData}
          />
        </div>
      )}

      {activeTab === 'registry' && (
        <div className="space-y-6">
          <ModelRegistryTable
            models={models}
            productionModelId={summary?.production_model?.model_id}
            onRollback={handleRollback}
          />
        </div>
      )}

      {activeTab === 'experiments' && (
        <div className="space-y-6">
          <ExperimentComparison experiments={experiments} />
        </div>
      )}

      {activeTab === 'data' && (
        <div className="space-y-6">
          <DataQualityCard dataQuality={dataQuality || summary?.curation_pipeline} />
          <FeedbackMetrics
            feedbackSummary={summary?.feedback_summary}
            feedbackList={feedbackList}
            onSubmitFeedback={handleSubmitFeedback}
          />
        </div>
      )}
    </div>
  );
}
