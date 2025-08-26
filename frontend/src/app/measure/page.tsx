'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

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

  const FACE_SCAN_DURATION = 30;  // 30초 얼굴 스캔

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
      }
    } catch (err) {
      setError('카메라 접근 권한이 필요합니다.');
      console.error('Camera error:', err);
    }
  }, []);

  // 측정 시작
  const startMeasurement = useCallback(async () => {
    try {
      setCurrentStep('face');
      setError(null);
      setIsProcessing(true);
      
      // 카메라 초기화
      await initializeCamera();
      
      // 30초 후 자동으로 voice 단계로
      setTimeout(() => {
        setCurrentStep('voice');
        // 5초 후 완료
        setTimeout(() => {
          setCurrentStep('complete');
          setIsProcessing(false);
        }, 5000);
      }, 30000);
      
    } catch (err) {
      setError('측정 시작 실패: ' + (err as Error).message);
      setIsProcessing(false);
    }
  }, [initializeCamera]);

  const resetMeasurement = useCallback(() => {
    setCurrentStep('ready');
    setError(null);
    setIsProcessing(false);
    
    // 스트림 정리
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  }, []);

  const goToResults = useCallback(() => {
    router.push('/result');
  }, [router]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const progress = 0; // 임시로 0으로 설정

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md mx-auto">
        <div className="glass-card rounded-2xl p-6 text-center">
          
          {/* Header */}
          <div className="mb-4">
            <h1 className="text-2xl font-orbitron font-bold text-neon-cyan mb-2">엔오건강도우미</h1>
            <p className="text-gray-300 text-sm">안녕하세요, 게스트님</p>
          </div>

          {/* Status Display */}
          <div className="mb-4">
            <h2 id="status-title" className="text-2xl font-bold text-neon-cyan neon-glow">
              {currentStep === 'ready' && '건강 측정 준비'}
              {currentStep === 'face' && '얼굴 분석 중'}
              {currentStep === 'voice' && '음성 분석 중'}
              {currentStep === 'complete' && '분석 완료!'}
            </h2>
            <p id="status-instruction" className="text-gray-300 mt-1">
              {currentStep === 'ready' && '측정을 시작하려면 아래 버튼을 눌러주세요.'}
              {currentStep === 'face' && `가이드라인에 얼굴을 맞춰주세요. (${FACE_SCAN_DURATION}초)`}
              {currentStep === 'voice' && '편안하게 \'아~\' 소리를 내주세요. (5초)'}
              {currentStep === 'complete' && '결과를 확인하고 나만의 사운드트랙을 만들어보세요.'}
            </p>
          </div>

          {/* Visualizer */}
          <div className="relative w-full aspect-square bg-black rounded-lg overflow-hidden mb-4">
            {/* Face Scan Phase */}
            {currentStep === 'face' && (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
                <div className="face-guideline active"></div>
              </>
            )}
            
            {/* Voice Scan Phase */}
            {currentStep === 'voice' && (
              <div className="w-full h-full bg-gray-800 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 text-neon-cyan mx-auto mb-2">🎤</div>
                  <p className="text-neon-cyan">음성 녹음 중...</p>
                </div>
              </div>
            )}
            
            {/* Ready/Complete Phase */}
            {(currentStep === 'ready' || currentStep === 'complete') && (
              <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                <span className="text-gray-500">
                  {currentStep === 'ready' ? '카메라 준비 중...' : '측정 완료!'}
                </span>
              </div>
            )}
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-700/50 rounded-full h-4 mb-6">
            <div 
              className="bg-gradient-to-r from-neon-cyan to-neon-sky h-4 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>

          {/* Control Button */}
          <button 
            onClick={currentStep === 'complete' ? goToResults : () => setShowPrivacyModal(true)}
            disabled={isProcessing}
            className={`w-full font-bold py-4 px-6 rounded-lg transition-all duration-300 shadow-lg text-xl ${
              currentStep === 'complete'
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white'
                : isProcessing
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed opacity-75'
                : 'bg-gradient-to-r from-neon-cyan to-neon-sky hover:from-neon-sky hover:to-neon-cyan text-gray-900 hover:shadow-neon-cyan/50'
            }`}
          >
            {currentStep === 'ready' && '35초 측정 시작하기'}
            {isProcessing && '측정 중...'}
            {currentStep === 'complete' && '결과 보기'}
          </button>

          {/* Reset Button (when measuring) */}
          {isProcessing && (
            <button 
              onClick={resetMeasurement}
              className="w-full mt-3 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-all duration-300"
            >
              측정 중단
            </button>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="fixed top-4 left-4 right-4 bg-red-900/20 border border-red-500/50 rounded-lg p-4 animate-fade-in">
          <div className="flex items-center space-x-2 text-red-400">
            <span className="text-lg">⚠️</span>
            <span className="font-medium">{error}</span>
          </div>
          <button 
            onClick={() => setError(null)} 
            className="text-red-300 hover:text-red-100 text-sm mt-2"
          >
            닫기
          </button>
        </div>
      )}

      {/* 개인정보보호 동의 모달 */}
      {showPrivacyModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-card p-8 max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-2xl font-bold text-neon-cyan mb-6 text-center">
              🛡️ 개인정보보호 동의
            </h3>
            
            <div className="space-y-4 mb-6">
              {/* 필수 동의 항목 */}
              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="modal-required-consent"
                  checked={privacyConsent}
                  onChange={(e) => setPrivacyConsent(e.target.checked)}
                  className="mt-1 w-5 h-5 bg-gray-800 border-gray-600 text-neon-cyan focus:ring-neon-cyan rounded"
                />
                <div className="flex-1">
                  <label htmlFor="modal-required-consent" className="font-medium text-white cursor-pointer">
                    필수 동의 항목
                  </label>
                  <p className="text-sm text-gray-400 mt-1">
                    얼굴 영상, 음성 데이터 수집 및 분석, 측정 결과 저장
                  </p>
                </div>
              </div>
            </div>

            {/* 동의 후 측정 시작 버튼 */}
            <div className="flex space-x-4 justify-center">
              <button
                onClick={() => setShowPrivacyModal(false)}
                className="btn-secondary px-6 py-3"
              >
                취소
              </button>
              <button
                onClick={() => {
                  if (privacyConsent) {
                    setShowPrivacyModal(false);
                    startMeasurement();
                  }
                }}
                disabled={!privacyConsent}
                className={`px-6 py-3 rounded-lg font-bold transition-all duration-300 ${
                  privacyConsent
                    ? 'bg-gradient-to-r from-neon-cyan to-neon-sky hover:from-neon-sky hover:to-neon-cyan text-gray-900 shadow-lg hover:shadow-neon-cyan/50'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
              >
                {privacyConsent ? '동의하고 측정 시작' : '필수 동의 후 측정 가능'}
              </button>
            </div>

            {/* 개인정보보호 관련 안내 */}
            <p className="text-xs text-gray-500 text-center mt-4">
              모든 데이터는 비식별 처리되어 안전하게 관리됩니다.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}