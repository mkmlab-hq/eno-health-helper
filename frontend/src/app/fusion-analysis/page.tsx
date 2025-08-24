'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoadingSpinner from './components/LoadingSpinner';
import ProgressSteps from './components/ProgressSteps';

interface FusionAnalysisResult {
  temperament: {
    temperament: string;
    confidence: number;
    message: string;
  };
  confidence: number;
  message: string;
  timestamp: string;
}

export default function FusionAnalysisPage() {
  const router = useRouter();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<FusionAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const recordingStartTimeRef = useRef<number | null>(null);
  const analysisAbortControllerRef = useRef<AbortController | null>(null);
  const hasAutoStartedRef = useRef(false);
  const [autoStart, setAutoStart] = useState(true);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [maxRecordSeconds, setMaxRecordSeconds] = useState(10);

  // 분석 단계 정의
  const analysisSteps = [
    {
      id: 'rppg',
      title: 'rPPG 특징 추출',
      description: '얼굴 영상에서 생체신호 특징을 추출하고 있습니다',
      status: 'pending' as const
    },
    {
      id: 'voice',
      title: '음성 특징 추출',
      description: '오디오에서 음성 품질 특징을 분석하고 있습니다',
      status: 'pending' as const
    },
    {
      id: 'fusion',
      title: 'AI 융합 분석',
      description: 'rPPG와 음성 데이터를 융합하여 기질을 진단하고 있습니다',
      status: 'pending' as const
    }
  ];

  // 반응형 디자인 감지
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // 페이지 진입 시 자동 녹화 시작 (옵션)
  useEffect(() => {
    if (!autoStart) return;
    if (hasAutoStartedRef.current) return;
    hasAutoStartedRef.current = true;
    startVideoRecording();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart]);

  // 탭 비활성화/이탈 시 녹화 정리
  useEffect(() => {
    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && isRecording) {
        stopRecording();
      }
    };
    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => document.removeEventListener('visibilitychange', onVisibilityChange);
  }, [isRecording]);

  // 언마운트 시 스트림 정리
  useEffect(() => {
    return () => {
      try {
        const stream = videoRef.current?.srcObject as MediaStream | null;
        if (stream) {
          stream.getTracks().forEach(t => t.stop());
        }
      } catch {}
    };
  }, []);

  // 녹화 진행률 업데이트 (경과 시간 기반)
  useEffect(() => {
    if (isRecording) {
      const progressInterval = setInterval(() => {
        if (!recordingStartTimeRef.current) return;
        const elapsedSec = (Date.now() - recordingStartTimeRef.current) / 1000;
        const pct = Math.min(100, (elapsedSec / maxRecordSeconds) * 100);
        setRecordingProgress(pct);
      }, 100);
      
      return () => clearInterval(progressInterval);
    } else {
      setRecordingProgress(0);
    }
  }, [isRecording, maxRecordSeconds]);

  // 녹화 자동 종료 (설정 시간 도달)
  useEffect(() => {
    if (isRecording && recordingProgress >= 100) {
      stopRecording();
    }
  }, [isRecording, recordingProgress]);

  // 분석 단계 시뮬레이션
  useEffect(() => {
    if (isAnalyzing) {
      const stepInterval = setInterval(() => {
        setAnalysisStep(prev => {
          if (prev >= 2) return 2;
          return prev + 1;
        });
      }, 2000);
      
      return () => clearInterval(stepInterval);
    } else {
      setAnalysisStep(0);
    }
  }, [isAnalyzing]);

  // 오디오 업로드 후 자동 분석 실행
  useEffect(() => {
    if (autoAnalyze && audioBlob && videoBlob && !isAnalyzing) {
      runFusionAnalysis();
    }
  }, [autoAnalyze, audioBlob, videoBlob, isAnalyzing]);

  // 비디오 녹화 시작
  const startVideoRecording = async () => {
    try {
      if (!('mediaDevices' in navigator)) {
        setError('이 브라우저는 카메라 사용을 지원하지 않습니다.');
        return;
      }
      if (!window.isSecureContext) {
        setError('보안되지 않은 환경입니다. https 환경에서 다시 시도해주세요.');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: isMobile ? 480 : 640, 
          height: isMobile ? 360 : 480,
          facingMode: 'user'
        }, 
        audio: false 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      const chunks: Blob[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        setVideoBlob(blob);
        recordingStartTimeRef.current = null;
        
        // 스트림 정리
        stream.getTracks().forEach(track => track.stop());
      };
      
      recordingStartTimeRef.current = Date.now();
      mediaRecorder.start(1000); // 매 1초마다 청크 수집
      setIsRecording(true);
      setRecordingTime(0);
      setRecordingProgress(0);
      
      // 녹화 시간 카운터
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err: any) {
      console.error('비디오 녹화 시작 실패:', err);
      const name = err?.name || '';
      if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
        setError('카메라 권한이 거부되었습니다. 브라우저 설정에서 권한을 허용해주세요.');
      } else if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
        setError('사용 가능한 카메라를 찾을 수 없습니다.');
      } else if (name === 'NotReadableError') {
        setError('카메라 장치를 사용할 수 없습니다. 다른 앱이 사용 중일 수 있습니다.');
      } else if (name === 'OverconstrainedError') {
        setError('요청한 카메라 해상도를 지원하지 않습니다.');
      } else if (name === 'SecurityError') {
        setError('보안 정책에 의해 차단되었습니다. https 환경에서 시도해주세요.');
      } else {
        setError('카메라 접근 권한이 필요합니다.');
      }
    }
  };

  // 녹화 중지
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      recordingStartTimeRef.current = null;
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  // 오디오 파일 업로드
  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && (file.type.startsWith('audio/') || file.name.match(/\.(wav|mp3|m4a|flac)$/i))) {
      setAudioBlob(file);
      setError(null);
      if (autoAnalyze && videoBlob && !isAnalyzing) {
        setTimeout(() => runFusionAnalysis(), 0);
      }
    } else {
      setError('올바른 오디오 파일을 선택해주세요.');
    }
  };

  // 융합 분석 취소
  const cancelAnalysis = () => {
    try {
      analysisAbortControllerRef.current?.abort();
    } catch {}
    analysisAbortControllerRef.current = null;
    setIsAnalyzing(false);
    setAnalysisStep(0);
  };

  // 융합 분석 실행
  const runFusionAnalysis = async () => {
    if (!videoBlob || !audioBlob) {
      setError('비디오와 오디오 데이터가 모두 필요합니다.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisStep(0);

    const controller = new AbortController();
    analysisAbortControllerRef.current = controller;

    try {
      const formData = new FormData();
      formData.append('video', videoBlob, 'recording.webm');
      formData.append('audio', audioBlob, 'audio.wav');
      formData.append('user_id', 'demo_user');

      const response = await fetch('/api/health/fusion-analysis', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      if (!response.ok) {
        let message = '분석 중 오류가 발생했습니다.';
        try {
          const data = await response.json();
          message = data?.error || data?.detail || message;
        } catch {}
        throw new Error(message);
      }

      const analysisResult = await response.json();
      setResult(analysisResult);
      
    } catch (err: any) {
      console.error('융합 분석 실패:', err);
      const isAbort = err?.name === 'AbortError';
      setError(isAbort ? '분석이 취소되었습니다.' : (err instanceof Error ? err.message : '분석 중 오류가 발생했습니다.'));
    } finally {
      setIsAnalyzing(false);
      setAnalysisStep(0);
      analysisAbortControllerRef.current = null;
    }
  };

  // 현재 분석 단계 상태 계산
  const getCurrentSteps = () => {
    return analysisSteps.map((step, index) => ({
      ...step,
      status: (index < analysisStep ? 'completed' : index === analysisStep ? 'active' : 'pending') as 'pending' | 'active' | 'completed' | 'error'
    }));
  };

  // 결과 페이지로 이동
  const goToResult = () => {
    if (result) {
      router.push(`/result?temperament=${result.temperament.temperament}&confidence=${result.confidence}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-2 sm:p-4">
      <div className="max-w-6xl mx-auto">
        {/* 헤더 */}
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-gray-800 mb-3 sm:mb-4">
            🧬 4대 디지털 기질 융합 분석
          </h1>
          <p className="text-sm sm:text-base lg:text-lg text-gray-600 px-4">
            rPPG와 음성을 동시에 분석하여 정확한 기질을 진단합니다
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
          {/* 왼쪽: 데이터 수집 */}
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
            <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 mb-4 sm:mb-6">
              📹 생체신호 데이터 수집
            </h2>

            {/* 자동화 설정 */}
            <div className="flex items-center gap-4 mb-4">
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input type="checkbox" className="rounded" checked={autoStart} onChange={(e) => setAutoStart(e.target.checked)} />
                자동 녹화
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input type="checkbox" className="rounded" checked={autoAnalyze} onChange={(e) => setAutoAnalyze(e.target.checked)} />
                자동 분석 (업로드 후)
              </label>
              <div className="ml-auto text-xs text-gray-500">최대 {maxRecordSeconds}초 녹화</div>
            </div>

            {/* 비디오 녹화 섹션 */}
            <div className="mb-6">
              <h3 className="text-base sm:text-lg font-medium text-gray-700 mb-3">1. 얼굴 영상 녹화</h3>
              
              <div className="relative">
                <video
                  ref={videoRef}
                  className="w-full h-32 sm:h-40 md:h-48 bg-gray-200 rounded-lg mb-3"
                  autoPlay
                  muted
                  playsInline
                />
                
                {/* 녹화 진행률 바 */}
                {isRecording && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b-lg overflow-hidden">
                    <div 
                      className="h-full bg-red-500 transition-all duration-100 ease-linear"
                      style={{ width: `${recordingProgress}%` }}
                    ></div>
                  </div>
                )}
                
                {isRecording && (
                  <div className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded text-xs sm:text-sm font-medium">
                    🔴 {Math.floor(recordingTime / 60)}:{(recordingTime % 60).toString().padStart(2, '0')}
                  </div>
                )}
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                {!isRecording ? (
                  <button
                    onClick={startVideoRecording}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-3 sm:px-4 py-2 rounded-lg transition-colors text-sm sm:text-base font-medium"
                  >
                    🎬 녹화 시작
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="bg-red-500 hover:bg-red-600 text-white px-3 sm:px-4 py-2 rounded-lg transition-colors text-sm sm:text-base font-medium"
                  >
                    ⏹️ 녹화 중지
                  </button>
                )}
              </div>

              {videoBlob && (
                <div className="mt-3 p-2 bg-green-100 rounded text-green-800 text-xs sm:text-sm">
                  ✅ 비디오 녹화 완료 ({Math.round(videoBlob.size / 1024)}KB)
                </div>
              )}
            </div>

            {/* 오디오 업로드 섹션 */}
            <div className="mb-6">
              <h3 className="text-base sm:text-lg font-medium text-gray-700 mb-3">2. 음성 파일 업로드</h3>
              
              <div className="relative">
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleAudioUpload}
                  className="block w-full text-xs sm:text-sm text-gray-500 file:mr-2 sm:file:mr-4 file:py-2 file:px-3 sm:file:px-4 file:rounded-full file:border-0 file:text-xs sm:file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors"
                />
                
                {/* 드래그 앤 드롭 영역 */}
                <div className="mt-2 p-3 border-2 border-dashed border-gray-300 rounded-lg text-center text-xs sm:text-sm text-gray-500 hover:border-blue-400 transition-colors">
                  또는 오디오 파일을 여기에 드래그하세요
                </div>
              </div>

              {audioBlob && (
                <div className="mt-3 p-2 bg-green-100 rounded text-green-800 text-xs sm:text-sm">
                  ✅ 오디오 파일 업로드 완료 ({Math.round(audioBlob.size / 1024)}KB)
                </div>
              )}
            </div>

            {/* 분석 실행 버튼 */}
            <button
              onClick={runFusionAnalysis}
              disabled={!videoBlob || !audioBlob || isAnalyzing}
              className={`w-full py-3 px-6 rounded-lg text-white font-medium transition-all duration-300 transform ${
                !videoBlob || !audioBlob || isAnalyzing
                  ? 'bg-gray-400 cursor-not-allowed scale-95'
                  : 'bg-indigo-600 hover:bg-indigo-700 hover:scale-105 active:scale-95'
              }`}
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-white mr-2"></div>
                  <span className="text-sm sm:text-base">융합 분석 중...</span>
                </span>
              ) : (
                <span className="text-sm sm:text-base">🧬 융합 분석 실행</span>
              )}
            </button>
            {isAnalyzing && (
              <button
                onClick={cancelAnalysis}
                className="mt-2 w-full py-2 px-4 rounded-lg text-white bg-gray-600 hover:bg-gray-700 transition-colors text-sm sm:text-base font-medium"
              >
                ⛔ 분석 취소
              </button>
            )}
          </div>

          {/* 오른쪽: 결과 표시 */}
          <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
            <h2 className="text-xl sm:text-2xl font-semibold text-gray-800 mb-4 sm:mb-6">
              📊 분석 결과
            </h2>

            {error && (
              <div className="mb-4 p-3 sm:p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm">
                ❌ {error}
              </div>
            )}

            {!result && !isAnalyzing && (
              <div className="text-center text-gray-500 py-8 sm:py-12">
                <div className="text-4xl sm:text-6xl mb-4">🔍</div>
                <p className="text-sm sm:text-base">왼쪽에서 데이터를 수집하고 분석을 실행해주세요</p>
              </div>
            )}

            {isAnalyzing && (
              <div className="text-center py-8 sm:py-12">
                <LoadingSpinner 
                  size="lg" 
                  color="purple" 
                  text="융합 분석을 진행하고 있습니다..."
                />
                
                {/* 분석 단계 표시 */}
                <div className="mt-6">
                  <ProgressSteps 
                    steps={getCurrentSteps()} 
                    currentStep={analysisStep}
                  />
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* 기질 결과 */}
                <div className="p-4 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-lg">
                  <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-2">
                    🎯 진단된 기질
                  </h3>
                  <div className="text-2xl sm:text-3xl font-bold text-indigo-700 mb-2">
                    {result.temperament.temperament}
                  </div>
                  <p className="text-sm text-gray-600">
                    {result.temperament.message}
                  </p>
                </div>

                {/* 신뢰도 */}
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-2">
                    📈 분석 신뢰도
                  </h3>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 sm:h-3">
                      <div
                        className="bg-blue-500 h-full rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${result.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-base sm:text-lg font-semibold text-blue-600">
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                </div>

                {/* 분석 정보 */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-2">
                    ℹ️ 분석 정보
                  </h3>
                  <div className="space-y-1 text-xs sm:text-sm text-gray-600">
                    <div>분석 시간: {new Date(result.timestamp).toLocaleString()}</div>
                    <div>분석 유형: 융합 건강 분석</div>
                    <div>데이터 소스: rPPG + 음성</div>
                  </div>
                </div>

                {/* 결과 페이지 이동 버튼 */}
                <button
                  onClick={goToResult}
                  className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-medium transition-all duration-300 transform hover:scale-105 active:scale-95"
                >
                  📋 상세 결과 보기
                </button>
              </div>
            )}
          </div>
        </div>

        {/* 안내 정보 */}
        <div className="mt-6 sm:mt-8 bg-white rounded-xl shadow-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-semibold text-gray-800 mb-4">
            💡 융합 분석이란?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs sm:text-sm text-gray-600">
            <div className="text-center">
              <div className="text-2xl sm:text-3xl mb-2">📹</div>
              <h3 className="font-medium text-gray-800 mb-2">rPPG 분석</h3>
              <p>얼굴 영상에서 심박수, 혈압 등 생체신호를 비접촉으로 측정</p>
            </div>
            <div className="text-center">
              <div className="text-2xl sm:text-3xl mb-2">🎵</div>
              <h3 className="font-medium text-gray-800 mb-2">음성 분석</h3>
              <p>목소리에서 감정 상태, 스트레스 레벨, 음성 패턴을 분석</p>
            </div>
            <div className="text-center">
              <div className="text-2xl sm:text-3xl mb-2">🧬</div>
              <h3 className="font-medium text-gray-800 mb-2">AI 융합</h3>
              <p>두 데이터를 결합하여 더 정확한 4대 디지털 기질 진단</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
