'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

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

interface HealthArtNFTProps {
  healthData: HealthData;
  onClose?: () => void;
}

interface GeneratedArt {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  metadata: {
    heartRate: number;
    stressIndex: number;
    emotion: string;
    temperament: string;
    overallScore: number;
    generatedAt: string;
    uniqueHash: string;
  };
}

export default function HealthArtNFT({ healthData, onClose }: HealthArtNFTProps) {
  const [generatedArt, setGeneratedArt] = useState<GeneratedArt | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [selectedStyle, setSelectedStyle] = useState<'abstract' | 'geometric' | 'organic' | 'minimal'>('abstract');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // 건강 데이터를 시각적 패턴으로 변환
  const generateVisualPattern = (data: HealthData) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // 캔버스 초기화
    ctx.clearRect(0, 0, width, height);

    // 배경 그라데이션
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(1, '#16213e');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // 심박수 기반 원형 패턴
    if (data.rppg) {
      const heartRate = data.rppg.heartRate;
      const stressIndex = data.rppg.stressIndex;
      
      // 중심점
      const centerX = width / 2;
      const centerY = height / 2;
      
      // 심박수에 따른 원의 개수
      const circleCount = Math.floor(heartRate / 10);
      
      for (let i = 0; i < circleCount; i++) {
        const radius = 20 + i * 15;
        const alpha = 0.1 + (i / circleCount) * 0.3;
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = `rgba(0, 255, 136, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    }

    // 음성 데이터 기반 파형 패턴
    if (data.voice) {
      const pitch = data.voice.pitch;
      const clarity = data.voice.clarity;
      
      ctx.strokeStyle = '#00d4ff';
      ctx.lineWidth = 3;
      ctx.beginPath();
      
      for (let x = 0; x < width; x += 2) {
        const frequency = (pitch / 1000) * Math.PI * 2;
        const amplitude = clarity * 50;
        const y = height / 2 + Math.sin(x * frequency * 0.01) * amplitude;
        
        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    }

    // 스트레스 지수 기반 불규칙 패턴
    if (data.rppg) {
      const stressIndex = data.rppg.stressIndex;
      const stressIntensity = stressIndex * 100;
      
      ctx.strokeStyle = `rgba(255, 100, 100, ${0.3 + stressIndex * 0.4})`;
      ctx.lineWidth = 1;
      
      for (let i = 0; i < 50; i++) {
        const x1 = Math.random() * width;
        const y1 = Math.random() * height;
        const x2 = x1 + (Math.random() - 0.5) * stressIntensity;
        const y2 = y1 + (Math.random() - 0.5) * stressIntensity;
        
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    }

    // 체질 기반 색상 테마
    if (data.fusion) {
      const temperament = data.fusion.digitalTemperament;
      let colorTheme = '#00ff88'; // 기본값
      
      switch (temperament) {
        case '태양인':
          colorTheme = '#ff6b35'; // 따뜻한 주황
          break;
        case '태음인':
          colorTheme = '#4ecdc4'; // 차가운 청록
          break;
        case '소양인':
          colorTheme = '#ffd93d'; // 밝은 노랑
          break;
        case '소음인':
          colorTheme = '#6c5ce7'; // 깊은 보라
          break;
      }
      
      // 체질별 특별한 패턴 추가
      ctx.fillStyle = `${colorTheme}20`;
      ctx.fillRect(width * 0.1, height * 0.1, width * 0.8, height * 0.8);
    }
  };

  // AI 아트 생성
  const generateHealthArt = async () => {
    setIsGenerating(true);
    setGenerationProgress(0);

    // 진행률 시뮬레이션
    const progressInterval = setInterval(() => {
      setGenerationProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    // 실제 아트 생성
    setTimeout(() => {
      generateVisualPattern(healthData);
      
      // 생성된 아트 정보
      const newArt: GeneratedArt = {
        id: `health-art-${Date.now()}`,
        title: `건강의 예술 #${Date.now()}`,
        description: `${healthData.fusion?.digitalTemperament || '미분류'} 체질의 건강 상태를 표현한 유니크한 디지털 아트입니다.`,
        imageUrl: canvasRef.current?.toDataURL() || '',
        metadata: {
          heartRate: healthData.rppg?.heartRate || 0,
          stressIndex: healthData.rppg?.stressIndex || 0,
          emotion: healthData.voice?.emotion || 'unknown',
          temperament: healthData.fusion?.digitalTemperament || 'unknown',
          overallScore: healthData.fusion?.overallScore || 0,
          generatedAt: new Date().toISOString(),
          uniqueHash: `hash-${Math.random().toString(36).substr(2, 9)}`
        }
      };

      setGeneratedArt(newArt);
      setIsGenerating(false);
      setGenerationProgress(100);
    }, 3000);
  };

  // NFT 메타데이터 생성
  const generateNFTMetadata = () => {
    if (!generatedArt) return null;

    return {
      name: generatedArt.title,
      description: generatedArt.description,
      image: generatedArt.imageUrl,
      attributes: [
        {
          trait_type: "체질",
          value: generatedArt.metadata.temperament
        },
        {
          trait_type: "심박수",
          value: generatedArt.metadata.heartRate
        },
        {
          trait_type: "스트레스 지수",
          value: (generatedArt.metadata.stressIndex * 100).toFixed(1)
        },
        {
          trait_type: "감정 상태",
          value: generatedArt.metadata.emotion
        },
        {
          trait_type: "종합 건강 점수",
          value: generatedArt.metadata.overallScore
        },
        {
          trait_type: "생성 시간",
          value: new Date(generatedArt.metadata.generatedAt).toLocaleString('ko-KR')
        },
        {
          trait_type: "고유 해시",
          value: generatedArt.metadata.uniqueHash
        }
      ]
    };
  };

  // NFT 다운로드
  const downloadNFT = () => {
    if (!generatedArt) return;

    const metadata = generateNFTMetadata();
    if (!metadata) return;

    const metadataBlob = new Blob([JSON.stringify(metadata, null, 2)], {
      type: 'application/json'
    });
    const metadataUrl = URL.createObjectURL(metadataBlob);

    const a = document.createElement('a');
    a.href = metadataUrl;
    a.download = `${generatedArt.title}-metadata.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(metadataUrl);

    // 이미지도 다운로드
    const imageLink = document.createElement('a');
    imageLink.href = generatedArt.imageUrl;
    imageLink.download = `${generatedArt.title}.png`;
    document.body.appendChild(imageLink);
    imageLink.click();
    document.body.removeChild(imageLink);
  };

  // NFT 공유
  const shareNFT = async () => {
    if (!generatedArt) return;

    const shareText = `🎨 나만의 건강 아트 NFT를 생성했습니다!\n\n${generatedArt.title}\n${generatedArt.description}\n\n건강도우미 앱에서 당신만의 유니크한 건강 아트를 만들어보세요!`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: generatedArt.title,
          text: shareText,
          url: window.location.href
        });
      } catch (error) {
        // 폴백: 클립보드 복사
        navigator.clipboard.writeText(shareText);
        alert('NFT 정보가 클립보드에 복사되었습니다!');
      }
    } else {
      // 폴백: 클립보드 복사
      navigator.clipboard.writeText(shareText);
      alert('NFT 정보가 클립보드에 복사되었습니다!');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-gray-900 rounded-xl w-full max-w-5xl h-[800px] flex flex-col shadow-lg border border-eno-500/30"
      >
        {/* Header */}
        <div className="border-b border-eno-500/30 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center">
                <span className="text-2xl">🎨</span>
              </div>
              <div>
                <h2 className="text-white text-xl font-semibold">건강 아트 NFT 생성기</h2>
                <p className="text-purple-300 text-sm">
                  당신의 건강 데이터를 유니크한 디지털 예술로 변환
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 아트 생성 컨트롤 */}
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-white text-lg font-semibold mb-4">🎨 아트 스타일 선택</h3>
                <div className="grid grid-cols-2 gap-3">
                  {(['abstract', 'geometric', 'organic', 'minimal'] as const).map((style) => (
                    <button
                      key={style}
                      onClick={() => setSelectedStyle(style)}
                      className={`p-3 rounded-lg border transition-all ${
                        selectedStyle === style
                          ? 'border-purple-500 bg-purple-500/20 text-purple-300'
                          : 'border-gray-600 bg-gray-700/50 text-gray-300 hover:border-gray-500'
                      }`}
                    >
                      {style === 'abstract' && '🎭 추상적'}
                      {style === 'geometric' && '🔷 기하학적'}
                      {style === 'organic' && '🌿 유기적'}
                      {style === 'minimal' && '⚪ 미니멀'}
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-white text-lg font-semibold mb-4">💎 건강 데이터 분석</h3>
                <div className="space-y-3 text-sm">
                  {healthData.rppg && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">심박수</span>
                      <span className="text-white font-medium">{healthData.rppg.heartRate} BPM</span>
                    </div>
                  )}
                  {healthData.rppg && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">스트레스 지수</span>
                      <span className="text-white font-medium">{(healthData.rppg.stressIndex * 100).toFixed(1)}%</span>
                    </div>
                  )}
                  {healthData.voice && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">음성 감정</span>
                      <span className="text-white font-medium">{healthData.voice.emotion}</span>
                    </div>
                  )}
                  {healthData.fusion && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">체질</span>
                      <span className="text-white font-medium">{healthData.fusion.digitalTemperament}</span>
                    </div>
                  )}
                  {healthData.fusion && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">종합 점수</span>
                      <span className="text-white font-medium">{healthData.fusion.overallScore}점</span>
                    </div>
                  )}
                </div>
              </div>

              {!generatedArt && (
                <button
                  onClick={generateHealthArt}
                  disabled={isGenerating}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-semibold text-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 disabled:opacity-50"
                >
                  {isGenerating ? '🎨 AI 아트 생성 중...' : '🎨 건강 아트 생성하기'}
                </button>
              )}

              {isGenerating && (
                <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                  <div className="text-center">
                    <div className="text-purple-400 font-medium mb-2">AI가 당신의 건강을 예술로 변환하고 있습니다...</div>
                    <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
                      <div 
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${generationProgress}%` }}
                      ></div>
                    </div>
                    <div className="text-purple-300 text-sm">{Math.round(generationProgress)}% 완료</div>
                  </div>
                </div>
              )}
            </div>

            {/* 아트 캔버스 및 결과 */}
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700/50">
                <h3 className="text-white text-lg font-semibold mb-4">🎨 생성된 건강 아트</h3>
                <div className="flex justify-center">
                  <canvas
                    ref={canvasRef}
                    width={400}
                    height={400}
                    className="border border-gray-600 rounded-lg bg-gray-900"
                  />
                </div>
              </div>

              {generatedArt && (
                <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-xl p-6 border border-purple-500/30">
                  <h3 className="text-white text-lg font-semibold mb-4">💎 NFT 메타데이터</h3>
                  <div className="space-y-3 text-sm mb-6">
                    <div className="flex justify-between">
                      <span className="text-purple-300">제목</span>
                      <span className="text-white font-medium">{generatedArt.title}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">고유 ID</span>
                      <span className="text-white font-medium">{generatedArt.id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-300">생성 시간</span>
                      <span className="text-white font-medium">
                        {new Date(generatedArt.metadata.generatedAt).toLocaleString('ko-KR')}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <button
                      onClick={downloadNFT}
                      className="bg-green-600 hover:bg-green-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                    >
                      📥 NFT 다운로드
                    </button>
                    <button
                      onClick={shareNFT}
                      className="bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                    >
                      🔗 NFT 공유하기
                    </button>
                  </div>

                  <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                    <div className="text-purple-300 font-medium mb-2">💡 NFT 활용 방법</div>
                    <div className="text-white text-sm">
                      생성된 NFT는 블록체인 마켓플레이스에 등록하거나, 
                      소셜 미디어 프로필 이미지로 활용할 수 있습니다. 
                      당신만의 유니크한 건강 아트를 자랑해보세요!
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
} 