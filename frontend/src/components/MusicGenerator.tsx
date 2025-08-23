'use client';

import React, { useState, useEffect } from 'react';
import { Play, Pause, Download, Music, Heart, Brain } from 'lucide-react';
import SunoAIClient, { EmotionData, MusicGenerationResponse } from '../lib/sunoAI';

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

  // Suno AI 클라이언트 초기화
  const sunoClient = new SunoAIClient(process.env.NEXT_PUBLIC_SUNO_API_KEY || '');

  /**
   * 개인화된 음악 생성
   */
  const generateMusic = async () => {
    if (!emotionData) {
      setError('감정 데이터가 필요합니다.');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const result = await sunoClient.generatePersonalizedMusic({
        emotionData,
        duration: 30,
        language: 'ko',
      });

      if (result.success && result.musicUrl) {
        setMusicData(result);
        onMusicGenerated?.(result);
        
        // 오디오 객체 생성
        const newAudio = new Audio(result.musicUrl);
        newAudio.preload = 'metadata';
        setAudio(newAudio);
        
      } else {
        setError(result.error || '음악 생성에 실패했습니다.');
      }

    } catch (error) {
      setError('음악 생성 중 오류가 발생했습니다.');
      console.error('음악 생성 오류:', error);
    } finally {
      setIsGenerating(false);
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
      a.download = `personalized_music_${emotionData.userId}.mp3`;
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
    const { emotion, intensity } = emotionData;
    
    if (emotion === 'stressed' || intensity > 0.8) {
      return '차분하고 명상적인 음악으로 긴장을 풀어드립니다.';
    } else if (emotion === 'anxious' || intensity > 0.6) {
      return '부드럽고 편안한 팝 음악으로 마음을 진정시킵니다.';
    } else {
      return '평화롭고 아름다운 앰비언트 음악으로 평온함을 유지합니다.';
    }
  };

  /**
   * 권장 BPM 계산
   */
  const getRecommendedBPM = () => {
    if (emotionData.intensity > 0.8) {
      return 60;
    } else if (emotionData.intensity > 0.6) {
      return 70;
    } else {
      return 80;
    }
  };

  return (
    <div className="glass-card p-6 animate-fade-in">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Music className="w-8 h-8 text-neon-cyan" />
          <h2 className="text-2xl font-orbitron font-bold neon-text">
            개인화된 치유 음악
          </h2>
        </div>
        
        <p className="text-gray-300 mb-4">
          당신의 감정 상태를 분석하여 맞춤형 음악을 생성합니다
        </p>

        {/* 감정 상태 표시 */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-glass-dark p-3 rounded-lg">
            <Heart className="w-6 h-6 text-red-400 mx-auto mb-2" />
            <p className="text-sm text-gray-300">감정 상태</p>
            <p className="text-lg font-bold text-neon-cyan">
              {emotionData.emotion === 'stressed' ? '긴장' : 
               emotionData.emotion === 'anxious' ? '불안' : '평온'}
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
      </div>

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
                음악 생성 중...
              </>
            ) : (
              <>
                <Music className="w-6 h-6 mr-2 inline" />
                개인화된 음악 생성하기
              </>
            )}
          </button>
        </div>
      )}

      {/* 생성된 음악 정보 */}
      {musicData && (
        <div className="space-y-4">
          <div className="bg-glass-dark p-4 rounded-lg">
            <h3 className="text-lg font-bold text-neon-cyan mb-2">생성된 음악</h3>
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
                <span className="text-gray-400">ID:</span>
                <span className="text-white ml-2">{musicData.musicId}</span>
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

          {/* 가사 표시 */}
          {musicData.lyrics && (
            <div className="bg-glass-dark p-4 rounded-lg">
              <h4 className="text-md font-bold text-neon-cyan mb-2">가사</h4>
              <p className="text-gray-300 text-sm whitespace-pre-line">
                {musicData.lyrics}
              </p>
            </div>
          )}

          {/* 새 음악 생성 */}
          <div className="text-center">
            <button
              onClick={generateMusic}
              className="btn-secondary px-6 py-3"
            >
              <Music className="w-5 h-5 mr-2" />
              다른 음악 생성하기
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