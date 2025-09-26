import { realValueAPI } from './realValueAPI';

export interface RPPGResult {
  heartRate: number;
  heartRateVariability: number;
  stressIndex: number; // stressLevel을 stressIndex로 변경
  confidence: number;
  quality: string; // 품질 정보 추가
  frameCount: number; // 프레임 수 추가
  timestamp: Date;
  // 실제값 API 응답 필드 추가
  dominantFrequency?: number;
  signalToNoiseRatio?: number;
  isRealValue?: boolean;
}

export class RPPGAnalyzer {
  private videoElement: HTMLVideoElement;
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private isAnalyzing: boolean = false;
  private frameCount: number = 0;
  private redValues: number[] = [];
  private greenValues: number[] = [];
  private blueValues: number[] = [];
  private analysisInterval: number | null = null;
  private realValueAvailable: boolean = false;

  constructor(videoElement: HTMLVideoElement) {
    this.videoElement = videoElement;
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d')!;
    this.canvas.width = 640;
    this.canvas.height = 480;
    
    // 실제값 API 사용 가능 여부 확인
    this.checkRealValueAvailability();
  }

  /**
   * 실제값 API 사용 가능 여부 확인
   */
  private async checkRealValueAvailability(): Promise<void> {
    try {
      this.realValueAvailable = await realValueAPI.isRealValueAvailable();
      console.log(`실제값 API 사용 가능: ${this.realValueAvailable}`);
    } catch (error) {
      console.error('실제값 API 확인 실패:', error);
      this.realValueAvailable = false;
    }
  }

  // rPPG 분석 시작
  startAnalysis(): void {
    if (this.isAnalyzing) return;
    
    this.isAnalyzing = true;
    this.frameCount = 0;
    this.redValues = [];
    this.greenValues = [];
    this.blueValues = [];
    
    this.analysisInterval = window.setInterval(() => {
      this.analyzeFrame();
    }, 100); // 10 FPS
  }

  // rPPG 분석 중지
  stopAnalysis(): void {
    if (this.analysisInterval) {
      clearInterval(this.analysisInterval);
      this.analysisInterval = null;
    }
    this.isAnalyzing = false;
  }

  // 프레임 분석
  private analyzeFrame(): void {
    if (!this.videoElement.videoWidth || !this.videoElement.videoHeight) return;
    
    // 비디오 프레임을 캔버스에 그리기
    this.ctx.drawImage(this.videoElement, 0, 0, this.canvas.width, this.canvas.height);
    
    // 얼굴 영역에서 RGB 값 추출 (중앙 영역)
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const sampleSize = 50;
    
    const imageData = this.ctx.getImageData(
      centerX - sampleSize / 2,
      centerY - sampleSize / 2,
      sampleSize,
      sampleSize
    );
    
    let totalRed = 0, totalGreen = 0, totalBlue = 0;
    let pixelCount = 0;
    
    for (let i = 0; i < imageData.data.length; i += 4) {
      totalRed += imageData.data[i];
      totalGreen += imageData.data[i + 1];
      totalBlue += imageData.data[i + 2];
      pixelCount++;
    }
    
    const avgRed = totalRed / pixelCount;
    const avgGreen = totalGreen / pixelCount;
    const avgBlue = totalBlue / pixelCount;
    
    this.redValues.push(avgRed);
    this.greenValues.push(avgGreen);
    this.blueValues.push(avgBlue);
    
    this.frameCount++;
    
    // 300 프레임 (30초) 수집 후 분석
    if (this.frameCount >= 300) {
      this.stopAnalysis();
      this.processResults();
    }
  }

  // 결과 처리
  private async processResults(): Promise<void> {
    if (this.frameCount < 300) return;
    
    try {
      if (this.realValueAvailable) {
        // 실제값 API 사용
        const result = await this.getRealValueAnalysis();
        if (this.onResultCallback) {
          this.onResultCallback(result);
        }
      } else {
        // 실제값 API 사용 불가
        console.error('실제값 API를 사용할 수 없습니다. 건강 분석을 위해 서버 연결을 확인해주세요.');
        if (this.onResultCallback) {
          this.onResultCallback(this.getDefaultResult());
        }
      }
    } catch (error) {
      console.error('RPPG 분석 실패:', error);
      if (this.onResultCallback) {
        this.onResultCallback(this.getDefaultResult());
      }
    }
  }

  // 실제값 API 분석
  private async getRealValueAnalysis(): Promise<RPPGResult> {
    const request = {
      greenChannel: this.greenValues,
      redChannel: this.redValues,
      blueChannel: this.blueValues,
      frameRate: 30,
      duration: this.frameCount / 30
    };
    
    try {
      const response = await realValueAPI.analyzeRealRPPG(request);
      
      return {
        heartRate: response.heart_rate,
        heartRateVariability: response.heart_rate_variability,
        stressIndex: this.mapStressLevel(response.stress_index.toString()),
        confidence: response.confidence,
        quality: response.quality,
        frameCount: this.frameCount,
        timestamp: new Date(),
        isRealValue: true,
        dominantFrequency: response.dominant_frequency,
        signalToNoiseRatio: response.signal_to_noise_ratio
      };
    } catch (error) {
      console.error('실제값 API 호출 실패:', error);
      throw error;
    }
  }

  // 스트레스 레벨 매핑
  private mapStressLevel(stressLevel: string): number {
    switch (stressLevel.toLowerCase()) {
      case 'low': return 0.2;
      case 'medium': return 0.5;
      case 'high': return 0.8;
      default: return 0.5;
    }
  }

  // 기본 결과 (에러 시)
  private getDefaultResult(): RPPGResult {
    return {
      heartRate: 0,
      heartRateVariability: 0,
      stressIndex: 0,
      confidence: 0,
      quality: 'Poor',
      frameCount: this.frameCount,
      timestamp: new Date(),
      isRealValue: false
    };
  }

  // 결과 콜백
  private onResultCallback: ((result: RPPGResult) => void) | null = null;
  
  onResult(callback: (result: RPPGResult) => void): void {
    this.onResultCallback = callback;
  }

  // 실시간 데이터 가져오기
  getCurrentData() {
    return {
      frameCount: this.frameCount,
      redValues: this.redValues,
      greenValues: this.greenValues,
      blueValues: this.blueValues,
      isAnalyzing: this.isAnalyzing,
      realValueAvailable: this.realValueAvailable
    };
  }

  /**
   * 현재 분석 모드 확인
   */
  getAnalysisMode(): string {
    if (this.realValueAvailable) {
      return '실제값 (백엔드 FFT 알고리즘)';
    } else {
      return '서비스 불가 (백엔드 연결 필요)';
    }
  }
} 