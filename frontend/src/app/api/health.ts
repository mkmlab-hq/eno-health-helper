// 백엔드 API 호출 함수들

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface HealthStatus {
  status: string;
  service: string;
  timestamp: string;
}

export interface MeasurementResult {
  success: boolean;
  message: string;
  data: {
    rppg: any;
    voice: any;
    analysis_method: string;
    timestamp: string;
    quality_score: number;
  };
  timestamp: string;
}

export interface MeasurementHistory {
  measurements: any[];
  total: number;
  limit: number;
  offset: number;
}

// 헬스체크 API
export async function checkHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
}

// 측정 기록 조회 API
export async function getMeasurementHistory(
  limit: number = 10,
  offset: number = 0
): Promise<MeasurementHistory> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/measure/history?limit=${limit}&offset=${offset}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch measurement history:', error);
    throw error;
  }
}

// 측정 상태 확인 API
export async function getMeasurementStatus(
  measurementId: string
): Promise<any> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/measure/status/${measurementId}`
    );
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch measurement status:', error);
    throw error;
  }
} 