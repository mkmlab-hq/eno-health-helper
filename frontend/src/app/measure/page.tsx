'use client';

import { useState, useRef, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
// import { useAuth } from '@/context/AuthContext'; // 인증 체크 제거
import { Camera, Mic, Activity, LogOut, Play, Pause, RotateCcw } from 'lucide-react';

type MeasurementStep = 'start' | 'face' | 'voice' | 'analyzing' | 'complete';

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
  const [currentStep, setCurrentStep] = useState<MeasurementStep>('start');
  const [isRecording, setIsRecording] = useState(false);
  const [faceData, setFaceData] = useState<Blob | null>(null);
  const [voiceData, setVoiceData] = useState<Blob | null>(null);
  const [progress, setProgress] = useState(0);
  const [healthResult, setHealthResult] = useState<HealthResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  // const { currentUser, logout } = useAuth(); // 인증 체크 제거
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // 로그아웃 함수 제거 (인증 없이 사용)
  // const handleLogout = async () => {
  //   try {
  //     await logout();
  //     router.push('/login');
  //   } catch (error) {
  //     console.error('Logout failed:', error);
  //   }
  // };

  const startFaceMeasurement = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      let retry = 0;
      const assignStream = () => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
          setCurrentStep('face');
        } else if (retry < 10) {
          retry++;
          setTimeout(assignStream, 100);
        }
      };
      assignStream();
    } catch (error) {
      console.error('Camera access failed:', error);
      setError('카메라 접근에 실패했습니다.');
    }
  }, []);

  const captureFace = useCallback(() => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0);
        canvas.toBlob((blob) => {
          if (blob) {
            setFaceData(blob);
            setCurrentStep('voice');
          }
        }, 'image/jpeg');
      }
    } else {
      setError('카메라가 정상적으로 연결되지 않았습니다. 새로고침 후 다시 시도해 주세요.');
    }
  }, []);

  const startVoiceMeasurement = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setVoiceData(audioBlob);
        setCurrentStep('analyzing');
        performHealthAnalysis();
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone access failed:', error);
    }
  }, []);

  const stopVoiceMeasurement = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const performHealthAnalysis = async () => {
    if (!faceData || !voiceData) { // 인증 체크 제거
      console.error('Required data missing for analysis');
      return;
    }

    try {
      setProgress(0);
      
      // 진행률 시뮬레이션
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + Math.random() * 15;
        });
      }, 200);

      // Firebase 연동 백엔드 API 호출
      const formData = new FormData();
      formData.append('video_file', faceData, 'face_video.mp4');
      formData.append('audio_file', voiceData, 'voice_audio.wav');
      // formData.append('user_id', currentUser.uid); // 인증 체크 제거

      // 백엔드 서버로 직접 요청
      const response = await fetch('http://localhost:8001/api/v1/measure/combined', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`API 호출 실패: ${response.status} - ${errorData.detail || '알 수 없는 오류'}`);
      }

      const result = await response.json();
      setHealthResult(result);
      setProgress(100);

      // 분석 완료 후 결과 페이지로
      setTimeout(() => {
        setCurrentStep('complete');
      }, 500);

    } catch (error) {
      console.error('Health analysis failed:', error);
      setProgress(100);
      
      // 사용자 친화적 에러 메시지
      let errorMessage = '건강 분석 중 오류가 발생했습니다.';
      if (error instanceof Error) {
        if (error.message.includes('API 호출 실패')) {
          errorMessage = '백엔드 서버 연결에 실패했습니다. 서버 상태를 확인해주세요.';
        } else if (error.message.includes('Required data missing')) {
          errorMessage = '필요한 데이터가 누락되었습니다. 다시 측정해주세요.';
        }
      }
      
      // 에러 상태 설정 (UI에서 표시)
      setError(errorMessage);
    }
  };

  const resetMeasurement = () => {
    setCurrentStep('start');
    setFaceData(null);
    setVoiceData(null);
    setProgress(0);
    setIsRecording(false);
  };

  const goToResults = useCallback(() => {
    router.push('/result');
  }, [router]);

  // 인증 체크 제거
  // if (!currentUser) {
  //   return (
  //     <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
  //       <div className="text-center">
  //         <h1 className="text-2xl text-red-400 mb-4">접근 권한이 없습니다</h1>
  //         <button onClick={() => router.push('/login')} className="btn-primary">
  //           로그인하기
  //         </button>
  //       </div>
  //     </div>
  //   );
  // }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Header */}
      <header className="glass-card m-4 p-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-orbitron font-bold neon-text">엔오건강도우미</h1>
          <p className="text-gray-300 text-sm">안녕하세요, {/* {currentUser.email}님 */} 게스트님</p>
        </div>
        <button onClick={() => router.push('/login')} className="btn-secondary flex items-center space-x-2">
          <LogOut className="w-4 h-4" />
          <span>로그아웃</span>
        </button>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto p-4">
        {/* 에러 메시지 표시 */}
        {error && (
          <div className="glass-card p-4 mb-4 bg-red-900/20 border border-red-500/50 animate-fade-in">
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

        {currentStep === 'start' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-3xl font-orbitron font-bold neon-text mb-6">
              고요 속의 메아리
            </h2>
            <p className="text-gray-300 mb-8 text-lg">
              얼굴과 음성을 통해 정확한 건강 상태를 분석합니다<br/>
              <span className="text-neon-cyan font-medium">따뜻한 기술, 직관적인 건강</span>
            </p>
            <div className="mb-6 p-4 bg-neon-cyan/10 rounded-lg border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                💡 <strong>측정 방법:</strong><br/>
                • 얼굴 측정: 카메라에 정면 응시 (30초)<br/>
                • 음성 측정: "아~" 소리 5초간 지속<br/>
                • AI 분석: 복용 전후 비교 가능
              </p>
            </div>
            <button onClick={startFaceMeasurement} className="btn-primary text-xl px-8 py-4">
              <Camera className="w-6 h-6 mr-2 inline" />
              측정 시작하기
            </button>
          </div>
        )}

        {currentStep === 'face' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              얼굴 측정 단계
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">카메라에 얼굴을 비추세요 (30초)</span><br/>
              정면을 바라보고 정지 상태를 유지해주세요
            </p>
            
            <div className="relative max-w-md mx-auto mb-6">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full rounded-lg border-2 border-neon-cyan"
              />
              <div className="absolute inset-0 border-4 border-neon-cyan rounded-lg animate-pulse-slow"></div>
              <div className="absolute top-2 right-2 bg-neon-cyan/80 text-black px-2 py-1 rounded text-sm font-medium">
                RPPG 측정
              </div>
            </div>

            <div className="mb-4 p-3 bg-neon-cyan/10 rounded border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                🔍 <strong>측정 중:</strong> 미세한 색상 변화를 분석하여 심박수와 스트레스 수준을 측정합니다
              </p>
            </div>

            <div className="flex space-x-4 justify-center">
              <button onClick={captureFace} className="btn-primary">
                <Camera className="w-5 h-5 mr-2" />
                촬영하기
              </button>
              <button onClick={resetMeasurement} className="btn-secondary">
                <RotateCcw className="w-5 h-5 mr-2" />
                다시 시작
              </button>
            </div>
          </div>
        )}

        {currentStep === 'voice' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              음성 측정 단계
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">5초 동안 '아~' 발음을 해주세요</span><br/>
              마이크에 명확하게 소리를 내주세요
            </p>
            
            <div className="mb-6">
              <div className="w-24 h-24 mx-auto bg-glass rounded-full flex items-center justify-center border-2 border-neon-cyan">
                <Mic className={`w-12 h-12 ${isRecording ? 'text-red-400 animate-pulse' : 'text-neon-cyan'}`} />
              </div>
              {isRecording && (
                <div className="mt-2 text-red-400 text-sm animate-pulse">
                  🎤 녹음 중... (5초)
                </div>
              )}
            </div>

            <div className="mb-4 p-3 bg-neon-cyan/10 rounded border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                🎵 <strong>음성 분석:</strong> Jitter, Shimmer 등 음성 품질 지표를 통해 건강 상태를 평가합니다
              </p>
            </div>

            <div className="flex space-x-4 justify-center">
              {!isRecording ? (
                <button onClick={startVoiceMeasurement} className="btn-primary">
                  <Play className="w-5 h-5 mr-2" />
                  녹음 시작
                </button>
              ) : (
                <button onClick={stopVoiceMeasurement} className="btn-secondary">
                  <Pause className="w-5 h-5 mr-2" />
                  녹음 중지
                </button>
              )}
              <button onClick={resetMeasurement} className="btn-secondary">
                <RotateCcw className="w-5 h-5 mr-2" />
                다시 시작
              </button>
            </div>
          </div>
        )}

        {currentStep === 'analyzing' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              AI 분석 중...
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">따뜻한 기술</span>이 건강 데이터를 분석하고 있습니다<br/>
              잠시만 기다려주세요
            </p>
            
            <div className="mb-6">
              <div className="w-24 h-24 mx-auto bg-glass rounded-full flex items-center justify-center border-2 border-neon-cyan">
                <Activity className="w-12 h-12 text-neon-cyan animate-pulse" />
              </div>
            </div>

            <div className="w-full bg-gray-700 rounded-full h-3 mb-4">
              <div 
                className="bg-gradient-to-r from-neon-cyan to-neon-sky h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-neon-cyan font-medium">{Math.round(progress)}%</p>
            
            <div className="mt-4 p-3 bg-neon-cyan/10 rounded border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                🧠 <strong>분석 내용:</strong> rPPG + 음성 분석을 통한 종합 건강 평가
              </p>
            </div>
          </div>
        )}

        {currentStep === 'complete' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              측정 완료!
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">직관적인 건강</span> 분석이 완료되었습니다<br/>
              복용 전후 비교를 통해 건강 변화를 체감하세요
            </p>
            
            <div className="mb-6">
              <div className="w-24 h-24 mx-auto bg-green-500 rounded-full flex items-center justify-center">
                <Activity className="w-12 h-12 text-white" />
              </div>
            </div>

            <div className="mb-6 p-4 bg-green-500/10 rounded-lg border border-green-500/30">
              <p className="text-green-400 text-sm">
                🎯 <strong>다음 단계:</strong> 측정 결과를 확인하고 건강 가이드를 받아보세요
              </p>
            </div>

            <button onClick={goToResults} className="btn-primary text-xl px-8 py-4">
              결과 보기
            </button>
          </div>
        )}
      </main>
    </div>
  );
}