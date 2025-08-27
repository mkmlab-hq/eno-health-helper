'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { RPPGAnalyzer, RPPGResult } from '@/lib/rppgAnalyzer';
import { VoiceAnalyzer, VoiceAnalysisResult } from '@/lib/voiceAnalyzer';
import { saveHealthData } from '@/lib/firebase';

export default function MeasurePage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<'ready' | 'face' | 'voice' | 'complete'>('ready');
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [privacyConsent, setPrivacyConsent] = useState(false);
  
  // 카메라 관련
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rppgAnalyzerRef = useRef<RPPGAnalyzer | null>(null);
  
  // 음성 관련
  const voiceAnalyzerRef = useRef<VoiceAnalyzer | null>(null);
  
  // 측정 결과
  const [rppgResult, setRppgResult] = useState<RPPGResult | null>(null);
  const [voiceResult, setVoiceResult] = useState<VoiceAnalysisResult | null>(null);
  
  // 진행률
  const [faceProgress, setFaceProgress] = useState(0);
  const [voiceProgress, setVoiceProgress] = useState(0);

  const FACE_SCAN_DURATION = 30000;  // 30초 얼굴 스캔
  const VOICE_RECORD_DURATION = 5000; // 5초 음성 녹음

  // 카메라 초기화
  const initializeCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 640,
          height: 480,
          frameRate: 30
        }
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        
        // rPPG 분석기 초기화
        rppgAnalyzerRef.current = new RPPGAnalyzer(videoRef.current);
        rppgAnalyzerRef.current.onResult((result) => {
          setRppgResult(result);
          console.log('rPPG 분석 완료:', result);
        });
      }
    } catch (err) {
      setError('카메라 접근 권한이 필요합니다.');
      console.error('Camera error:', err);
    }
  }, []);

  // 음성 분석기 초기화
  const initializeVoiceAnalyzer = useCallback(() => {
    voiceAnalyzerRef.current = new VoiceAnalyzer();
  }, []);

  // 측정 시작
  const startMeasurement = useCallback(async () => {
    try {
      if (!privacyConsent) {
        setShowPrivacyModal(true);
        return;
      }

      setCurrentStep('face');
      setError(null);
      setIsProcessing(true);
      
      // 카메라 초기화
      await initializeCamera();
      
      // rPPG 분석 시작
      if (rppgAnalyzerRef.current) {
        rppgAnalyzerRef.current.startAnalysis();
      }
      
      // 진행률 업데이트
      const progressInterval = setInterval(() => {
        setFaceProgress(prev => {
          const newProgress = prev + (100 / (FACE_SCAN_DURATION / 100));
          if (newProgress >= 100) {
            clearInterval(progressInterval);
            return 100;
          }
          return newProgress;
        });
      }, 100);
      
      // 30초 후 자동으로 voice 단계로
      setTimeout(() => {
        setCurrentStep('voice');
        setFaceProgress(100);
        
        // 음성 분석기 초기화
        initializeVoiceAnalyzer();
        
        // 음성 녹음 시작
        if (voiceAnalyzerRef.current) {
          voiceAnalyzerRef.current.startRecording();
        }
        
        // 음성 진행률 업데이트
        const voiceProgressInterval = setInterval(() => {
          setVoiceProgress(prev => {
            const newProgress = prev + (100 / (VOICE_RECORD_DURATION / 100));
            if (newProgress >= 100) {
              clearInterval(voiceProgressInterval);
              return 100;
            }
            return newProgress;
          });
        }, 100);
        
        // 5초 후 완료
        setTimeout(() => {
          setCurrentStep('complete');
          setVoiceProgress(100);
          setIsProcessing(false);
          
          // 음성 분석 결과 가져오기
          if (voiceAnalyzerRef.current) {
            const result = voiceAnalyzerRef.current.stopRecording();
            if (result) {
              setVoiceResult(result);
              console.log('음성 분석 완료:', result);
            }
          }
        }, VOICE_RECORD_DURATION);
        
      }, FACE_SCAN_DURATION);
      
    } catch (err) {
      setError('측정 시작 실패: ' + (err as Error).message);
      setIsProcessing(false);
    }
  }, [initializeCamera, initializeVoiceAnalyzer, privacyConsent]);

  // 측정 결과 저장
  const saveResults = useCallback(async () => {
    if (!rppgResult || !voiceResult) return;
    
    try {
      const userId = 'demo-user'; // 실제로는 인증된 사용자 ID
      const healthData = {
        rppg: rppgResult,
        voice: voiceResult,
        measurementType: 'combined',
        device: navigator.userAgent
      };
      
      const result = await saveHealthData(userId, healthData);
      if (result.success) {
        console.log('건강 데이터 저장 성공');
        router.push('/result');
      } else {
        console.error('건강 데이터 저장 실패:', result.error);
      }
    } catch (error) {
      console.error('결과 저장 중 오류:', error);
    }
  }, [rppgResult, voiceResult, router]);

  const resetMeasurement = useCallback(() => {
    setCurrentStep('ready');
    setError(null);
    setIsProcessing(false);
    setFaceProgress(0);
    setVoiceProgress(0);
    setRppgResult(null);
    setVoiceResult(null);
    
    // 스트림 정리
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // 분석기 정리
    if (rppgAnalyzerRef.current) {
      rppgAnalyzerRef.current.stopAnalysis();
    }
    
    if (voiceAnalyzerRef.current) {
      voiceAnalyzerRef.current.dispose();
    }
  }, []);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (rppgAnalyzerRef.current) {
        rppgAnalyzerRef.current.stopAnalysis();
      }
      if (voiceAnalyzerRef.current) {
        voiceAnalyzerRef.current.dispose();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto">
        <div className="glass-card rounded-2xl p-6 text-center">
          
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white mb-2">건강 측정</h1>
            <p className="text-gray-300">카메라와 마이크를 통해 건강 상태를 측정합니다</p>
          </div>

          {/* Privacy Modal */}
          {showPrivacyModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-md mx-4">
                <h3 className="text-lg font-bold mb-4">개인정보 처리 동의</h3>
                <p className="text-gray-600 mb-4">
                  건강 측정을 위해 카메라와 마이크 접근 권한이 필요합니다.
                  수집된 데이터는 건강 분석 목적으로만 사용됩니다.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setPrivacyConsent(true);
                      setShowPrivacyModal(false);
                      startMeasurement();
                    }}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  >
                    동의
                  </button>
                  <button
                    onClick={() => setShowPrivacyModal(false)}
                    className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                  >
                    거부
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Ready Step */}
          {currentStep === 'ready' && (
            <div>
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🩺</span>
              </div>
              <button
                onClick={() => setShowPrivacyModal(true)}
                className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-8 py-3 rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all duration-300"
              >
                측정 시작하기
              </button>
            </div>
          )}

          {/* Face Scan Step */}
          {currentStep === 'face' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">얼굴 스캔 중...</h2>
              <div className="relative mb-4">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-48 bg-black rounded-lg"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 border-2 border-blue-500 rounded-full"></div>
                </div>
              </div>
              <div className="mb-4">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${faceProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-300 mt-2">{Math.round(faceProgress)}% 완료</p>
              </div>
              <p className="text-gray-300">카메라에 얼굴을 비추세요. 30초 동안 측정합니다.</p>
            </div>
          )}

          {/* Voice Record Step */}
          {currentStep === 'voice' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">음성 녹음 중...</h2>
              <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                <span className="text-4xl">🎤</span>
              </div>
              <div className="mb-4">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${voiceProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-300 mt-2">{Math.round(voiceProgress)}% 완료</p>
              </div>
              <p className="text-gray-300">5초 동안 '아~' 발음을 해주세요.</p>
            </div>
          )}

          {/* Complete Step */}
          {currentStep === 'complete' && (
            <div>
              <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">✅</span>
              </div>
              <h2 className="text-xl font-semibold text-white mb-4">측정 완료!</h2>
              
              {/* rPPG 결과 */}
              {rppgResult && (
                <div className="bg-blue-900/30 rounded-lg p-4 mb-4 text-left">
                  <h3 className="text-lg font-semibold text-blue-300 mb-2">심혈관 건강</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>심박수: <span className="text-white">{rppgResult.heartRate} BPM</span></div>
                    <div>심박변이도: <span className="text-white">{rppgResult.heartRateVariability}ms</span></div>
                    <div>스트레스: <span className="text-white">{rppgResult.stressLevel}%</span></div>
                    <div>신뢰도: <span className="text-white">{rppgResult.confidence}%</span></div>
                  </div>
                </div>
              )}
              
              {/* 음성 분석 결과 */}
              {voiceResult && (
                <div className="bg-green-900/30 rounded-lg p-4 mb-4 text-left">
                  <h3 className="text-lg font-semibold text-green-300 mb-2">음성 건강</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>Jitter: <span className="text-white">{voiceResult.jitter.toFixed(3)}</span></div>
                    <div>Shimmer: <span className="text-white">{voiceResult.shimmer.toFixed(3)}</span></div>
                    <div>HNR: <span className="text-white">{voiceResult.hnr}dB</span></div>
                    <div>스트레스: <span className="text-white">{voiceResult.stressLevel}%</span></div>
                  </div>
                </div>
              )}
              
              <div className="flex gap-2">
                <button
                  onClick={saveResults}
                  className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
                >
                  결과 저장
                </button>
                <button
                  onClick={resetMeasurement}
                  className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
                >
                  다시 측정
                </button>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mt-4 p-3 bg-red-900/30 border border-red-500 rounded text-red-300">
              {error}
            </div>
          )}

          {/* Back Button */}
          {currentStep !== 'ready' && (
            <button
              onClick={resetMeasurement}
              className="mt-4 text-gray-400 hover:text-white transition-colors"
            >
              ← 처음으로 돌아가기
            </button>
          )}
        </div>
      </div>
    </div>
  );
}