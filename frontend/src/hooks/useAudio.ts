import { useState, useRef, useCallback, useEffect } from 'react';

interface AudioState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioBlob: Blob | null;
  audioUrl: string | null;
  error: string | null;
}

interface UseAudioOptions {
  onRecordingStart?: () => void;
  onRecordingStop?: (blob: Blob) => void;
  onRecordingPause?: () => void;
  onRecordingResume?: () => void;
  onError?: (error: string) => void;
  maxDuration?: number; // 최대 녹음 시간 (초)
  audioConstraints?: MediaTrackConstraints;
}

export function useAudio(options: UseAudioOptions = {}) {
  const {
    onRecordingStart,
    onRecordingStop,
    onRecordingPause,
    onRecordingResume,
    onError,
    maxDuration = 300, // 기본 5분
    audioConstraints = {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  } = options;

  const [state, setState] = useState<AudioState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioBlob: null,
    audioUrl: null,
    error: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  // 에러 처리
  const handleError = useCallback((error: string) => {
    setState(prev => ({ ...prev, error, isRecording: false, isPaused: false }));
    onError?.(error);
  }, [onError]);

  // 녹음 시작
  const startRecording = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));
      
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: audioConstraints,
      });
      
      streamRef.current = stream;
      chunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setState(prev => ({
          ...prev,
          audioBlob,
          audioUrl,
          isRecording: false,
          isPaused: false,
        }));
        
        onRecordingStop?.(audioBlob);
        
        // 스트림 정리
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      };
      
      mediaRecorder.onerror = (event) => {
        handleError(`녹음 중 오류가 발생했습니다: ${event.error}`);
      };
      
      mediaRecorder.start(100); // 100ms마다 데이터 수집
      startTimeRef.current = Date.now();
      
      setState(prev => ({ ...prev, isRecording: true, isPaused: false }));
      onRecordingStart?.();
      
      // 최대 녹음 시간 설정
      if (maxDuration > 0) {
        setTimeout(() => {
          if (state.isRecording) {
            stopRecording();
          }
        }, maxDuration * 1000);
      }
      
      // 녹음 시간 추적
      durationIntervalRef.current = setInterval(() => {
        setState(prev => ({
          ...prev,
          duration: Math.floor((Date.now() - startTimeRef.current) / 1000),
        }));
      }, 1000);
      
    } catch (error) {
      handleError(`마이크 접근 권한이 필요합니다: ${error}`);
    }
  }, [audioConstraints, maxDuration, onRecordingStart, handleError]);

  // 녹음 중지
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }
    }
  }, [state.isRecording]);

  // 녹음 일시정지
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording && !state.isPaused) {
      mediaRecorderRef.current.pause();
      setState(prev => ({ ...prev, isPaused: true }));
      onRecordingPause?.();
    }
  }, [state.isRecording, state.isPaused, onRecordingPause]);

  // 녹음 재개
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording && state.isPaused) {
      mediaRecorderRef.current.resume();
      setState(prev => ({ ...prev, isPaused: false }));
      onRecordingResume?.();
    }
  }, [state.isRecording, state.isPaused, onRecordingResume]);

  // 녹음 취소
  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }
      
      // 스트림 정리
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      
      setState(prev => ({
        ...prev,
        isRecording: false,
        isPaused: false,
        duration: 0,
        audioBlob: null,
        audioUrl: null,
      }));
    }
  }, [state.isRecording]);

  // 오디오 재생
  const playAudio = useCallback(() => {
    if (state.audioUrl) {
      const audio = new Audio(state.audioUrl);
      audio.play().catch(error => {
        handleError(`오디오 재생 중 오류가 발생했습니다: ${error}`);
      });
    }
  }, [state.audioUrl, handleError]);

  // 오디오 다운로드
  const downloadAudio = useCallback((filename = 'recording.webm') => {
    if (state.audioBlob) {
      const url = URL.createObjectURL(state.audioBlob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [state.audioBlob]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (state.audioUrl) {
        URL.revokeObjectURL(state.audioUrl);
      }
    };
  }, [state.audioUrl]);

  // 녹음 시간 포맷팅
  const formatDuration = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return {
    // 상태
    ...state,
    
    // 액션
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    cancelRecording,
    playAudio,
    downloadAudio,
    
    // 유틸리티
    formatDuration,
    
    // 녹음 가능 여부
    canRecord: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
  };
}
