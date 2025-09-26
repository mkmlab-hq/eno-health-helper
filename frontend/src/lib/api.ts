/**
 * MKM Lab eno-health-helper API 클라이언트
 * 백엔드 서비스와의 통신을 담당
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://us-central1-eno-health-helper.cloudfunctions.net/eno_health_api';

export interface AnalysisRequest {
  user_id: string;
  analysis_type: 'rppg' | 'voice' | 'fusion' | 'health';
  data: Record<string, unknown>;
}

export interface AnalysisResponse {
  success: boolean;
  data?: Record<string, unknown>;
  error?: string;
  timestamp: string;
  analysis_type: string;
}

export interface HealthData {
  user_id: string;
  timestamp: string;
  rppg_data?: Record<string, unknown>;
  voice_data?: Record<string, unknown>;
  emotion_data?: Record<string, unknown>;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  /**
   * 기본 HTTP 요청 메서드
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API 요청 실패 (${endpoint}):`, error);
      throw error;
    }
  }

  /**
   * 헬스 체크
   */
  async healthCheck(): Promise<{ status: string; services: Record<string, string> }> {
    return this.request('/health');
  }

  /**
   * 시스템 상태 확인
   */
  async getStatus(): Promise<{ status: string; services: Record<string, string> }> {
    return this.request('/api/status');
  }

  /**
   * rPPG 분석
   */
  async analyzeRPPG(userId: string, rppgData: Record<string, unknown>): Promise<AnalysisResponse> {
    const request: AnalysisRequest = {
      user_id: userId,
      analysis_type: 'rppg',
      data: { rppg_data: rppgData }
    };

    return this.request('/api/analyze/rppg', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 음성 분석
   */
  async analyzeVoice(userId: string, voiceData: Record<string, unknown>): Promise<AnalysisResponse> {
    const request: AnalysisRequest = {
      user_id: userId,
      analysis_type: 'voice',
      data: { voice_data: voiceData }
    };

    return this.request('/api/analyze/voice', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 융합 분석
   */
  async analyzeFusion(userId: string, rppgData: Record<string, unknown>, voiceData: Record<string, unknown>): Promise<AnalysisResponse> {
    const request: AnalysisRequest = {
      user_id: userId,
      analysis_type: 'fusion',
      data: { 
        rppg_data: rppgData,
        voice_data: voiceData
      }
    };

    return this.request('/api/analyze/fusion', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 종합 건강 분석
   */
  async analyzeHealth(userId: string, healthData: HealthData): Promise<AnalysisResponse> {
    const request: AnalysisRequest = {
      user_id: userId,
      analysis_type: 'health',
      data: healthData as unknown as Record<string, unknown>
    };

    return this.request('/api/analyze/health', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 연결 테스트
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('백엔드 연결 실패:', error);
      return false;
    }
  }
}

// 싱글톤 인스턴스
export const apiClient = new APIClient();

// 기본 export
export default apiClient;
