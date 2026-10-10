import React, { useState, useEffect } from 'react';
import { useTranslation } from '../../i18n';
import { connectivityManager } from '../../services/offline/connectivityManager';
import { syncQueue } from '../../services/offline/syncQueue';
import { syncEngine } from '../../services/offline/syncEngine';
import { CONNECTIVITY_STATES } from '../../services/offline/syncTypes';
import { CheckCircle2, Clock, RefreshCw, AlertCircle, Wifi, WifiOff } from 'lucide-react';

export default function SyncStatusBadge({ onOpenPanel }) {
  const { t } = useTranslation();
  const [connInfo, setConnInfo] = useState(connectivityManager.getStatusInfo());
  const [queueStats, setQueueStats] = useState({ pending: 0, failed: 0, conflicts: 0 });
  const [isSyncing, setIsSyncing] = useState(syncEngine.isSyncing);

  useEffect(() => {
    const unsubConn = connectivityManager.subscribe((info) => {
      setConnInfo(info);
    });

    const unsubSync = syncEngine.subscribe((event) => {
      setIsSyncing(syncEngine.isSyncing);
      refreshStats();
    });

    const refreshStats = async () => {
      try {
        const stats = await syncQueue.getQueueStats();
        setQueueStats(stats);
      } catch (err) {
        console.warn('Queue stats read error:', err);
      }
    };

    refreshStats();
    const interval = setInterval(refreshStats, 3000);

    return () => {
      unsubConn();
      unsubSync();
      clearInterval(interval);
    };
  }, []);

  // Determine appearance
  let badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let Icon = CheckCircle2;
  let text = t('syncSynced');

  if (isSyncing || connInfo.state === CONNECTIVITY_STATES.SYNCING) {
    badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
    Icon = RefreshCw;
    text = t('syncSyncing');
  } else if (queueStats.failed > 0 || queueStats.conflicts > 0 || connInfo.state === CONNECTIVITY_STATES.SYNC_ERROR) {
    badgeColor = 'bg-red-500/10 text-red-400 border-red-500/30';
    Icon = AlertCircle;
    text = `${t('syncIssue')} (${queueStats.failed + queueStats.conflicts})`;
  } else if (!connInfo.isOnline) {
    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = WifiOff;
    text = queueStats.pending > 0 ? `${t('syncWaiting')} (${queueStats.pending})` : 'Offline';
  } else if (queueStats.pending > 0) {
    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = Clock;
    text = `${t('syncWaiting')} (${queueStats.pending})`;
  }

  return (
    <button
      onClick={onOpenPanel}
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-semibold transition active:scale-95 shadow-sm hover:opacity-90 ${badgeColor}`}
      title={t('syncPanelTitle')}
    >
      <Icon className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
      <span>{text}</span>
    </button>
  );
}
