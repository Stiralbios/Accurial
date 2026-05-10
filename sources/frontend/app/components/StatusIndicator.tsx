import { useState, useEffect } from "react";

import { getHealthStatus } from "../services/api.tsx";

interface HealthStatus {
  status: "ok" | "error";
  message?: string;
}

export function StatusIndicator() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);

  useEffect(() => {
    async function fetchStatus() {
      const status = await getHealthStatus();
      setHealthStatus(status);
    }

    void fetchStatus();
  }, []);

  return (
    <div className="status-indicator">
      {healthStatus ? (
        <div>
          Health Status: <span className={`status-${healthStatus.status}`}>{healthStatus.status.toUpperCase()}</span>
          {healthStatus.message && <div>{healthStatus.message}</div>}
        </div>
      ) : (
        <div>Loading health status...</div>
      )}
    </div>
  );
}
