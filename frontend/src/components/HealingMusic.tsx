'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { checkMusicUsageLimit, incrementMusicUsage } from '@/lib/firebase';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';

interface HealthData {
  rppg?: {
    heartRate: number;
    stressIndex: number;
    confidence: number;
    quality: string;
  };
  voice?: {
    pitch: number;
    clarity: number;
    emotion: string;
    quality: string;
  };
  fusion?: {
    digitalTemperament: string;
    overallScore: number;
    recommendations: string[];
  };
}

interface MusicRecommendation {
  id: string;
  title: string;
  artist: string;
  genre: string;
  mood: string;
  frequency: string;
  duration: string;
  description: string;
  healthBenefit: string;
  reason: string;
  audioUrl?: string;
  isGenerated: boolean;
}

interface HealingMusicProps {
  healthData: HealthData;
  onClose?: () => void;
}

export default function HealingMusic({ healthData, onClose }: HealingMusicProps) {
  const { currentUser: user } = useAuth();
  const [recommendations, setRecommendations] = useState<MusicRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedMusic, setSelectedMusic] = useState<MusicRecommendation | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  
  // 사용 횟수 제한 관련 상태
  const [usageLimit, setUsageLimit] = useState<{
    canUse: boolean;
    remaining: number;
    dailyCount: number;
    dailyLimit: number;
  } | null>(null);
  const [isCheckingUsage, setIsCheckingUsage] = useState(true);

  // 음악 다운로드 기능
  const downloadMusic = useCallback(async (music: MusicRecommendation) => {
    if (!music.audioUrl) {
      alert('다운로드할 음악 파일이 없습니다.');
      return;
    }

    try {
      const response = await fetch(music.audioUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `${music.title}_${music.artist}.mp3`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
      window.URL.revokeObjectURL(url);
      alert('음악이 성공적으로 다운로드되었습니다!');
    } catch (error) {
      console.error('음악 다운로드 오류:', error);
      alert('다운로드 중 오류가 발생했습니다.');
    }
  }, []);

  // 음악 공유 기능 (카카오톡, 인스타그램 등)
  const shareMusic = useCallback(async (music: MusicRecommendation) => {
    if (navigator.share && music.audioUrl) {
      try {
        await navigator.share({
          title: `나만의 AI 맞춤 음악: ${music.title}`,
          text: `${music.artist}의 ${music.title} - AI가 추천한 맞춤형 치유 음악입니다!`,
          url: music.audioUrl
        });
      } catch (error) {
        console.error('공유 오류:', error);
        // 폴백: 링크 복사
        copyMusicLink(music);
      }
    } else {
      // 폴백: 링크 복사
      copyMusicLink(music);
    }
  }, []);

  // 음악 링크 복사
  const copyMusicLink = useCallback(async (music: MusicRecommendation) => {
    try {
      const shareText = `🎵 나만의 AI 맞춤 음악\n${music.title} - ${music.artist}\n${music.description}\n\n건강도우미 앱에서 더 많은 맞춤 음악을 만나보세요!`;
      await navigator.clipboard.writeText(shareText);
      alert('음악 정보가 클립보드에 복사되었습니다!');
    } catch (error) {
      console.error('링크 복사 오류:', error);
      alert('링크 복사에 실패했습니다.');
    }
  }, []);

  // 사용 횟수 제한 확인
  const checkUsageLimit = useCallback(async () => {
    if (!user?.email) {
      setUsageLimit({ canUse: false, remaining: 0, dailyCount: 0, dailyLimit: 3 });
      setIsCheckingUsage(false);
      return;
    }

    try {
      const usage = await checkMusicUsageLimit(user.email);
      setUsageLimit({
        canUse: usage.canUse,
        remaining: usage.remaining,
        dailyCount: 10 - usage.remaining,
        dailyLimit: 10
      });
    } catch (error) {
      console.error('사용량 제한 확인 오류:', error);
      setUsageLimit({ canUse: false, remaining: 0, dailyCount: 0, dailyLimit: 3 });
    } finally {
      setIsCheckingUsage(false);
    }
  }, [user?.email]);

  // 컴포넌트 마운트 시 사용량 제한 확인
  useEffect(() => {
    checkUsageLimit();
  }, [checkUsageLimit]);

  // 건강 데이터 기반 음악 추천 생성
  const generateMusicRecommendations = useCallback(async () => {
    if (!user?.email || !usageLimit?.canUse) {
      console.warn('사용량 제한에 도달했거나 사용자 인증이 필요합니다');
      return;
    }

    setIsLoading(true);
    
    try {
      // 사용량 증가
      const newCount = await incrementMusicUsage(user.email);
      if (newCount !== null) {
        // 사용량 제한 재확인
        await checkUsageLimit();
      }

      // Firebase Functions를 통한 AI 음악 추천 요청
      const response = await fetch('/api/healing-music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          healthData,
          requestType: 'recommendations',
          userId: user.email
        }),
      });

      if (!response.ok) {
        throw new Error('음악 추천 생성 실패');
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
      
    } catch (error) {
      console.error('음악 추천 오류:', error);
      
      // Fallback: 기본 추천 생성
      const fallbackRecommendations = generateFallbackRecommendations(healthData);
      setRecommendations(fallbackRecommendations);
    } finally {
      setIsLoading(false);
    }
  }, [healthData, user?.email, usageLimit?.canUse, checkUsageLimit]);

  // Fallback 추천 생성 (AI 서비스 실패 시)
  const generateFallbackRecommendations = (healthData: HealthData): MusicRecommendation[] => {
    const recommendations: MusicRecommendation[] = [];
    
    // 스트레스 지수 기반 추천
    if (healthData.rppg?.stressIndex) {
      const stressLevel = healthData.rppg.stressIndex;
      
      if (stressLevel > 0.7) {
        recommendations.push({
          id: 'stress-relief-1',
          title: '고요한 숲속 명상',
          artist: 'Nature Sounds',
          genre: '명상/자연음',
          mood: '차분함',
          frequency: '432Hz (치유 주파수)',
          duration: '15분',
          description: '스트레스 해소를 위한 자연의 소리와 치유 주파수',
          healthBenefit: '스트레스 감소, 심신 안정',
          reason: `현재 스트레스 지수가 ${(stressLevel * 100).toFixed(1)}%로 높아 안정적인 음악이 필요합니다.`,
          isGenerated: false
        });
      } else if (stressLevel > 0.4) {
        recommendations.push({
          id: 'stress-relief-2',
          title: '부드러운 클래식 모음',
          artist: 'Classical Collection',
          genre: '클래식',
          mood: '평온함',
          frequency: '528Hz (사랑의 주파수)',
          duration: '20분',
          description: '모차르트와 바흐의 평온한 선율',
          healthBenefit: '심박수 안정화, 집중력 향상',
          reason: `적당한 스트레스 수준으로 부드러운 클래식이 적합합니다.`,
          isGenerated: false
        });
      }
    }
    
    // 체질 기반 추천
    if (healthData.fusion?.digitalTemperament) {
      const temperament = healthData.fusion.digitalTemperament;
      
      if (temperament === '태양인') {
        recommendations.push({
          id: 'temperament-sun',
          title: '태양인 맞춤 치유음',
          artist: 'AI Generated',
          genre: '치유음악',
          mood: '활기참',
          frequency: '639Hz (관계의 주파수)',
          duration: '25분',
          description: '태양인의 특성을 고려한 맞춤형 치유 음악',
          healthBenefit: '에너지 균형, 활력 증진',
          reason: '태양인 체질에 맞는 활기찬 치유 음악입니다.',
          isGenerated: true
        });
      } else if (temperament === '태음인') {
        recommendations.push({
          id: 'temperament-moon',
          title: '태음인 맞춤 치유음',
          artist: 'AI Generated',
          genre: '치유음악',
          mood: '차분함',
          frequency: '741Hz (깨달음의 주파수)',
          duration: '30분',
          description: '태음인의 특성을 고려한 맞춤형 치유 음악',
          healthBenefit: '내면의 평화, 깊은 휴식',
          reason: '태음인 체질에 맞는 차분한 치유 음악입니다.',
          isGenerated: true
        });
      }
    }
    
    // 음성 감정 기반 추천
    if (healthData.voice?.emotion) {
      const emotion = healthData.voice.emotion;
      
      if (emotion === '긴장' || emotion === '불안') {
        recommendations.push({
          id: 'emotion-calm',
          title: '긴장 해소 음악',
          artist: 'Healing Sounds',
          genre: '치유음악',
          mood: '안정감',
          frequency: '396Hz (해방의 주파수)',
          duration: '18분',
          description: '긴장과 불안을 해소하는 부드러운 선율',
          healthBenefit: '긴장 해소, 마음의 평화',
          reason: '음성 분석 결과 긴장 상태로 안정적인 음악이 필요합니다.',
          isGenerated: false
        });
      }
    }
    
    return recommendations;
  };

  // 음악 재생/일시정지
  const togglePlayback = useCallback(() => {
    if (!selectedMusic) return;
    
    if (isPlaying) {
      audioElement?.pause();
      setIsPlaying(false);
    } else {
      if (audioElement) {
        audioElement.play();
        setIsPlaying(true);
      }
    }
  }, [selectedMusic, isPlaying, audioElement]);

  // 음악 선택
  const selectMusic = useCallback((music: MusicRecommendation) => {
    setSelectedMusic(music);
    
    // 실제 오디오 URL이 있는 경우에만 재생 가능
    if (music.audioUrl) {
      const audio = new Audio(music.audioUrl);
      audio.addEventListener('loadedmetadata', () => {
        setDuration(audio.duration);
      });
      audio.addEventListener('timeupdate', () => {
        setCurrentTime(audio.currentTime);
      });
      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setCurrentTime(0);
      });
      setAudioElement(audio);
    }
  }, []);

  // 컴포넌트 마운트 시 추천 생성
  useEffect(() => {
    generateMusicRecommendations();
  }, [generateMusicRecommendations]);

  // 컴포넌트 언마운트 시 오디오 정리
  useEffect(() => {
    return () => {
      if (audioElement) {
        audioElement.pause();
        audioElement.src = '';
      }
  };
  }, [audioElement]);

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // 사용량 제한 UI 렌더링
  const renderUsageLimitInfo = () => {
    // 로그인이 필요한 경우
    if (!user) {
      return (
        <div className="bg-gray-800 rounded-xl p-6 text-center border border-gray-700">
          <div className="w-24 h-24 bg-eno-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl">🔐</span>
          </div>
          <h3 className="text-eno-400 text-xl font-semibold mb-2">로그인이 필요합니다</h3>
          <p className="text-gray-300 mb-4">
            치유 음악 기능을 사용하려면 구글 또는 카카오로 로그인해주세요.
          </p>
          <div className="space-y-3">
            <Button
              onClick={() => window.location.href = '/login'}
              variant="default"
              size="lg"
              className="w-full"
            >
              🚀 로그인하기
            </Button>
            <p className="text-eno-400 text-sm">
              1초 만에 가입하고 사용하세요! ✨
            </p>
          </div>
        </div>
      );
    }

    if (isCheckingUsage) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="flex space-x-2">
            <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce"></div>
            <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="ml-3 text-eno-400">사용량을 확인하고 있습니다...</span>
        </div>
      );
    }

    if (!usageLimit?.canUse) {
      return (
        <div className="bg-gray-800 rounded-xl p-6 text-center border border-gray-700">
          <div className="w-24 h-24 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-4xl">⚠️</span>
          </div>
          <h3 className="text-red-400 text-xl font-semibold mb-2">일일 사용량 제한에 도달했습니다</h3>
          <p className="text-gray-300 mb-4">
            오늘은 이미 {usageLimit?.dailyCount || 0}회의 음악 추천을 받았습니다.
          </p>
          <p className="text-eno-400 text-sm">
            내일 다시 시도해주세요! 🎵
          </p>
        </div>
      );
    }

    return (
      <div className="bg-gray-800/50 rounded-xl p-4 mb-4 border border-eno-500/30">
        <div className="flex items-center justify-between text-sm">
          <span className="text-eno-400">🎵 오늘 남은 음악 추천</span>
          <span className="text-white font-semibold">
            {usageLimit.remaining}회
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
          <div
            className="bg-eno-500 h-2 rounded-full transition-all duration-200"
            style={{ width: `${((usageLimit.dailyLimit - usageLimit.remaining) / usageLimit.dailyLimit) * 100}%` }}
          ></div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-xl w-full max-w-4xl h-[700px] flex flex-col shadow-lg border border-eno-500/30"
      >
        {/* Header */}
        <CardHeader className="border-b border-eno-500/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-eno-600 rounded-full flex items-center justify-center">
                <span className="text-2xl">🎵</span>
              </div>
              <div>
                <CardTitle className="text-white">개인 맞춤형 치유 음악</CardTitle>
                <CardDescription className="text-eno-400">
                  건강 분석 결과를 바탕으로 한 맞춤 음악 추천
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="text-gray-400 hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>
        </CardHeader>

        <div className="flex-1 flex overflow-hidden">
          {/* 음악 추천 목록 */}
          <div className="w-1/2 p-4 border-r border-eno-500/30 overflow-y-auto">
            <h4 className="text-lg font-semibold text-white mb-4">🎯 맞춤 음악 추천</h4>
            
            {/* 사용량 제한 정보 */}
            {renderUsageLimitInfo()}
            
            {/* 로그인 상태와 사용량 제한에 따라 추천 목록 표시 */}
            {user && usageLimit?.canUse && (
              <>
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce"></div>
                      <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-3 h-3 bg-eno-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="ml-3 text-eno-400">AI가 음악을 분석하고 있습니다...</span>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {recommendations.map((music) => (
                      <motion.div
                        key={music.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className={`cursor-pointer transition-all duration-200`}
                        onClick={() => selectMusic(music)}
                      >
                        <Card 
                          variant={selectedMusic?.id === music.id ? "elevated" : "dark"}
                          padding="sm"
                          hover="lift"
                          className={`${
                            selectedMusic?.id === music.id
                              ? 'border-eno-500/50 bg-eno-500/10'
                              : 'border-transparent'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h5 className="text-white font-semibold">{music.title}</h5>
                              <p className="text-gray-300 text-sm">{music.artist}</p>
                              <div className="flex items-center space-x-2 mt-2">
                                <span className="px-2 py-1 bg-eno-500/20 text-eno-400 text-xs rounded">
                                  {music.genre}
                                </span>
                                <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded">
                                  {music.mood}
                                </span>
                                {music.isGenerated && (
                                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                                    AI 생성
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-400 text-xs mt-2">{music.duration} • {music.frequency}</p>
                            </div>
                            <div className="text-right">
                              <div className="w-8 h-8 bg-eno-600 rounded-full flex items-center justify-center">
                                <span className="text-white text-sm">▶</span>
                              </div>
                            </div>
                          </div>
                        </Card>
                      </motion.div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>

          {/* 음악 플레이어 및 상세 정보 */}
          <div className="w-1/2 p-4 overflow-y-auto">
            {selectedMusic ? (
              <div className="space-y-6">
                {/* 음악 정보 */}
                <Card variant="dark" padding="lg" className="text-center">
                  <div className="w-32 h-32 bg-eno-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <span className="text-6xl">🎵</span>
                  </div>
                  <CardTitle className="text-2xl mb-2">{selectedMusic.title}</CardTitle>
                  <p className="text-gray-300 text-lg">{selectedMusic.artist}</p>
                  <CardDescription className="text-eno-400 mt-1">
                    {selectedMusic.genre} • {selectedMusic.mood}
                  </CardDescription>
                </Card>

                {/* 재생 컨트롤 */}
                <Card variant="dark" padding="lg">
                  <div className="flex items-center justify-center space-x-4 mb-4">
                    <Button
                      onClick={togglePlayback}
                      disabled={!selectedMusic.audioUrl}
                      size="xl"
                      variant={selectedMusic.audioUrl ? "default" : "secondary"}
                      className="w-16 h-16 rounded-full"
                    >
                      <span className="text-2xl">
                        {isPlaying ? '⏸' : '▶'}
                      </span>
                    </Button>
                  </div>

                  {/* 진행률 바 */}
                  {selectedMusic.audioUrl && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-gray-400">
                        <span>{formatTime(currentTime)}</span>
                        <span>{formatTime(duration)}</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-eno-500 h-2 rounded-full transition-all duration-200"
                          style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {!selectedMusic.audioUrl && (
                    <div className="text-center py-4">
                      <CardDescription>
                        🎵 이 음악은 현재 미리보기 모드입니다.<br/>
                        실제 음악을 들으려면 AI 음악 생성 기능을 이용해주세요.
                      </CardDescription>
                    </div>
                  )}
                </Card>

                {/* 건강 효과 및 추천 이유 */}
                <div className="space-y-4">
                  <Card variant="dark" padding="sm" className="border-blue-500/30">
                    <CardTitle className="text-blue-300 mb-2">💙 건강 효과</CardTitle>
                    <CardContent className="p-0">
                      <p className="text-white">{selectedMusic.healthBenefit}</p>
                    </CardContent>
                  </Card>
                  
                  <Card variant="dark" padding="sm" className="border-green-500/30">
                    <CardTitle className="text-green-300 mb-2">🎯 추천 이유</CardTitle>
                    <CardContent className="p-0">
                      <p className="text-white">{selectedMusic.reason}</p>
                    </CardContent>
                  </Card>
                  
                  <Card variant="dark" padding="sm" className="border-eno-500/30">
                    <CardTitle className="text-eno-300 mb-2">📝 음악 설명</CardTitle>
                    <CardContent className="p-0">
                      <p className="text-white">{selectedMusic.description}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* AI 음악 생성 버튼 */}
                {selectedMusic.isGenerated && (
                  <div className="text-center">
                    <Button 
                      variant="success" 
                      size="lg"
                      className="w-full"
                    >
                      🎵 AI로 실제 음악 생성하기
                    </Button>
                    <CardDescription className="mt-2">
                      Suno AI를 활용하여 완전히 개인화된 치유 음악을 생성합니다
                    </CardDescription>
                  </div>
                )}

                {/* 음악 다운로드 및 공유 버튼 */}
                {selectedMusic.audioUrl && (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <Button 
                        onClick={() => downloadMusic(selectedMusic)}
                        variant="outline" 
                        size="lg"
                        className="w-full bg-green-600 hover:bg-green-700 border-green-500 text-white"
                      >
                        📥 다운로드
                      </Button>
                      <Button 
                        onClick={() => shareMusic(selectedMusic)}
                        variant="outline" 
                        size="lg"
                        className="w-full bg-blue-600 hover:bg-blue-700 border-blue-500 text-white"
                      >
                        🔗 공유하기
                      </Button>
                    </div>
                    <CardDescription className="text-center">
                      개인 맞춤 음악을 다운로드하거나 친구들과 공유해보세요!
                    </CardDescription>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <Card variant="dark" padding="lg" className="text-center">
                  <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-4xl">🎵</span>
                  </div>
                  <CardDescription>왼쪽에서 음악을 선택해주세요</CardDescription>
                </Card>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
