import React, { useEffect, useState } from 'react';
import { fetchHealth } from '../utils/api.ts';

type BackendStatus = 'checking' | 'online' | 'offline';

export const StatusBar: React.FC<{ onRejectedSops: (s: string[]) => void }> = ({ onRejectedSops }) => {
  const [status,  setStatus]  = useState<BackendStatus>('checking');
  const [model,   setModel]   = useState('');
  const [chunks,  setChunks]  = useState(0);

  useEffect(() => {
    let cancelled = false;

    const refreshHealth = () => {
      fetchHealth()
        .then(h => {
          if (cancelled) return;
          setStatus('online');
          setModel(h.model);
          setChunks(h.chunk_count);
        })
        .catch(() => {
          if (cancelled) return;
          setStatus('offline');
        });
    };

    refreshHealth();

    const intervalId = window.setInterval(refreshHealth, 5000);
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        refreshHealth();
      }
    };

    window.addEventListener('focus', refreshHealth);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      cancelled = true;
      window.clearInterval(intervalId);
      window.removeEventListener('focus', refreshHealth);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  return (
    <div className="status-bar">
      <div className="status-bar__left">
        <span className={`status-dot status-dot--${status}`} />
        <span className="status-label">
          {status === 'online'   ? model :
           status === 'offline'  ? 'Backend offline — start the FastAPI server' :
           'Connecting…'}
        </span>
        {status === 'online' && chunks > 0 && (
          <span className="status-chunks">{chunks} chunks indexed</span>
        )}
      </div>
    </div>
  );
};
