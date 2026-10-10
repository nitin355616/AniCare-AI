import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from '../../i18n';
import { connectivityManager } from '../../services/offline/connectivityManager';
import { syncQueue } from '../../services/offline/syncQueue';
import { syncEngine } from '../../services/offline/syncEngine';
import { X, RefreshCw, CheckCircle2, AlertTriangle, AlertCircle, Clock, Wifi, WifiOff, Trash2 } from 'lucide-react';

export default function SyncStatusModal({ isOpen, onClose }) {
  const { t, lang } = useTranslation();
  const [connInfo, setConnInfo] = useState(connectivityManager.getStatusInfo());
  const [actions, setActions] = useState([]);
  const [lastSyncTime, setLastSyncTime] = useState(null);
  const [isSyncing, setIsSyncing] = useState(syncEngine.isSyncing);
  const [syncMessage, setSyncMessage] = useState('');

  const refreshData = useCallback(async () => {
    try {
      const all = await syncQueue.getAllActions();
      setActions(all);
      const last = await syncEngine.getLastSyncTime();
      setLastSyncTime(last);
      setConnInfo(connectivityManager.getStatusInfo());
    } catch (err) {
      console.warn('Failed to refresh sync data:', err);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      refreshData();
    }
  }, [isOpen, refreshData]);

  if (!isOpen) return null;

  const handleManualSync = async () => {
    setIsSyncing(true);
    setSyncMessage('');
    try {
      const res = await syncEngine.sync();
      if (res.success) {
        setSyncMessage(lang === 'hi' ? 'सिंक सफलतापूर्वक संपन्न हुआ!' : 'Synchronization completed successfully!');
      } else {
        setSyncMessage(res.reason || 'Sync skipped');
      }
      refreshData();
    } catch (err) {
      setSyncMessage(err.message || 'Sync error');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleRetryAction = async (localActionId) => {
    await syncQueue.updateActionStatus(localActionId, 'PENDING', null);
    refreshData();
    handleManualSync();
  };

  const handleRemoveAction = async (localActionId) => {
    await syncQueue.removeAction(localActionId);
    refreshData();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-3xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6 space-y-5 shadow-2xl relative text-slate-100">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-700 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-xl">
              <RefreshCw className={`w-5 h-5 ${isSyncing ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{t('syncPanelTitle')}</h3>
              <p className="text-xs text-slate-400">
                {connInfo.isOnline ? (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <Wifi className="w-3 h-3" /> {t('serverReachable')} ({connInfo.latencyMs}ms)
                  </span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1">
                    <WifiOff className="w-3 h-3" /> {t('offlineBannerTitle')}
                  </span>
                )}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sync KPI Overview */}
        <div className="grid grid-cols-3 gap-2">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-center">
            <span className="text-xs text-slate-400">{t('pendingActions')}</span>
            <p className="text-xl font-bold text-amber-400 mt-1">
              {actions.filter((a) => a.status === 'PENDING').length}
            </p>
          </div>
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-center">
            <span className="text-xs text-slate-400">{t('failedActions')}</span>
            <p className="text-xl font-bold text-red-400 mt-1">
              {actions.filter((a) => a.status === 'FAILED').length}
            </p>
          </div>
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-700 text-center">
            <span className="text-xs text-slate-400">{t('conflicts')}</span>
            <p className="text-xl font-bold text-purple-400 mt-1">
              {actions.filter((a) => a.status === 'CONFLICT').length}
            </p>
          </div>
        </div>

        {/* Last Sync Timestamp */}
        <div className="text-xs text-slate-400 flex items-center justify-between bg-slate-900/40 p-3 rounded-xl border border-slate-700/60">
          <span>{t('lastSynced')}:</span>
          <span className="font-mono text-slate-200">
            {lastSyncTime ? new Date(lastSyncTime).toLocaleTimeString() : 'Not synced yet'}
          </span>
        </div>

        {syncMessage && (
          <div className="p-3 bg-blue-500/20 border border-blue-500/40 rounded-xl text-xs text-blue-300 font-semibold">
            ℹ️ {syncMessage}
          </div>
        )}

        {/* Action Queue List */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              {lang === 'hi' ? 'ऑफलाइन कार्य सूची' : 'Queue Items'} ({actions.length})
            </h4>
            {actions.length > 0 && (
              <button
                onClick={async () => {
                  await syncQueue.clearQueue();
                  refreshData();
                }}
                className="text-xs text-slate-400 hover:text-red-400 flex items-center gap-1"
              >
                <Trash2 className="w-3 h-3" /> {t('clearSync')}
              </button>
            )}
          </div>

          {actions.length === 0 ? (
            <div className="p-4 bg-slate-900/30 rounded-xl text-center text-xs text-slate-500">
              {lang === 'hi' ? 'कोई लंबित ऑफलाइन कार्य नहीं है।' : 'No offline actions in queue.'}
            </div>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {actions.map((act) => {
                const isFailed = act.status === 'FAILED';
                const isConflict = act.status === 'CONFLICT';
                const isPending = act.status === 'PENDING';

                return (
                  <div
                    key={act.local_action_id}
                    className="bg-slate-900/80 border border-slate-700/80 p-2.5 rounded-xl text-xs flex items-center justify-between gap-2"
                  >
                    <div className="overflow-hidden">
                      <div className="flex items-center gap-1.5 font-bold text-white truncate">
                        <span>{act.action_type}</span>
                        <span className="text-slate-500 font-normal text-[10px]">({act.entity_id || 'new'})</span>
                      </div>
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">
                        {act.last_error || act.payload?.observations || 'Pending upload...'}
                      </p>
                    </div>

                    <div className="flex items-center gap-1 flex-shrink-0">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                          isFailed
                            ? 'bg-red-500/20 text-red-400'
                            : isConflict
                            ? 'bg-purple-500/20 text-purple-400'
                            : isPending
                            ? 'bg-amber-500/20 text-amber-400'
                            : 'bg-emerald-500/20 text-emerald-400'
                        }`}
                      >
                        {act.status}
                      </span>

                      {isFailed && (
                        <button
                          onClick={() => handleRetryAction(act.local_action_id)}
                          className="p-1 hover:bg-slate-700 text-blue-400 rounded"
                          title="Retry"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                      )}

                      <button
                        onClick={() => handleRemoveAction(act.local_action_id)}
                        className="p-1 hover:bg-slate-700 text-slate-400 hover:text-red-400 rounded"
                        title="Remove"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-2 pt-2">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-xl text-xs font-bold"
          >
            {t('close')}
          </button>
          <button
            onClick={handleManualSync}
            disabled={isSyncing || !connInfo.isOnline}
            className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-md"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{t('syncNow')}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
