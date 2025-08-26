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
  // 단계: welcome, face, voice, analyzing, done
  const [screen, setScreen] = useState<'welcome'|'face'|'voice'|'analyzing'|'done'>('welcome');
  const [faceTimeLeft, setFaceTimeLeft] = useState(30);
  const [voiceTimeLeft, setVoiceTimeLeft] = useState(5);
  const [isAudioRecording, setIsAudioRecording] = useState(false);
  const audioRecorderRef = useRef<MediaRecorder | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  // 오디오 자동 녹음용 (중복 선언 제거됨)


  // 측정 시작하기 버튼 클릭 시 전체 측정 플로우 시작
  const startFullMeasurement = async () => {
    setScreen('face');
    setFaceTimeLeft(30);
    setVoiceTimeLeft(5);
    setAudioBlob(null);
    setVideoBlob(null);
    setResult(null);
    setError(null);
    // 얼굴 녹화 시작
    await startVideoRecording();
  };

  // 얼굴 측정 타이머 및 자동 정지
  useEffect(() => {
    if (screen === 'face' && isRecording) {
      if (faceTimeLeft === 0) {
        stopRecording();
        setScreen('voice');
      } else {
        const timer = setTimeout(() => setFaceTimeLeft(faceTimeLeft - 1), 1000);
        return () => clearTimeout(timer);
      }
    }
  }, [screen, faceTimeLeft, isRecording]);

  // 얼굴 녹화가 끝나면 음성 녹음 시작
  useEffect(() => {
    if (screen === 'voice' && !audioBlob && !isAudioRecording) {
      const doAudio = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
          audioRecorderRef.current = mediaRecorder;
          const chunks: Blob[] = [];
          mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) chunks.push(event.data);
          };
          mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/webm' });
            setAudioBlob(blob);
            stream.getTracks().forEach(track => track.stop());
            setIsAudioRecording(false);
          };
          mediaRecorder.start();
          setIsAudioRecording(true);
        } catch (err) {
          setError('마이크 접근 권한이 필요합니다.');
        }
      };
      doAudio();
    }
  }, [screen, audioBlob, isAudioRecording]);

  // 음성 측정 타이머 및 자동 정지
  useEffect(() => {
    if (screen === 'voice' && isAudioRecording) {
      if (voiceTimeLeft === 0) {
        if (audioRecorderRef.current) audioRecorderRef.current.stop();
      } else {
        const timer = setTimeout(() => setVoiceTimeLeft(voiceTimeLeft - 1), 1000);
        return () => clearTimeout(timer);
      }
    }
  }, [screen, voiceTimeLeft, isAudioRecording]);

  // 비디오와 오디오가 모두 준비되면 자동 분석 실행
  useEffect(() => {
    if (screen === 'voice' && videoBlob && audioBlob && !isAnalyzing && !result) {
      setScreen('analyzing');
      runFusionAnalysis();
    }
  }, [screen, videoBlob, audioBlob, isAnalyzing, result]);

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

  // 녹화 진행률 업데이트
  useEffect(() => {
    if (isRecording) {
      const progressInterval = setInterval(() => {
        setRecordingProgress(prev => {
          if (prev >= 100) return 100;
          return prev + 1;
        });
      }, 100);
      
      return () => clearInterval(progressInterval);
    } else {
      setRecordingProgress(0);
    }
  }, [isRecording]);

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

  // 비디오 녹화 시작
  const startVideoRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: isMobile ? 480 : 640, 
          height: isMobile ? 360 : 480,
          facingMode: 'user'
        }, 
        audio: true 
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
        
        // 스트림 정리
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      setRecordingProgress(0);
      
      // 녹화 시간 카운터
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('비디오 녹화 시작 실패:', err);
      setError('카메라 접근 권한이 필요합니다.');
    }
  };

  // 녹화 중지
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  // 오디오 파일 업로드
  const handleAudioUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('audio/')) {
      setAudioBlob(file);
      setError(null);
    } else {
      setError('올바른 오디오 파일을 선택해주세요.');
    }
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

    try {
      const formData = new FormData();
      formData.append('video', videoBlob, 'recording.webm');
      formData.append('audio', audioBlob, 'audio.wav');
      formData.append('user_id', 'demo_user');

      const response = await fetch('/api/health/fusion-analysis', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`분석 실패: ${response.statusText}`);
      }

      const analysisResult = await response.json();
      setResult(analysisResult);
      
    } catch (err) {
      console.error('융합 분석 실패:', err);
      setError(err instanceof Error ? err.message : '분석 중 오류가 발생했습니다.');
    } finally {
      setIsAnalyzing(false);
      setAnalysisStep(0);
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-2 sm:p-4 flex flex-col items-center justify-center">
      {/* 단계별 화면 */}
      {screen === 'welcome' && (
        <div className="flex flex-col items-center justify-center gap-8">
          <h1 className="text-3xl md:text-5xl font-black text-indigo-900 mb-4 font-orbitron">엔오건강도우미 검사</h1>
          <p className="text-lg text-gray-700 mb-8">AI rPPG와 음성 분석을 통해 35초 만에 건강 상태를 측정합니다.</p>
          <button
            className="bg-sky-500 hover:bg-sky-600 text-white font-bold py-4 px-10 rounded-full text-xl shadow-lg transition"
            onClick={startFullMeasurement}
          >
            측정 시작하기
          </button>
        </div>
      )}

      {screen === 'face' && (
        <div className="flex flex-col items-center justify-center gap-8">
          <h2 className="text-2xl md:text-4xl font-bold text-sky-700 mb-2 font-orbitron">얼굴 인식 중...</h2>
          <p className="text-lg text-gray-600 mb-4">정확한 측정을 위해 화면 중앙에 얼굴을 맞춰주세요.</p>
          <video
            ref={videoRef}
            className="w-64 h-80 bg-black/50 rounded-lg border border-sky-500/50 mb-4"
            autoPlay
            muted
            playsInline
          />
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="absolute w-full h-full" viewBox="0 0 100 100">
              <circle
                className="progress-ring__circle text-sky-400"
                strokeWidth="6"
                stroke="currentColor"
                fill="transparent"
                r="48"
                cx="50"
                cy="50"
                style={{
                  strokeDasharray: 301.59,
                  strokeDashoffset: 301.59 * (1 - faceTimeLeft / 30),
                  transition: 'stroke-dashoffset 1s linear',
                }}
              />
            </svg>
            <span className="absolute text-3xl font-bold text-sky-700 font-orbitron">{faceTimeLeft}s</span>
          </div>
        </div>
      )}

      {screen === 'voice' && (
        <div className="flex flex-col items-center justify-center gap-8">
          <h2 className="text-2xl md:text-4xl font-bold text-sky-700 mb-2 font-orbitron">음성 분석 중...</h2>
          <p className="text-lg text-gray-600 mb-4 animate-pulse">지금부터 "아~" 소리를 내주세요.</p>
          <div className="relative w-32 h-32 flex items-center justify-center">
            <svg className="absolute w-full h-full" viewBox="0 0 100 100">
              <circle
                className="progress-ring__circle text-purple-400"
                strokeWidth="6"
                stroke="currentColor"
                fill="transparent"
                r="48"
                cx="50"
                cy="50"
                style={{
                  strokeDasharray: 301.59,
                  strokeDashoffset: 301.59 * (1 - voiceTimeLeft / 5),
                  transition: 'stroke-dashoffset 1s linear',
                }}
              />
            </svg>
            <span className="absolute text-3xl font-bold text-purple-700 font-orbitron">{voiceTimeLeft}s</span>
          </div>
        </div>
      )}

      {screen === 'analyzing' && (
        <div className="flex flex-col items-center justify-center gap-8">
          <div className="animate-spin rounded-full h-32 w-32 border-t-4 border-b-4 border-sky-400 mb-4"></div>
          <h2 className="text-2xl md:text-4xl font-bold text-sky-700 font-orbitron">분석 중...</h2>
        </div>
      )}

      {result && screen === 'analyzing' && (
        <div className="flex flex-col items-center justify-center gap-8 mt-8">
          <h2 className="text-2xl md:text-4xl font-bold text-green-700 font-orbitron">분석 완료!</h2>
          <div className="p-6 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">🎯 진단된 기질</h3>
            <div className="text-2xl font-bold text-indigo-700 mb-2">{result.temperament.temperament}</div>
            <p className="text-sm text-gray-600">{result.temperament.message}</p>
            <div className="mt-4">
              <span className="text-base font-semibold text-blue-600">신뢰도: {Math.round(result.confidence * 100)}%</span>
            </div>
          </div>
          <button
            onClick={() => setScreen('welcome')}
            className="mt-4 bg-sky-500 hover:bg-sky-600 text-white font-bold py-3 px-8 rounded-full text-lg transition"
          >
            다시 측정하기
          </button>
        </div>
      )}

      {error && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 rounded-lg px-6 py-3 text-lg shadow-lg z-50">
          ❌ {error}
        </div>
      )}
    </div>
  );
}
