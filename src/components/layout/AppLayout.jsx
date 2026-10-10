import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import EmergencyBanner from './EmergencyBanner';

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Topmost emergency and hackathon demo alert banner */}
      <EmergencyBanner />

      <div className="flex flex-1 min-h-0">
        {/* Navigation Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 lg:pl-72">
          {/* Header Topbar */}
          <Topbar onOpenSidebar={() => setSidebarOpen(true)} />

          {/* Page Outlet */}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Outlet />
          </main>

          {/* Footer note */}
          <footer className="border-t border-slate-200/80 bg-white/50 py-4 px-6 text-center text-xs text-slate-500">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
              <p>
                &copy; 2026 AniCare AI &bull; Smart India Hackathon Prototype Project
              </p>
              <p className="text-[11px] text-slate-400">
                Front-end Demonstration Interface &bull; Simulated Diagnostic & Telemetry Models
              </p>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
