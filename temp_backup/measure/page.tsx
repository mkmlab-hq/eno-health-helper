'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { signOutUser } from '../../../lib/firebase';

type MeasurementStep = 'start' | 'face' | 'voice' | 'analyzing' | 'complete';

interface MeasurementData {
  bpm?: number;
  hrv?: number;
  jitter?: number;
  shimmer?: number;
  timestamp: Date;
}

export default function MeasurePage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<MeasurementStep>('start');
  const [progress, setProgress] = useState(0);
  const [measurementData, setMeasurementData] = useState<MeasurementData | null>(null);
  const [isMeasuring, setIsMeasuring] = useState(false);
  const [error, setError] = useState('');
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // 인증 상태 확인
  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  // 로그아웃 처리
  const handleLogout = async () => {
    try {
      await signOutUser();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // 측정 시작
  const startMeasurement = () => {
    setCurrentStep('face');
    setProgress(0);
    setError('');
    setIsMeasuring(true);
  };

  // 얼굴 측정 단계
  const startFaceMeasurement = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 }, 
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // 10초간 얼굴 측정 시뮬레이션
      let faceProgress = 0;
      const faceInterval = setInterval(() => {
        faceProgress += 10;
        setProgress(faceProgress);
        
        if (faceProgress >= 100) {
          clearInterval(faceInterval);
          setCurrentStep('voice');
          setProgress(0);
        }
      }, 1000);
    } catch (error) {
      setError('카메라에 접근할 수 없습니다. 카메라 권한을 확인해주세요.');
      console.error('Camera error:', error);
    }
  };

  // 음성 측정 단계
  const startVoiceMeasurement = async () => {
    try {
      const audioStream = await navigator.mediaDevices.getUserMedia({ 
        audio: { 
          sampleRate: 44100,
          channelCount: 1
        } 
      });

      // 15초간 음성 측정 시뮬레이션
      let voiceProgress = 0;
      const voiceInterval = setInterval(() => {
        voiceProgress += 6.67;
        setProgress(voiceProgress);
        
        if (voiceProgress >= 100) {
          clearInterval(voiceInterval);
          setCurrentStep('analyzing');
          setProgress(0);
          analyzeResults();
        }
      }, 1000);
    } catch (error) {
      setError('마이크에 접근할 수 없습니다. 마이크 권한을 확인해주세요.');
      console.error('Microphone error:', error);
    }
  };

  // 결과 분석
  const analyzeResults = () => {
    // 5초간 분석 시뮬레이션
    let analysisProgress = 0;
    const analysisInterval = setInterval(() => {
      analysisProgress += 20;
      setProgress(analysisProgress);
      
      if (analysisProgress >= 100) {
        clearInterval(analysisInterval);
        setCurrentStep('complete');
        
        // 시뮬레이션된 측정 결과 생성
        const mockData: MeasurementData = {
          bpm: Math.floor(Math.random() * 30) + 60, // 60-90 BPM
          hrv: Math.floor(Math.random() * 20) + 30, // 30-50 ms
          jitter: Math.random() * 2 + 0.5, // 0.5-2.5%
          shimmer: Math.random() * 3 + 1, // 1-4%
          timestamp: new Date()
        };
        
        setMeasurementData(mockData);
      }
    }, 1000);
  };

  // 측정 단계별 렌더링
  const renderStep = () => {
    switch (currentStep) {
      case 'start':
        return (
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                고요 속의 메아리
              </h2>
              <p className="text-xl text-slate-300 font-noto-sans">
                건강 측정을 시작합니다
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                  <div className="text-cyan-400 text-2xl mb-2">📷</div>
                  <h3 className="font-semibold text-slate-200">얼굴 측정</h3>
                  <p className="text-sm text-slate-400">rPPG 기술로 심박수 측정</p>
                </div>
                <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                  <div className="text-sky-400 text-2xl mb-2">🎤</div>
                  <h3 className="font-semibold text-slate-200">음성 분석</h3>
                  <p className="text-sm text-slate-400">음성 특성으로 건강 상태 파악</p>
                </div>
                <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                  <div className="text-purple-400 text-2xl mb-2">🧠</div>
                  <h3 className="font-semibold text-slate-200">AI 분석</h3>
                  <p className="text-sm text-slate-400">종합 건강 지표 도출</p>
                </div>
              </div>
              
              <button
                onClick={startMeasurement}
                className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-sky-500 text-white font-bold text-xl rounded-xl hover:from-cyan-600 hover:to-sky-600 transition-all duration-200 transform hover:scale-105"
              >
                측정 시작하기
              </button>
            </div>
          </div>
        );

      case 'face':
        return (
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                얼굴 측정 중
              </h2>
              <p className="text-xl text-slate-300 font-noto-sans">
                카메라를 정면으로 바라보세요
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="relative mx-auto w-80 h-60">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full rounded-xl border-4 border-cyan-400"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 border-4 border-cyan-400 rounded-full opacity-50 animate-pulse"></div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-cyan-400 to-sky-400 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-slate-300">{progress}% 완료</p>
              </div>
            </div>
          </div>
        );

      case 'voice':
        return (
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                음성 측정 중
              </h2>
              <p className="text-xl text-slate-300 font-noto-sans">
                "아" 소리를 길게 내주세요
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-80 h-32 mx-auto bg-gradient-to-r from-slate-800 to-slate-700 rounded-xl border border-slate-600 p-4">
                <div className="flex items-end justify-center space-x-1 h-full">
                  {Array.from({ length: 20 }, (_, i) => (
                    <div
                      key={i}
                      className="w-2 bg-gradient-to-t from-cyan-400 to-sky-400 rounded-full animate-pulse"
                      style={{ 
                        height: `${Math.random() * 60 + 20}%`,
                        animationDelay: `${i * 0.1}s`
                      }}
                    ></div>
                  ))}
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-sky-400 to-purple-400 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-slate-300">{progress}% 완료</p>
              </div>
            </div>
          </div>
        );

      case 'analyzing':
        return (
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                분석 중
              </h2>
              <p className="text-xl text-slate-300 font-noto-sans">
                AI가 측정 결과를 분석하고 있습니다
              </p>
            </div>
            
            <div className="space-y-6">
              <div className="w-32 h-32 mx-auto">
                <div className="relative w-full h-full">
                  <div className="absolute inset-0 border-4 border-cyan-400 rounded-full animate-spin border-t-transparent"></div>
                  <div className="absolute inset-2 border-4 border-sky-400 rounded-full animate-spin border-b-transparent" style={{ animationDirection: 'reverse' }}></div>
                  <div className="absolute inset-4 border-4 border-purple-400 rounded-full animate-spin border-l-transparent"></div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-purple-400 to-pink-400 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-slate-300">{progress}% 완료</p>
              </div>
            </div>
          </div>
        );

      case 'complete':
        return (
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                측정 완료!
              </h2>
              <p className="text-xl text-slate-300 font-noto-sans">
                건강 측정이 성공적으로 완료되었습니다
              </p>
            </div>
            
            {measurementData && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                    <div className="text-cyan-400 text-2xl mb-2">💓</div>
                    <h3 className="font-semibold text-slate-200">심박수</h3>
                    <p className="text-3xl font-bold text-cyan-400">{measurementData.bpm} BPM</p>
                  </div>
                  <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                    <div className="text-sky-400 text-2xl mb-2">📊</div>
                    <h3 className="font-semibold text-slate-200">심박변이도</h3>
                    <p className="text-3xl font-bold text-sky-400">{measurementData.hrv} ms</p>
                  </div>
                  <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                    <div className="text-purple-400 text-2xl mb-2">🎵</div>
                    <h3 className="font-semibold text-slate-200">Jitter</h3>
                    <p className="text-3xl font-bold text-purple-400">{measurementData.jitter?.toFixed(1)}%</p>
                  </div>
                  <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600">
                    <div className="text-pink-400 text-2xl mb-2">🎶</div>
                    <h3 className="font-semibold text-slate-200">Shimmer</h3>
                    <p className="text-3xl font-bold text-pink-400">{measurementData.shimmer?.toFixed(1)}%</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <button
                    onClick={() => router.push('/result')}
                    className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold text-xl rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 transform hover:scale-105"
                  >
                    상세 결과 보기
                  </button>
                  
                  <button
                    onClick={() => {
                      setCurrentStep('start');
                      setProgress(0);
                      setMeasurementData(null);
                      setIsMeasuring(false);
                    }}
                    className="px-8 py-4 bg-slate-600 text-white font-bold text-xl rounded-xl hover:bg-slate-700 transition-all duration-200"
                  >
                    다시 측정하기
                  </button>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  // 측정 단계별 자동 진행
  useEffect(() => {
    if (currentStep === 'face' && !isMeasuring) {
      startFaceMeasurement();
    } else if (currentStep === 'voice' && !isMeasuring) {
      startVoiceMeasurement();
    }
  }, [currentStep]);

  // 스트림 정리
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-400 rounded-full animate-spin border-t-transparent mx-auto mb-4"></div>
          <p className="text-slate-300">로딩 중...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* 헤더 */}
      <header className="bg-slate-800/50 backdrop-blur-xl border-b border-white/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-sky-400 font-orbitron">
                엔오건강도우미
              </h1>
              <span className="text-slate-400">|</span>
              <span className="text-slate-300 font-noto-sans">건강 측정</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-slate-300 text-sm">
                {user.email}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition-colors duration-200"
              >
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          {error && (
            <div className="mb-8 p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-center">
              {error}
            </div>
          )}
          
          {renderStep()}
        </div>
      </main>
    </div>
  );
}
