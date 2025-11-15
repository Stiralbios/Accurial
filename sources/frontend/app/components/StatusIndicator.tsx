import React, { useState, useEffect } from 'react';
import { getHealthStatus } from '../services/api.tsx';

interface HealthStatus {
  status: 'ok' | 'error';
  message?: string;
}

function StatusIndicator() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    async function fetchStatus() {
      const status = await getHealthStatus();
      setHealthStatus(status);
    }

    fetchStatus();
  }, []);

  return (
    <div className="status-indicator">
      {healthStatus ? (
        <div>
          Health Status: <span className={`status-${healthStatus.status}`}>
            {healthStatus.status.toUpperCase()}
          </span>
          {healthStatus.message && <div>{healthStatus.message}</div>}
        </div>
      ) : (
        <div>Loading health status...</div>
      )}
    </div>
  );
}


export default StatusIndicator