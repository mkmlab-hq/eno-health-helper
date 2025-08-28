'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';

interface AudioWaveformProps {
  isRecording: boolean;
  audioData?: Float32Array;
  onWaveformUpdate?: (data: Float32Array) => void;
  width?: number;
  height?: number;
}

export default function AudioWaveform({ 
  isRecording, 
  audioData, 
  onWaveformUpdate,
  width = 400, 
  height = 200 
}: AudioWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const microphoneRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  const [isInitialized, setIsInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 오디오 컨텍스트 초기화
  const initializeAudio = useCallback(async () => {
    try {
      if (audioContextRef.current) return;

      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      
      // 분석기 설정
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0.8;
      analyser.minDecibels = -90;
      analyser.maxDecibels = -10;
      
      audioContextRef.current = audioContext;
      analyserRef.current = analyser;
      
      // 마이크 스트림 가져오기
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100,
          channelCount: 1
        }
      });
      
      streamRef.current = stream;
      const microphone = audioContext.createMediaStreamSource(stream);
      microphone.connect(analyser);
      microphoneRef.current = microphone;
      
      setIsInitialized(true);
      setError(null);
      
    } catch (err) {
      console.error('Audio initialization error:', err);
      setError('마이크 접근에 실패했습니다. 권한을 확인해주세요.');
    }
  }, []);

  // 오디오 파형 그리기
  const drawWaveform = useCallback(() => {
    if (!canvasRef.current || !analyserRef.current || !isRecording) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const analyser = analyserRef.current;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const floatArray = new Float32Array(bufferLength);

    // 주파수 데이터 가져오기
    analyser.getByteFrequencyData(dataArray);
    
    // Float32Array로 변환 (0-1 범위)
    for (let i = 0; i < bufferLength; i++) {
      floatArray[i] = dataArray[i] / 255;
    }

    // onWaveformUpdate 콜백 호출
    if (onWaveformUpdate) {
      onWaveformUpdate(floatArray);
    }

    // 캔버스 클리어
    ctx.clearRect(0, 0, width, height);

    // 그라디언트 배경
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(34, 197, 94, 0.1)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.1)');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // 파형 그리기
    const barWidth = (width / bufferLength) * 2.5;
    let barHeight;
    let x = 0;

    ctx.fillStyle = 'rgba(34, 197, 94, 0.8)';
    ctx.strokeStyle = 'rgba(34, 197, 94, 1)';
    ctx.lineWidth = 2;

    for (let i = 0; i < bufferLength; i++) {
      barHeight = (floatArray[i] * height) / 2;

      // 중앙 기준으로 위아래로 그리기
      const y1 = height / 2 - barHeight;
      const y2 = height / 2 + barHeight;

      // 그라디언트 효과
      const barGradient = ctx.createLinearGradient(x, y1, x, y2);
      barGradient.addColorStop(0, 'rgba(34, 197, 94, 0.8)');
      barGradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.8)');
      barGradient.addColorStop(1, 'rgba(34, 197, 94, 0.8)');

      ctx.fillStyle = barGradient;
      ctx.fillRect(x, y1, barWidth, barHeight * 2);

      // 테두리
      ctx.strokeRect(x, y1, barWidth, barHeight * 2);

      x += barWidth + 1;
    }

    // 실시간 파형 애니메이션
    if (isRecording) {
      animationFrameRef.current = requestAnimationFrame(drawWaveform);
    }
  }, [isRecording, width, height, onWaveformUpdate]);

  // 녹음 시작/중지 처리
  useEffect(() => {
    if (isRecording && isInitialized) {
      drawWaveform();
    } else if (!isRecording && animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, [isRecording, isInitialized, drawWaveform]);

  // 컴포넌트 마운트 시 오디오 초기화
  useEffect(() => {
    if (isRecording && !isInitialized) {
      initializeAudio();
    }
  }, [isRecording, isInitialized, initializeAudio]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // 외부 오디오 데이터가 제공된 경우 처리
  useEffect(() => {
    if (audioData && canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.clearRect(0, 0, width, height);

      // 그라디언트 배경
      const gradient = ctx.createLinearGradient(0, 0, 0, height);
      gradient.addColorStop(0, 'rgba(34, 197, 94, 0.1)');
      gradient.addColorStop(1, 'rgba(59, 130, 246, 0.1)');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // 정적 파형 그리기
      const barWidth = (width / audioData.length) * 2.5;
      let x = 0;

      ctx.fillStyle = 'rgba(34, 197, 94, 0.8)';
      ctx.strokeStyle = 'rgba(34, 197, 94, 1)';
      ctx.lineWidth = 2;

      for (let i = 0; i < audioData.length; i++) {
        const barHeight = (audioData[i] * height) / 2;
        const y1 = height / 2 - barHeight;
        const y2 = height / 2 + barHeight;

        // 그라디언트 효과
        const barGradient = ctx.createLinearGradient(x, y1, x, y2);
        barGradient.addColorStop(0, 'rgba(34, 197, 94, 0.8)');
        barGradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.8)');
        barGradient.addColorStop(1, 'rgba(34, 197, 94, 0.8)');

        ctx.fillStyle = barGradient;
        ctx.fillRect(x, y1, barWidth, barHeight * 2);

        // 테두리
        ctx.strokeRect(x, y1, barWidth, barHeight * 2);

        x += barWidth + 1;
      }
    }
  }, [audioData, width, height]);

  return (
    <div className="w-full">
      <div className="mb-4 text-center">
        <h3 className="text-lg font-semibold text-white mb-2">
          {isRecording ? '🎤 실시간 음성 파형' : '📊 음성 파형 시각화'}
        </h3>
        <p className="text-sm text-gray-300">
          {isRecording ? '마이크 입력을 실시간으로 모니터링합니다' : '측정된 음성 데이터를 표시합니다'}
        </p>
      </div>

      <div className="relative">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="w-full h-auto rounded-lg border border-cyan-500/30 bg-gray-900"
        />
        
        {/* 녹음 상태 표시 */}
        {isRecording && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute top-4 right-4"
          >
            <div className="flex items-center space-x-2 bg-red-500/20 border border-red-500/50 rounded-full px-3 py-1">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-red-400 text-xs font-medium">녹음 중</span>
            </div>
          </motion.div>
        )}

        {/* 오디오 레벨 미터 */}
        {isRecording && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-gray-800/50 rounded-full h-2 overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-green-400 to-blue-500"
                initial={{ width: '0%' }}
                animate={{ width: '60%' }}
                transition={{ duration: 0.5, repeat: Infinity, repeatType: 'reverse' }}
              />
            </div>
          </div>
        )}
      </div>

      {/* 오류 메시지 */}
      {error && (
        <div className="mt-4 p-3 bg-red-900/30 border border-red-500/50 rounded-lg">
          <p className="text-red-400 text-sm text-center">{error}</p>
        </div>
      )}

      {/* 상태 정보 */}
      <div className="mt-4 text-center text-sm text-gray-400">
        {isRecording ? (
          <div className="flex items-center justify-center space-x-4">
            <span>🎵 실시간 모니터링</span>
            <span>📊 FFT 크기: 2048</span>
            <span>🎤 샘플레이트: 44.1kHz</span>
          </div>
        ) : (
          <div className="flex items-center justify-center space-x-4">
            <span>⏸️ 대기 중</span>
            <span>📱 마이크 권한 필요</span>
          </div>
        )}
      </div>
    </div>
  );
}
