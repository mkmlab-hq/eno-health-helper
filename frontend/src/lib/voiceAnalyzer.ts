import { realValueAPI } from './realValueAPI';

export interface VoiceAnalysisResult {
  jitter: number;
  shimmer: number;
  hnr: number;
  pitch: number;
  volume: string; // intensity를 volume으로 변경
  clarity: number; // 명확도 추가
  emotion: string; // 감정 추가
  frequency: number; // 기본 주파수 추가
  stressLevel: number;
  confidence: number;
  quality: string; // 품질 정보 추가
  timestamp: Date;
  // 실제값 API 응답 필드 추가
  isRealValue?: boolean;
}

export class VoiceAnalyzer {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private isRecording: boolean = false;
  private audioData: Array<Float32Array> = [];
  private recordingDuration: number = 5000; // 5초
  private recordingStartTime: number = 0;
  private stream: MediaStream | null = null;
  private realValueAvailable: boolean = false;

  constructor(stream: MediaStream) {
    this.stream = stream;
    this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    this.analyser = this.audioContext.createAnalyser();
    this.analyser.fftSize = 2048;
    this.analyser.smoothingTimeConstant = 0.8;
    
    // 실제값 API 사용 가능 여부 확인
    this.checkRealValueAvailability();
  }

  /**
   * 실제값 API 사용 가능 여부 확인
   */
  private async checkRealValueAvailability(): Promise<void> {
    try {
      this.realValueAvailable = await realValueAPI.isRealValueAvailable();
      console.log(`음성 분석 실제값 API 사용 가능: ${this.realValueAvailable}`);
    } catch (error) {
      console.error('음성 분석 실제값 API 확인 실패:', error);
      this.realValueAvailable = false;
    }
  }

  // 음성 녹음 시작
  async startRecording(): Promise<boolean> {
    try {
      if (!this.stream) {
        const newStream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            sampleRate: 44100,
            channelCount: 1
          }
        });
        this.stream = newStream;
      }
      
      this.microphone = this.audioContext!.createMediaStreamSource(this.stream);
      this.microphone.connect(this.analyser!);
      
      this.isRecording = true;
      this.audioData = [];
      this.recordingStartTime = Date.now();
      
      this.recordAudio();
      
      // 지정된 시간 후 자동 중지
      setTimeout(() => {
        this.stopRecording();
      }, this.recordingDuration);
      
      return true;
    } catch (error) {
      console.error('음성 녹음 시작 실패:', error);
      return false;
    }
  }

  // 음성 녹음 중지
  stopRecording(): VoiceAnalysisResult | null {
    if (!this.isRecording) return null;
    
    this.isRecording = false;
    
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }
    
    // 분석 수행
    this.analyzeVoice();
    
    return null;
  }

  // 오디오 데이터 수집
  private recordAudio(): void {
    if (!this.isRecording || !this.analyser) return;
    
    const dataArray = new Float32Array(this.analyser.frequencyBinCount);
    this.analyser.getFloatFrequencyData(dataArray);
    
    this.audioData.push(new Float32Array(dataArray));
    
    if (this.isRecording) {
      requestAnimationFrame(() => this.recordAudio());
    }
  }

  // 음성 분석 수행
  private async analyzeVoice(): Promise<void> {
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
      console.error('음성 분석 실패:', error);
      if (this.onResultCallback) {
        this.onResultCallback(this.getDefaultResult());
      }
    }
  }

  // 실제값 API 분석
  private async getRealValueAnalysis(): Promise<VoiceAnalysisResult> {
    const request = {
      audioData: this.audioData[0] || new Float32Array(),
      sampleRate: 44100,
      duration: this.recordingDuration / 1000
    };
    
    try {
      const response = await realValueAPI.analyzeRealVoice(request);
      
      return {
        jitter: response.jitter,
        shimmer: response.shimmer,
        hnr: response.hnr,
        pitch: response.f0,
        volume: this.mapVolume(response.f0), // f0를 volume으로 사용
        clarity: this.calculateClarity(response.jitter, response.shimmer),
        emotion: this.calculateEmotion(response.f0, response.jitter),
        frequency: response.f0,
        stressLevel: this.calculateStressLevel(response.jitter, response.shimmer, response.hnr),
        confidence: response.confidence,
        quality: response.voice_quality,
        timestamp: new Date(),
        isRealValue: true
      };
    } catch (error) {
      console.error('실제값 API 호출 실패:', error);
      throw error;
    }
  }

  // 볼륨 매핑
  private mapVolume(volume: number): string {
    if (volume < 0.3) return 'Low';
    if (volume < 0.7) return 'Medium';
    return 'High';
  }

  // 명확도 계산
  private calculateClarity(jitter: number, shimmer: number): number {
    const clarityScore = Math.max(0, 100 - (jitter * 1000) - (shimmer * 1000));
    return Math.round(clarityScore);
  }

  // 감정 계산
  private calculateEmotion(pitch: number, jitter: number): string {
    if (pitch > 200) return 'Excited';
    if (jitter > 0.05) return 'Stressed';
    if (pitch < 150) return 'Calm';
    return 'Neutral';
  }

  // 스트레스 수준 계산
  private calculateStressLevel(jitter: number, shimmer: number, hnr: number): number {
    const stressScore = (jitter * 1000) + (shimmer * 1000) + ((30 - hnr) / 30);
    return Math.round(Math.min(100, stressScore * 100));
  }

  // 기본 결과 반환
  private getDefaultResult(): VoiceAnalysisResult {
    return {
      jitter: 0,
      shimmer: 0,
      hnr: 0,
      pitch: 0,
      volume: 'Low',
      clarity: 0,
      emotion: 'Neutral',
      frequency: 150,
      stressLevel: 0,
      confidence: 0,
      quality: 'Poor',
      timestamp: new Date(),
      isRealValue: false
    };
  }

  // 녹음 상태 확인
  isCurrentlyRecording(): boolean {
    return this.isRecording;
  }

  // 녹음 진행률 계산
  getRecordingProgress(): number {
    if (!this.isRecording) return 0;
    const elapsed = Date.now() - this.recordingStartTime;
    return Math.min(100, (elapsed / this.recordingDuration) * 100);
  }

  // 결과 콜백
  private onResultCallback: ((result: VoiceAnalysisResult) => void) | null = null;
  
  onResult(callback: (result: VoiceAnalysisResult) => void): void {
    this.onResultCallback = callback;
  }

  // 정리
  dispose(): void {
    this.stopRecording();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
  }

  /**
   * 현재 분석 모드 확인
   */
  getAnalysisMode(): string {
    if (this.realValueAvailable) {
      return '실제값 (백엔드 librosa 알고리즘)';
    } else {
      return '서비스 불가 (백엔드 연결 필요)';
    }
  }
} 