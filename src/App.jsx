import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import Dashboard from './pages/Dashboard';
import Animals from './pages/Animals';
import DiseaseDetection from './pages/DiseaseDetection';
import HealthReports from './pages/HealthReports';
import VeterinaryCare from './pages/VeterinaryCare';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import OutbreakIntelligence from './pages/OutbreakIntelligence';
import FarmerExperience from './pages/FarmerExperience';
import AIModelMonitoring from './pages/AIModelMonitoring';
import GeospatialIntelligence from './pages/GeospatialIntelligence';
import ResponseCommandCenter from './pages/ResponseCommandCenter';
import SIHDemo from './pages/SIHDemo';
import SIHExecutiveDashboard from './pages/SIHExecutiveDashboard';
import AIValidationDashboard from './pages/AIValidationDashboard';
import SIHMapping from './pages/SIHMapping';
import JuryQnA from './pages/JuryQnA';
import DatasetExplorer from './pages/DatasetExplorer';
import { TranslationProvider } from './i18n';

export default function App() {
  return (
    <TranslationProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="animals" element={<Animals />} />
            <Route path="disease-detection" element={<DiseaseDetection />} />
            <Route path="dataset-explorer" element={<DatasetExplorer />} />
            <Route path="reports" element={<HealthReports />} />
            <Route path="veterinary" element={<VeterinaryCare />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="outbreaks" element={<OutbreakIntelligence />} />
            <Route path="farmer" element={<FarmerExperience />} />
            <Route path="ai-monitoring" element={<AIModelMonitoring />} />
            <Route path="geospatial" element={<GeospatialIntelligence />} />
            <Route path="response" element={<ResponseCommandCenter />} />
            <Route path="sih-demo" element={<SIHDemo />} />
            <Route path="sih-dashboard" element={<SIHExecutiveDashboard />} />
            <Route path="ai-validation" element={<AIValidationDashboard />} />
            <Route path="sih-mapping" element={<SIHMapping />} />
            <Route path="jury-qa" element={<JuryQnA />} />
            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </TranslationProvider>
  );
}

