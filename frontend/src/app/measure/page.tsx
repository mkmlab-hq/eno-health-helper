'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Camera, Mic, Activity } from 'lucide-react';

interface HealthResult {
  rppg_result: {
    heart_rate: number;
    hrv: number;
    stress_level: string;
    confidence: number;
  };
  voice_result: {
    f0: number;
    jitter: number;
    shimmer: number;
    hnr: number;
    confidence: number;
  };
  health_score: number;
  measurement_id: string;
}

export default function MeasurePage() {
  const [isMeasuring, setIsMeasuring] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentPhase, setCurrentPhase] = useState<'ready' | 'face' | 'voice' | 'complete'>('ready');
  const [error, setError] = useState<string | null>(null);
  const [healthResult, setHealthResult] = useState<HealthResult | null>(null);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [privacyConsent, setPrivacyConsent] = useState({ requiredConsent: false, optionalConsent: false });
  
  // 실제 미디어 스트림 관련 상태
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [audioStream, setAudioStream] = useState<MediaStream | null>(null);
  const [isCameraReady, setIsCameraReady] = useState(false);
  const [isMicrophoneReady, setIsMicrophoneReady] = useState(false);
  
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const measurementIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  // 실제 데이터 수집용
  const videoFramesRef = useRef<ImageData[]>([]);
  const audioChunksRef = useRef<Blob[]>([]);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const TOTAL_DURATION = 35;
  const FACE_SCAN_DURATION = 30;  // 30초 얼굴 스캔
  const VOICE_SCAN_DURATION = 5;  // 5초 음성 측정

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
      
      setVideoStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          setIsCameraReady(true);
        };
      }
    } catch (err) {
      setError('카메라 접근 권한이 필요합니다.');
      console.error('Camera error:', err);
    }
  }, []);

  // 마이크 초기화
  const initializeMicrophone = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 48000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      setAudioStream(stream);
      setIsMicrophoneReady(true);
    } catch (err) {
      setError('마이크 접근 권한이 필요합니다.');
      console.error('Microphone error:', err);
    }
  }, []);

  // 비디오 프레임 캡처
  const captureVideoFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    videoFramesRef.current.push(imageData);
  }, []);

  // 오디오 녹음 시작
  const startAudioRecording = useCallback(() => {
    if (!audioStream) return;
    
    const mediaRecorder = new MediaRecorder(audioStream, {
      mimeType: 'audio/webm;codecs=opus'
    });
    
    mediaRecorderRef.current = mediaRecorder;
    audioChunksRef.current = [];
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunksRef.current.push(event.data);
      }
    };
    
    mediaRecorder.start(100); // 100ms마다 청크 수집
  }, [audioStream]);

  // 오디오 녹음 중지
  const stopAudioRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // rPPG 분석 API 호출
  const analyzeRPPG = useCallback(async (frames: ImageData[]) => {
    try {
      // 프레임을 base64로 변환
      const frameData = frames.map(frame => {
        const canvas = document.createElement('canvas');
        canvas.width = frame.width;
        canvas.height = frame.height;
        const ctx = canvas.getContext('2d');
        ctx?.putImageData(frame, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
      });

      const response = await fetch('http://localhost:8000/api/rppg/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frames: frameData,
          frame_rate: 30
        })
      });

      if (!response.ok) {
        throw new Error('rPPG 분석 실패');
      }

      return await response.json();
    } catch (err) {
      console.error('rPPG analysis error:', err);
      throw err;
    }
  }, []);

  // 음성 분석 API 호출
  const analyzeVoice = useCallback(async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice_recording.webm');

      const response = await fetch('http://localhost:8000/api/voice/analyze', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('음성 분석 실패');
      }

      return await response.json();
    } catch (err) {
      console.error('Voice analysis error:', err);
      throw err;
    }
  }, []);

  // 건강 점수 계산 API 호출
  const calculateHealthScore = useCallback(async (rppgData: any, voiceData: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/health/calculate-score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          rppg_result: rppgData,
          voice_result: voiceData
        })
      });

      if (!response.ok) {
        throw new Error('건강 점수 계산 실패');
      }

      return await response.json();
    } catch (err) {
      console.error('Health score calculation error:', err);
      throw err;
    }
  }, []);

  // 실제 측정 시작
  const startMeasurement = useCallback(async () => {
    try {
      setIsMeasuring(true);
      setElapsedTime(0);
      setCurrentPhase('face');
      setError(null);
      
      // 데이터 초기화
      videoFramesRef.current = [];
      audioChunksRef.current = [];

      // 카메라와 마이크 초기화
      await initializeCamera();
      await initializeMicrophone();

      measurementIntervalRef.current = setInterval(() => {
        setElapsedTime(prev => {
          const newTime = prev + 1;
          
          if (newTime <= FACE_SCAN_DURATION) {
            setCurrentPhase('face');
            // 얼굴 프레임 캡처
            captureVideoFrame();
          } else if (newTime <= TOTAL_DURATION) {
            if (newTime === FACE_SCAN_DURATION + 1) {
              setCurrentPhase('voice');
              // 음성 녹음 시작
              startAudioRecording();
            }
          } else {
            setCurrentPhase('complete');
            return prev;
          }
          
          return newTime;
        });
      }, 1000);
    } catch (err) {
      setError('측정 시작 실패: ' + (err as Error).message);
      setIsMeasuring(false);
    }
  }, [initializeCamera, initializeMicrophone, captureVideoFrame, startAudioRecording]);

  // 측정 완료 및 결과 분석
  const finishMeasurement = useCallback(async () => {
    try {
      if (measurementIntervalRef.current) {
        clearInterval(measurementIntervalRef.current);
        measurementIntervalRef.current = null;
      }

      // 음성 녹음 중지
      stopAudioRecording();

      // 결과 분석
      const rppgResult = await analyzeRPPG(videoFramesRef.current);
      const voiceResult = await analyzeVoice(new Blob(audioChunksRef.current));
      const healthScore = await calculateHealthScore(rppgResult, voiceResult);

      setHealthResult({
        rppg_result: rppgResult,
        voice_result: voiceResult,
        health_score: healthScore.health_score,
        measurement_id: healthScore.measurement_id
      });

      setIsMeasuring(false);
      setCurrentPhase('complete');
    } catch (err) {
      setError('측정 완료 실패: ' + (err as Error).message);
      setIsMeasuring(false);
    }
  }, [stopAudioRecording, analyzeRPPG, analyzeVoice, calculateHealthScore]);

  const resetMeasurement = useCallback(() => {
    setIsMeasuring(false);
    setElapsedTime(0);
    setCurrentPhase('ready');
    setError(null);
    setHealthResult(null);
    
    // 스트림 정리
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
      setVideoStream(null);
    }
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      setAudioStream(null);
    }
    
    setIsCameraReady(false);
    setIsMicrophoneReady(false);
    
    if (measurementIntervalRef.current) {
      clearInterval(measurementIntervalRef.current);
      measurementIntervalRef.current = null;
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, [videoStream, audioStream]);

  const goToResults = useCallback(() => {
    router.push('/result');
  }, [router]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (measurementIntervalRef.current) {
        clearInterval(measurementIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
      }
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [videoStream, audioStream]);

  // 자동 완료
  useEffect(() => {
    if (elapsedTime >= TOTAL_DURATION) {
      finishMeasurement();
    }
  }, [elapsedTime, finishMeasurement]);

  const progress = (elapsedTime / TOTAL_DURATION) * 100;

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
              {currentPhase === 'ready' && '건강 측정 준비'}
              {currentPhase === 'face' && '얼굴 분석 중'}
              {currentPhase === 'voice' && '음성 분석 중'}
              {currentPhase === 'complete' && '분석 완료!'}
            </h2>
            <p id="status-instruction" className="text-gray-300 mt-1">
              {currentPhase === 'ready' && '측정을 시작하려면 아래 버튼을 눌러주세요.'}
              {currentPhase === 'face' && `가이드라인에 얼굴을 맞춰주세요. (${FACE_SCAN_DURATION - elapsedTime}초)`}
              {currentPhase === 'voice' && `편안하게 '아~' 소리를 내주세요. (${TOTAL_DURATION - elapsedTime}초)`}
              {currentPhase === 'complete' && '결과를 확인하고 나만의 사운드트랙을 만들어보세요.'}
            </p>
          </div>

          {/* Visualizer */}
          <div className="relative w-full aspect-square bg-black rounded-lg overflow-hidden mb-4">
            {/* Face Scan Phase */}
            {currentPhase === 'face' && (
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
                <div className="face-guideline active"></div>
                {!isCameraReady && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <span className="text-neon-cyan">카메라 초기화 중...</span>
                  </div>
                )}
              </>
            )}
            
            {/* Voice Scan Phase */}
            {currentPhase === 'voice' && (
              <div className="w-full h-full bg-gray-800 flex items-center justify-center">
                <div className="text-center">
                  <Mic className="w-16 h-16 text-neon-cyan mx-auto mb-2" />
                  <p className="text-neon-cyan">음성 녹음 중...</p>
                  <p className="text-sm text-gray-400 mt-1">
                    {isMicrophoneReady ? '마이크 준비 완료' : '마이크 초기화 중...'}
                  </p>
                </div>
              </div>
            )}
            
            {/* Ready/Complete Phase */}
            {(currentPhase === 'ready' || currentPhase === 'complete') && (
              <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
                <span className="text-gray-500">
                  {currentPhase === 'ready' ? '카메라 준비 중...' : '측정 완료!'}
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
            onClick={currentPhase === 'complete' ? goToResults : () => setShowConsentModal(true)}
            disabled={isMeasuring}
            className={`w-full font-bold py-4 px-6 rounded-lg transition-all duration-300 shadow-lg text-xl ${
              currentPhase === 'complete'
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white'
                : isMeasuring
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed opacity-75'
                : 'bg-gradient-to-r from-neon-cyan to-neon-sky hover:from-neon-sky hover:to-neon-cyan text-gray-900 hover:shadow-neon-cyan/50'
            }`}
          >
            {currentPhase === 'ready' && '35초 측정 시작하기'}
            {isMeasuring && '측정 중...'}
            {currentPhase === 'complete' && '결과 보기'}
          </button>

          {/* Reset Button (when measuring) */}
          {isMeasuring && (
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
      {showConsentModal && (
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
                  checked={privacyConsent.requiredConsent}
                  onChange={(e) => setPrivacyConsent(prev => ({ ...prev, requiredConsent: e.target.checked }))}
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
              
              {/* 선택 동의 항목 */}
              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="modal-optional-consent"
                  checked={privacyConsent.optionalConsent}
                  onChange={(e) => setPrivacyConsent(prev => ({ ...prev, optionalConsent: e.target.checked }))}
                  className="mt-1 w-5 h-5 bg-gray-800 border-gray-600 text-neon-cyan focus:ring-neon-cyan rounded"
                />
                <div className="flex-1">
                  <label htmlFor="modal-optional-consent" className="font-medium text-white cursor-pointer">
                    선택 동의 항목
                  </label>
                  <p className="text-sm text-gray-400 mt-1">
                    개인 맞춤 건강 조언, 서비스 개선을 위한 데이터 활용
                  </p>
                </div>
              </div>
            </div>

            {/* 동의 후 측정 시작 버튼 */}
            <div className="flex space-x-4 justify-center">
              <button
                onClick={() => setShowConsentModal(false)}
                className="btn-secondary px-6 py-3"
              >
                취소
              </button>
              <button
                onClick={() => {
                  if (privacyConsent.requiredConsent) {
                    setShowConsentModal(false);
                    startMeasurement();
                  }
                }}
                disabled={!privacyConsent.requiredConsent}
                className={`px-6 py-3 rounded-lg font-bold transition-all duration-300 ${
                  privacyConsent.requiredConsent
                    ? 'bg-gradient-to-r from-neon-cyan to-neon-sky hover:from-neon-sky hover:to-neon-cyan text-gray-900 shadow-lg hover:shadow-neon-cyan/50'
                    : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                }`}
              >
                {privacyConsent.requiredConsent ? '동의하고 측정 시작' : '필수 동의 후 측정 가능'}
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