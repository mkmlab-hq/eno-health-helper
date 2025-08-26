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
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const audioRecorderRef = useRef<MediaRecorder | null>(null);

  // 모바일 체크
  useEffect(() => {
    setIsMobile(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent));
  }, []);

  // 측정 시작하기 버튼 클릭 시 전체 측정 플로우 시작
  const startMeasurement = () => {
    setScreen('face');
    startFaceMeasurement();
  };

  // 얼굴 측정 시작
  const startFaceMeasurement = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      
      // 30초 카운트다운
      const countdown = setInterval(() => {
        setFaceTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(countdown);
            stopFaceMeasurement();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (error) {
      setError('카메라 접근 권한이 필요합니다.');
    }
  };

  // 얼굴 측정 중지
  const stopFaceMeasurement = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      setVideoBlob(new Blob(['face_data'], { type: 'video/webm' }));
      setScreen('voice');
      startVoiceMeasurement();
    }
  };

  // 음성 측정 시작
  const startVoiceMeasurement = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      audioRecorderRef.current = mediaRecorder;
      
      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
        setScreen('analyzing');
        runFusionAnalysis();
      };
      
      mediaRecorder.start();
      setIsAudioRecording(true);
      
      // 5초 카운트다운
      const countdown = setInterval(() => {
        setVoiceTimeLeft(prev => {
          if (prev <= 1) {
            clearInterval(countdown);
            mediaRecorder.stop();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      
    } catch (error) {
      setError('마이크 접근 권한이 필요합니다.');
    }
  };

  // 융합 분석 실행
  const runFusionAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisStep(0);
    
    // 분석 단계 시뮬레이션
    const steps = ['데이터 전처리', 'rPPG 분석', '음성 분석', 'AI 융합 분석', '결과 생성'];
    
    for (let i = 0; i < steps.length; i++) {
      setAnalysisStep(i);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // 결과 생성
    const mockResult: FusionAnalysisResult = {
      temperament: {
        temperament: '태양체질',
        confidence: 0.87,
        message: '활발하고 열정적인 성격을 가진 태양체질입니다.'
      },
      confidence: 0.85,
      message: 'rPPG와 음성 분석을 통한 종합적인 건강 평가가 완료되었습니다.',
      timestamp: new Date().toISOString()
    };
    
    setResult(mockResult);
    setScreen('done');
    setIsAnalyzing(false);
  };

  // 다시 시작
  const restart = () => {
    setScreen('welcome');
    setFaceTimeLeft(30);
    setVoiceTimeLeft(5);
    setVideoBlob(null);
    setAudioBlob(null);
    setResult(null);
    setError(null);
    setIsAnalyzing(false);
    setIsAudioRecording(false);
  };

  // 결과 페이지로 이동
  const goToResults = () => {
    router.push('/result');
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl text-red-400 mb-4">오류가 발생했습니다</h1>
          <p className="text-gray-300 mb-4">{error}</p>
          <button onClick={restart} className="btn-primary">
            다시 시작하기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <main className="max-w-4xl mx-auto p-4">
        {screen === 'welcome' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-3xl font-orbitron font-bold neon-text mb-6">
              융합 건강 분석
            </h2>
            <p className="text-gray-300 mb-8 text-lg">
              rPPG와 음성 분석을 통한 종합적인 건강 평가<br/>
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
            <button onClick={startMeasurement} className="btn-primary text-xl px-8 py-4">
              측정 시작하기
            </button>
          </div>
        )}

        {screen === 'face' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              얼굴 측정 단계
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">카메라에 얼굴을 비추세요 ({faceTimeLeft}초)</span><br/>
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

            <div className="text-4xl font-bold text-neon-cyan mb-4">
              {faceTimeLeft}초
            </div>
          </div>
        )}

        {screen === 'voice' && (
          <div className="glass-card p-8 text-center animate-fade-in">
            <h2 className="text-2xl font-orbitron font-bold neon-text mb-6">
              음성 측정 단계
            </h2>
            <p className="text-gray-300 mb-6">
              <span className="text-neon-cyan font-medium">{voiceTimeLeft}초 동안 '아~' 발음을 해주세요</span><br/>
              마이크에 명확하게 소리를 내주세요
            </p>
            
            <div className="mb-6">
              <div className="w-24 h-24 mx-auto bg-glass rounded-full flex items-center justify-center border-2 border-neon-cyan">
                <div className={`w-12 h-12 ${isAudioRecording ? 'text-red-400 animate-pulse' : 'text-neon-cyan'}`}>
                  🎤
                </div>
              </div>
              {isAudioRecording && (
                <div className="mt-2 text-red-400 text-sm animate-pulse">
                  🎤 녹음 중... ({voiceTimeLeft}초)
                </div>
              )}
            </div>

            <div className="mb-4 p-3 bg-neon-cyan/10 rounded border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                🎵 <strong>음성 분석:</strong> Jitter, Shimmer 등 음성 품질 지표를 통해 건강 상태를 평가합니다
              </p>
            </div>

            <div className="text-4xl font-bold text-neon-cyan mb-4">
              {voiceTimeLeft}초
            </div>
          </div>
        )}

        {screen === 'analyzing' && (
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
                <div className="w-12 h-12 text-neon-cyan animate-pulse">
                  🧠
                </div>
              </div>
            </div>

            <ProgressSteps 
              currentStep={analysisStep} 
              steps={[
                { id: 'preprocess', title: '데이터 전처리', description: '입력 데이터를 분석 가능한 형태로 변환', status: analysisStep >= 0 ? 'completed' : 'pending' },
                { id: 'rppg', title: 'rPPG 분석', description: '얼굴 영상에서 생체신호 추출', status: analysisStep >= 1 ? 'completed' : analysisStep === 1 ? 'active' : 'pending' },
                { id: 'voice', title: '음성 분석', description: '음성 품질 지표 분석', status: analysisStep >= 2 ? 'completed' : analysisStep === 2 ? 'active' : 'pending' },
                { id: 'fusion', title: 'AI 융합 분석', description: 'rPPG와 음성 데이터 융합', status: analysisStep >= 3 ? 'completed' : analysisStep === 3 ? 'active' : 'pending' },
                { id: 'result', title: '결과 생성', description: '최종 건강 분석 결과 생성', status: analysisStep >= 4 ? 'completed' : analysisStep === 4 ? 'active' : 'pending' }
              ]} 
            />
            
            <div className="mt-4 p-3 bg-neon-cyan/10 rounded border border-neon-cyan/30">
              <p className="text-neon-cyan text-sm">
                🧠 <strong>분석 내용:</strong> rPPG + 음성 분석을 통한 종합 건강 평가
              </p>
            </div>
          </div>
        )}

        {screen === 'done' && result && (
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
                <div className="w-12 h-12 text-white">
                  ✅
                </div>
              </div>
            </div>

            <div className="mb-6 p-4 bg-green-500/10 rounded-lg border border-green-500/30">
              <h3 className="text-green-400 font-bold mb-2">분석 결과</h3>
              <p className="text-green-400 text-sm">
                <strong>체질:</strong> {result.temperament.temperament}<br/>
                <strong>신뢰도:</strong> {(result.confidence * 100).toFixed(1)}%<br/>
                <strong>메시지:</strong> {result.message}
              </p>
            </div>

            <div className="flex space-x-4 justify-center">
              <button onClick={goToResults} className="btn-primary text-xl px-8 py-4">
                결과 보기
              </button>
              <button onClick={restart} className="btn-secondary text-xl px-8 py-4">
                다시 측정
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
