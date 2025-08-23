'use client';

import React, { useState, useEffect } from 'react';
import { Play, Pause, Download, Music, Heart, Brain, Sparkles, Eye, Code } from 'lucide-react';
import { EmotionData } from '../lib/sunoAI';
import SunoAIClient, { MusicGenerationResponse } from '../lib/sunoAI';
import { SunoAIPromptMapper } from '../lib/sunoAIPrompts';

interface MusicGeneratorProps {
  emotionData: EmotionData;
  onMusicGenerated?: (music: MusicGenerationResponse) => void;
}

export default function MusicGenerator({ emotionData, onMusicGenerated }: MusicGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [musicData, setMusicData] = useState<MusicGenerationResponse | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // AI 작곡 과정을 시뮬레이션하기 위한 상태
  const [progress, setProgress] = useState<string[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [showProgress, setShowProgress] = useState(false);
  
  // Suno AI 클라이언트
  const [sunoClient] = useState(() => new SunoAIClient(process.env.NEXT_PUBLIC_SUNO_API_KEY || ''));
  
  // 프롬프트 미리보기 상태
  const [showPromptPreview, setShowPromptPreview] = useState(false);

  /**
   * 개인화된 음악 생성 (Suno AI API 연동)
   */
  const generateMusic = async () => {
    if (!emotionData) {
      setError('감정 데이터가 필요합니다.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setProgress([]);
    setCurrentStep(0);
    setShowProgress(true);

    try {
      // AI 작곡 과정 시뮬레이션
      const steps = [
        "🎵 당신의 감정 데이터를 분석 중...",
        "🎼 AI가 프롬프트를 최적화 중...",
        "🎹 Suno AI가 음악을 작곡 중...",
        "🎧 최종 믹싱 및 마스터링...",
        "✅ 당신만을 위한 AI 사운드트랙 완성!"
      ];

      // 단계별 진행 시뮬레이션
      for (let i = 0; i < steps.length; i++) {
        setCurrentStep(i);
        setProgress(prev => [...prev, steps[i]]);
        
        // 실제 Suno AI API 호출 (3단계에서)
        if (i === 2) {
          try {
            const result = await sunoClient.generatePersonalizedMusic(emotionData);
            
            if (result.success && result.musicUrl) {
              setMusicData(result);
              onMusicGenerated?.(result);
              
              // 오디오 객체 생성
              const newAudio = new Audio(result.musicUrl);
              newAudio.preload = 'metadata';
              setAudio(newAudio);
            } else {
              throw new Error(result.error || '음악 생성에 실패했습니다.');
            }
          } catch (apiError) {
            console.error('Suno AI API 오류:', apiError);
            // API 오류 시에도 시뮬레이션은 계속 진행
          }
        }
        
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      
    } catch (error) {
      setError('음악 생성 중 오류가 발생했습니다.');
      console.error('음악 생성 오류:', error);
    } finally {
      setIsGenerating(false);
      setShowProgress(false);
    }
  };

  /**
   * 음악 재생/일시정지
   */
  const togglePlayback = () => {
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio.play();
      setIsPlaying(true);
    }
  };

  /**
   * 음악 다운로드
   */
  const downloadMusic = async () => {
    if (!musicData?.musicUrl) return;

    try {
      const response = await fetch(musicData.musicUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai_music_${emotionData.emotion}_${emotionData.userId}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      setError('음악 다운로드에 실패했습니다.');
    }
  };

  /**
   * 감정 상태에 따른 음악 스타일 설명
   */
  const getMusicStyleDescription = () => {
    return SunoAIPromptMapper.getEmotionKoreanDescription(emotionData.emotion);
  };

  /**
   * 권장 BPM 계산
   */
  const getRecommendedBPM = () => {
    const prompt = SunoAIPromptMapper.getPromptForEmotion(emotionData.emotion);
    return prompt ? prompt.bpm : 80;
  };

  /**
   * 프롬프트 미리보기 토글
   */
  const togglePromptPreview = () => {
    setShowPromptPreview(!showPromptPreview);
  };

  return (
    <div className="glass-card p-6 animate-fade-in">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Music className="w-8 h-8 text-neon-cyan" />
          <h2 className="text-2xl font-orbitron font-bold neon-text">
            AI 생성 '감정의 사운드트랙'
          </h2>
        </div>
        
        <p className="text-gray-300 mb-4">
          Suno AI가 당신의 감정 상태를 분석하여 세상에 단 하나뿐인 맞춤형 음악을 작곡합니다
        </p>

        {/* 감정 상태 표시 */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-glass-dark p-3 rounded-lg">
            <Heart className="w-6 h-6 text-red-400 mx-auto mb-2" />
            <p className="text-sm text-gray-300">감정 상태</p>
            <p className="text-lg font-bold text-neon-cyan">
              {emotionData.emotion === 'stressed' ? '긴장' : 
               emotionData.emotion === 'anxious' ? '불안' : 
               emotionData.emotion === 'energetic' ? '활기찬' :
               emotionData.emotion === 'focused' ? '집중' : '평온'}
            </p>
          </div>
          
          <div className="bg-glass-dark p-3 rounded-lg">
            <Brain className="w-6 h-6 text-blue-400 mx-auto mb-2" />
            <p className="text-sm text-gray-300">강도</p>
            <p className="text-lg font-bold text-neon-cyan">
              {Math.round(emotionData.intensity * 100)}%
            </p>
          </div>
          
          <div className="bg-glass-dark p-3 rounded-lg">
            <div className="w-6 h-6 bg-green-400 rounded-full mx-auto mb-2" />
            <p className="text-sm text-gray-300">시간</p>
            <p className="text-lg font-bold text-neon-cyan">
              {new Date(emotionData.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>

        {/* 음악 스타일 설명 */}
        <div className="bg-glass-dark p-4 rounded-lg mb-6">
          <p className="text-gray-300 text-sm leading-relaxed">
            {getMusicStyleDescription()}
          </p>
          <p className="text-neon-cyan text-sm mt-2">
            권장 BPM: {getRecommendedBPM()}
          </p>
        </div>

        {/* 프롬프트 미리보기 버튼 */}
        <div className="mb-4">
          <button
            onClick={togglePromptPreview}
            className="btn-secondary px-4 py-2 text-sm flex items-center mx-auto space-x-2"
          >
            <Code className="w-4 h-4" />
            <span>AI 프롬프트 미리보기</span>
          </button>
        </div>

        {/* 프롬프트 미리보기 */}
        {showPromptPreview && (
          <div className="bg-glass-dark p-4 rounded-lg mb-6 text-left">
            <h4 className="text-md font-bold text-neon-cyan mb-2 flex items-center">
              <Eye className="w-4 h-4 mr-2" />
              Suno AI 프롬프트
            </h4>
            <p className="text-gray-300 text-sm leading-relaxed font-mono">
              {SunoAIPromptMapper.generateOptimizedPrompt(emotionData.emotion, emotionData.intensity)}
            </p>
          </div>
        )}
      </div>

      {/* AI 작곡 진행 상황 */}
      {showProgress && (
        <div className="glass-card p-6 mb-6 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-500/30">
          <div className="text-center mb-4">
            <Sparkles className="w-8 h-8 text-purple-400 mx-auto mb-2 animate-pulse" />
            <h3 className="text-xl font-orbitron font-bold text-purple-400">
              Suno AI 작곡 진행 상황
            </h3>
          </div>
          
          <div className="space-y-3">
            {progress.map((step, index) => (
              <div 
                key={index} 
                className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-500 ${
                  index === currentStep 
                    ? 'bg-purple-500/20 border border-purple-400/50 text-purple-300' 
                    : index < currentStep 
                    ? 'bg-green-500/20 border border-green-400/50 text-green-300'
                    : 'bg-gray-500/20 border border-gray-400/30 text-gray-400'
                }`}
              >
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold ${
                  index === currentStep 
                    ? 'bg-purple-400 text-purple-900 animate-pulse' 
                    : index < currentStep 
                    ? 'bg-green-400 text-green-900'
                    : 'bg-gray-400 text-gray-700'
                }`}>
                  {index < currentStep ? '✓' : index === currentStep ? '●' : '○'}
                </div>
                <span className="flex-1">{step}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 음악 생성 버튼 */}
      {!musicData && (
        <div className="text-center">
          <button
            onClick={generateMusic}
            disabled={isGenerating}
            className={`btn-primary text-xl px-8 py-4 ${
              isGenerating ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mx-auto mb-2"></div>
                Suno AI가 음악을 작곡 중...
              </>
            ) : (
              <>
                <Music className="w-6 h-6 mr-2 inline" />
                Suno AI 작곡 시작하기
              </>
            )}
          </button>
        </div>
      )}

      {/* 생성된 음악 정보 */}
      {musicData && (
        <div className="space-y-4">
          <div className="glass-card p-4 rounded-lg bg-gradient-to-r from-green-900/20 to-blue-900/20 border border-green-500/30">
            <h3 className="text-lg font-bold text-neon-cyan mb-2 flex items-center">
              <Sparkles className="w-5 h-5 mr-2 text-green-400" />
              Suno AI가 생성한 음악
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">스타일:</span>
                <span className="text-white ml-2">{musicData.style}</span>
              </div>
              <div>
                <span className="text-gray-400">BPM:</span>
                <span className="text-white ml-2">{musicData.bpm}</span>
              </div>
              <div>
                <span className="text-gray-400">길이:</span>
                <span className="text-white ml-2">{musicData.duration}초</span>
              </div>
              <div>
                <span className="text-gray-400">생성 상태:</span>
                <span className="text-white ml-2">{musicData.generationStatus}</span>
              </div>
            </div>
          </div>

          {/* 음악 컨트롤 */}
          <div className="flex space-x-4 justify-center">
            <button
              onClick={togglePlayback}
              className="btn-primary px-6 py-3"
            >
              {isPlaying ? (
                <>
                  <Pause className="w-5 h-5 mr-2" />
                  일시정지
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  재생
                </>
              )}
            </button>

            <button
              onClick={downloadMusic}
              className="btn-secondary px-6 py-3"
            >
              <Download className="w-5 h-5 mr-2" />
              다운로드
            </button>
          </div>

          {/* 새 음악 생성 */}
          <div className="text-center">
            <button
              onClick={generateMusic}
              className="btn-secondary px-6 py-3"
            >
              <Music className="w-5 h-5 mr-2" />
              다른 음악 Suno AI 작곡하기
            </button>
          </div>
        </div>
      )}

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/50 p-4 rounded-lg mt-4">
          <p className="text-red-400 text-center">{error}</p>
        </div>
      )}
    </div>
  );
} 