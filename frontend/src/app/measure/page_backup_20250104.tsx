'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { RPPGAnalyzer, RPPGResult } from '@/lib/rppgAnalyzer';
import { VoiceAnalyzer, VoiceAnalysisResult } from '@/lib/voiceAnalyzer';
import { saveHealthData } from '@/lib/firebase';
import AIChat from '@/components/AIChat';
import AudioWaveform from '@/components/AudioWaveform';
import HealingMusic from '@/components/HealingMusic';
import HealthDashboard from '@/components/HealthDashboard';
import HealthArtNFT from '@/components/HealthArtNFT';

export default function MeasurePage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<'ready' | 'face' | 'voice' | 'complete'>('ready');
  const [error, setError] = useState<string | null>(null);
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [privacyConsent, setPrivacyConsent] = useState(false);
  const [cameraPermission, setCameraPermission] = useState<boolean>(false);
  const [microphonePermission, setMicrophonePermission] = useState<boolean>(false);
  const [showAIChat, setShowAIChat] = useState(false);
  const [showHealingMusic, setShowHealingMusic] = useState(false);
  const [showHealthDashboard, setShowHealthDashboard] = useState(false);
  const [showHealthArtNFT, setShowHealthArtNFT] = useState(false);
  const [isVoiceRecording, setIsVoiceRecording] = useState(false);
  const [audioWaveformData, setAudioWaveformData] = useState<Float32Array | null>(null);
  
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

  // 권한 확인
  const checkPermissions = useCallback(async () => {
    try {
      // 카메라 권한 확인
      const cameraPermission = await navigator.permissions.query({ name: 'camera' as PermissionName });
      setCameraPermission(cameraPermission.state === 'granted');
      
      // 마이크 권한 확인
      const microphonePermission = await navigator.permissions.query({ name: 'microphone' as PermissionName });
      setMicrophonePermission(microphonePermission.state === 'granted');
      
      console.log('Camera permission:', cameraPermission.state);
      console.log('Microphone permission:', microphonePermission.state);
    } catch {
      console.log('Permission check not supported, will request during use');
    }
  }, []);

  // 카메라 초기화 (모바일 최적화)
  const initializeCamera = useCallback(async () => {
    try {
      setError(null);
      
      // 모바일 환경에서 최적화된 비디오 설정
      const constraints = {
        video: {
          width: { ideal: 640, max: 1280 },
          height: { ideal: 480, max: 720 },
          frameRate: { ideal: 30, max: 60 },
          facingMode: 'user', // 전면 카메라 사용
          aspectRatio: { ideal: 4/3 }
        },
        audio: false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        
        // 비디오 로드 완료 대기
        await new Promise((resolve) => {
          if (videoRef.current) {
            videoRef.current.onloadedmetadata = resolve;
          }
        });
        
        // rPPG 분석기 초기화
        rppgAnalyzerRef.current = new RPPGAnalyzer(videoRef.current);
        rppgAnalyzerRef.current.onResult((result) => {
          setRppgResult(result);
          console.log('rPPG 분석 완료:', result);
        });
        
        setCameraPermission(true);
        console.log('카메라 초기화 성공');
      }
    } catch (err: unknown) {
      console.error('Camera initialization error:', err);
      
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('카메라 접근 권한이 거부되었습니다. 브라우저 설정에서 카메라 권한을 허용해주세요.');
        } else if (err.name === 'NotFoundError') {
          setError('카메라를 찾을 수 없습니다. 카메라가 연결되어 있는지 확인해주세요.');
        } else if (err.name === 'NotSupportedError') {
          setError('이 브라우저는 카메라 기능을 지원하지 않습니다.');
        } else if (err.name === 'NotReadableError') {
          setError('카메라가 다른 애플리케이션에서 사용 중입니다. 다른 앱을 종료하고 다시 시도해주세요.');
        } else {
          setError(`카메라 초기화 오류: ${err.message}`);
        }
      } else {
        setError('카메라 초기화 중 알 수 없는 오류가 발생했습니다.');
      }
    }
  }, []);

  // 음성 분석기 초기화 (모바일 최적화)
  const initializeVoiceAnalyzer = useCallback(async () => {
    try {
      // 마이크 권한 요청
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100,
          channelCount: 1
        }
      });
      
      voiceAnalyzerRef.current = new VoiceAnalyzer(stream);
      voiceAnalyzerRef.current.onResult((result) => {
        setVoiceResult(result);
        console.log('음성 분석 완료:', result);
      });
      setMicrophonePermission(true);
      console.log('음성 분석기 초기화 성공');
      
      // 스트림을 정리하지 않고 VoiceAnalyzer에서 관리
    } catch (err: unknown) {
      console.error('Microphone initialization error:', err);
      
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('마이크 접근 권한이 거부되었습니다. 브라우저 설정에서 마이크 권한을 허용해주세요.');
        } else if (err.name === 'NotFoundError') {
          setError('마이크를 찾을 수 없습니다. 마이크가 연결되어 있는지 확인해주세요.');
        } else if (err.name === 'NotReadableError') {
          setError('마이크가 다른 애플리케이션에서 사용 중입니다. 다른 앱을 종료하고 다시 시도해주세요.');
        } else {
          setError(`마이크 초기화 오류: ${err.message}`);
        }
      } else {
        setError('마이크 초기화 중 알 수 없는 오류가 발생했습니다.');
      }
    }
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
      setFaceProgress(0);
      setVoiceProgress(0);
      
      console.log('카메라 초기화 시작...');
      
      // 카메라 초기화
      await initializeCamera();
      
      if (!rppgAnalyzerRef.current) {
        throw new Error('카메라 분석기 초기화 실패');
      }
      
      console.log('rPPG 분석 시작...');
      
      // rPPG 분석 시작
      rppgAnalyzerRef.current.startAnalysis();
      
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
      
      // 얼굴 스캔 완료 후 음성 측정으로 이동
      setTimeout(async () => {
        try {
          setCurrentStep('voice');
          setFaceProgress(100);
          
          console.log('음성 분석기 초기화 시작...');
          
          // 음성 분석기 초기화
          await initializeVoiceAnalyzer();
          
          if (!voiceAnalyzerRef.current) {
            throw new Error('음성 분석기 초기화 실패');
          }
          
          console.log('음성 녹음 시작...');
          
          // 음성 녹음 시작
          setIsVoiceRecording(true);
          await voiceAnalyzerRef.current.startRecording();
          
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
          
          // 음성 녹음 완료
          setTimeout(() => {
            if (voiceAnalyzerRef.current) {
              voiceAnalyzerRef.current.stopRecording();
            }
            setIsVoiceRecording(false);
            setVoiceProgress(100);
            setCurrentStep('complete');
            console.log('측정 완료');
          }, VOICE_RECORD_DURATION);
          
        } catch (voiceError) {
          console.error('음성 측정 오류:', voiceError);
          setError(`음성 측정 중 오류가 발생했습니다: ${voiceError instanceof Error ? voiceError.message : '알 수 없는 오류'}`);
          setCurrentStep('face'); // 얼굴 측정 단계로 되돌리기
        }
        
      }, FACE_SCAN_DURATION);
      
    } catch (err) {
      console.error('Measurement error:', err);
      setError(`측정 중 오류가 발생했습니다: ${err instanceof Error ? err.message : '알 수 없는 오류'}`);
      setCurrentStep('ready'); // 준비 단계로 되돌리기
    }
  }, [privacyConsent, initializeCamera, initializeVoiceAnalyzer]);

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
      if (result) {
        console.log('건강 데이터 저장 성공:', result);
        router.push('/result');
      } else {
        console.error('건강 데이터 저장 실패');
      }
    } catch (error) {
      console.error('결과 저장 중 오류:', error);
    }
  }, [rppgResult, voiceResult, router]);

  const resetMeasurement = useCallback(() => {
    setCurrentStep('ready');
    setError(null);
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
      voiceAnalyzerRef.current.stopRecording();
    }
  }, []);

  // 오디오 파형 업데이트
  const handleWaveformUpdate = useCallback((data: Float32Array) => {
    setAudioWaveformData(data);
  }, []);

  // AI 분석용 건강 데이터
  const getHealthDataForAI = useCallback(() => {
    const healthData: any = {};
    
    if (rppgResult) {
      healthData.rppg = {
        heartRate: rppgResult.heartRate,
        stressIndex: rppgResult.stressIndex,
        confidence: rppgResult.confidence,
        quality: rppgResult.quality
      };
    }
    
    if (voiceResult) {
      healthData.voice = {
        pitch: voiceResult.pitch,
        clarity: voiceResult.clarity,
        emotion: voiceResult.emotion,
        quality: voiceResult.quality
      };
    }
    
    // 실제 측정 데이터 기반 융합 정보
    healthData.fusion = {
      digitalTemperament: "실제 측정 기반",
      overallScore: rppgResult && voiceResult ? 
        Math.round((rppgResult.confidence + voiceResult.confidence) * 50) : 0,
      recommendations: [
        rppgResult && rppgResult.stressIndex > 0.7 ? "현재 스트레스 수준이 높습니다" : "스트레스 수준이 양호합니다",
        voiceResult && voiceResult.clarity < 0.6 ? "음성 명확도 개선이 필요합니다" : "음성 상태가 양호합니다",
        "규칙적인 건강 측정을 권장합니다"
      ]
    };
    
    healthData.timestamp = new Date().toISOString();
    healthData.device = navigator.userAgent;
    
    return healthData;
  }, [rppgResult, voiceResult]);

  // 컴포넌트 마운트 시 권한 확인
  useEffect(() => {
    checkPermissions();
  }, [checkPermissions]);

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
        voiceAnalyzerRef.current.stopRecording();
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            건강 측정
          </h1>
          <p className="text-gray-300">
            카메라와 마이크를 사용하여 건강 상태를 측정합니다
          </p>
        </div>

        {/* 메인 측정 영역 */}
        <div className="max-w-4xl mx-auto">
          {/* 권한 상태 표시 */}
          <div className="bg-gray-800/50 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-semibold mb-3 text-cyan-300">권한 상태</h3>
            <div className="space-y-2">
              <div className={`permission-status ${cameraPermission ? 'permission-granted' : 'permission-pending'}`}>
                <span>{cameraPermission ? '✅' : '⏳'}</span>
                <span>카메라 권한: {cameraPermission ? '허용됨' : '대기 중'}</span>
              </div>
              <div className={`permission-status ${microphonePermission ? 'permission-granted' : 'permission-pending'}`}>
                <span>{microphonePermission ? '✅' : '⏳'}</span>
                <span>마이크 권한: {microphonePermission ? '허용됨' : '대기 중'}</span>
              </div>
            </div>
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

          {/* Face Scan Step - 개선된 UI */}
          {currentStep === 'face' && (
            <div className="text-center">
              <h2 className="text-2xl font-bold text-white mb-6">얼굴 스캔 중...</h2>
              
              {/* 확대된 카메라 화면 */}
              <div className="relative mb-6 mx-auto" style={{ width: '90vw', maxWidth: '500px', height: '70vh', maxHeight: '600px' }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full bg-black rounded-2xl object-cover"
                />
                
                {/* 스캔 라인 애니메이션 */}
                <div className="absolute inset-0 pointer-events-none">
                  <div className="scan-line"></div>
                </div>
                
                {/* 얼굴 가이드라인 */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="face-outline"></div>
                </div>
                
                {/* 진행률 표시 */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-black/70 rounded-full p-3">
                    <div className="text-white font-bold text-lg">{Math.round(faceProgress)}%</div>
                  </div>
                </div>
              </div>
              
              {/* 개선된 진행률 바 */}
              <div className="mb-6 max-w-md mx-auto">
                <div className="progress-bar bg-gray-700 rounded-full h-3 overflow-hidden">
                  <div 
                    className="progress-fill bg-gradient-to-r from-blue-500 to-cyan-500 h-full transition-all duration-300 rounded-full"
                    style={{ width: `${faceProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-300 mt-2">측정 진행률</p>
              </div>
              
              {/* 사용자 안내 */}
              <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4 max-w-md mx-auto">
                <p className="text-blue-300 font-medium">카메라에 얼굴을 비추세요</p>
                <p className="text-blue-200 text-sm mt-1">30초 동안 측정합니다</p>
              </div>
            </div>
          )}

          {/* Voice Record Step */}
          {currentStep === 'voice' && (
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">음성 녹음 중...</h2>
              
              {/* 실시간 오디오 파형 시각화 */}
              <div className="mb-6">
                <AudioWaveform
                  isRecording={isVoiceRecording}
                  onWaveformUpdate={handleWaveformUpdate}
                  width={350}
                  height={150}
                />
              </div>
              
              <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 voice-recording">
                <span className="text-4xl">🎤</span>
              </div>
              <div className="mb-4">
                <div className="progress-bar">
                  <div 
                    className="progress-fill bg-green-500"
                    style={{ width: `${voiceProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-300 mt-2">{Math.round(voiceProgress)}% 완료</p>
              </div>
              <p className="text-gray-300">5초 동안 "아~" 발음을 해주세요.</p>
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
                <div className="result-card">
                  <h3 className="text-lg font-semibold text-blue-300 mb-2">심혈관 건강</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>심박수: <span className="text-white">{rppgResult.heartRate} BPM</span></div>
                    <div>스트레스 지수: <span className="text-white">{(rppgResult.stressIndex * 100).toFixed(1)}%</span></div>
                    <div>신뢰도: <span className="text-white">{(rppgResult.confidence * 100).toFixed(1)}%</span></div>
                    <div>품질: <span className="text-white">{rppgResult.quality}</span></div>
                    <div>프레임 수: <span className="text-white">{rppgResult.frameCount}</span></div>
                  </div>
                </div>
              )}
              
              {/* 음성 분석 결과 */}
              {voiceResult && (
                <div className="result-card">
                  <h3 className="text-lg font-semibold text-green-300 mb-2">음성 건강</h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>피치: <span className="text-white">{voiceResult.pitch} Hz</span></div>
                    <div>볼륨: <span className="text-white">{voiceResult.volume}</span></div>
                    <div>명확도: <span className="text-white">{(voiceResult.clarity * 100).toFixed(1)}%</span></div>
                    <div>감정: <span className="text-white">{voiceResult.emotion}</span></div>
                    <div>기본 주파수: <span className="text-white">{voiceResult.frequency} Hz</span></div>
                    <div>지터: <span className="text-white">{voiceResult.jitter}</span></div>
                    <div>쉬머: <span className="text-white">{voiceResult.shimmer}%</span></div>
                    <div>HNR: <span className="text-white">{voiceResult.hnr} dB</span></div>
                    <div>품질: <span className="text-white">{voiceResult.quality}</span></div>
                  </div>
                </div>
              )}
              
              <div className="button-group">
                <button
                  onClick={() => setShowAIChat(true)}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
                >
                  🤖 AI 건강 상담
                </button>
                <button
                  onClick={() => setShowHealingMusic(true)}
                  className="bg-gradient-to-r from-green-500 to-blue-500 text-white px-6 py-2 rounded hover:from-green-600 hover:to-blue-600 transition-all duration-300"
                >
                  🎵 치유 음악
                </button>
                <button
                  onClick={() => setShowHealthDashboard(true)}
                  className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-2 rounded hover:from-blue-600 hover:to-cyan-600 transition-all duration-300"
                >
                  📊 건강 리포트
                </button>
                <button
                  onClick={() => setShowHealthArtNFT(true)}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded hover:from-purple-600 hover:to-pink-600 transition-all duration-300"
                >
                  🎨 NFT 아트
                </button>
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

      {/* AI Chat Modal */}
      {showAIChat && (
        <AIChat
          healthData={getHealthDataForAI()}
          maxQuestions={10}
          onClose={() => setShowAIChat(false)}
        />
      )}

      {/* Healing Music Modal */}
      {showHealingMusic && (
        <HealingMusic
          healthData={getHealthDataForAI()}
          onClose={() => setShowHealingMusic(false)}
        />
      )}

      {/* Health Dashboard Modal */}
      {showHealthDashboard && (
        <HealthDashboard
          onClose={() => setShowHealthDashboard(false)}
        />
      )}

      {/* Health Art NFT Modal */}
      {showHealthArtNFT && (
        <HealthArtNFT
          healthData={getHealthDataForAI()}
          onClose={() => setShowHealthArtNFT(false)}
        />
      )}
    </div>
  );
}