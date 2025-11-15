interface HealthResponse {
  status: 'ok' | 'error';
  message?: string;
}

export const getHealthStatus = async (): Promise<HealthResponse> => {
  try {
    const response = await fetch('http://localhost:8800/api/debug/healthcheck/status');
    return await response.json() as HealthResponse;
  } catch (error) {
    console.error('Healthcheck failed:', error);
    return { status: 'error', message: 'Connection failed' };
  }
};