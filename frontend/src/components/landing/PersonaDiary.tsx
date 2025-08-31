'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface PersonaEntry {
  id: string;
  date: string;
  mood: string;
  energy: number;
  activities: string[];
  persona: string;
  insights: string;
}

export default function PersonaDiary() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [currentEntry, setCurrentEntry] = useState<PersonaEntry>({
    id: '1',
    date: new Date().toISOString().split('T')[0],
    mood: '평온함',
    energy: 7,
    activities: ['명상', '산책'],
    persona: 'A1-태양형',
    insights: '오늘은 태양의 에너지가 강하게 느껴집니다.'
  });

  const moodOptions = ['평온함', '활기참', '차분함', '열정적', '사색적'];
  const personaTypes = ['A1-태양형', 'A2-달형', 'A3-별형'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900">
      {/* 헤더 */}
      <header className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center shadow-neon-cyan">
              <div className="w-6 h-6 text-white neon-glow">📔</div>
            </div>
            <div>
              <h1 className="text-2xl font-orbitron font-bold text-white neon-text">
                페르소나 다이어리
              </h1>
              <p className="text-sm text-gray-300 font-noto">MKM12 기반 개인 건강 일기</p>
            </div>
          </div>
          
          <Link 
            href="/"
            className="glass-button text-gray-300 hover:text-eno-400 transition-colors font-noto"
          >
            🏠 홈으로
          </Link>
        </div>
      </header>

      <main className="relative z-10 px-6 pb-20">
        <div className="max-w-7xl mx-auto">
          {/* 히어로 섹션 */}
          <section className="text-center py-16">
            <h2 className="text-5xl md:text-6xl font-orbitron font-bold mb-6">
              <span className="neon-text">당신의 하루를</span>
              <br/>
              <span className="text-eno-400">MKM12로 기록하세요</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12 font-noto leading-relaxed">
              매일의 기분, 에너지, 활동을 기록하고<br/>
              <span className="text-eno-400 font-semibold">개인 맞춤형 페르소나</span>를 발견하세요
            </p>
          </section>

          {/* 메인 컨텐츠 */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* 왼쪽: 일기 작성 */}
            <div className="lg:col-span-2">
              <div className="glass-card p-8 rounded-2xl mb-8">
                <h3 className="text-2xl font-orbitron font-bold text-white mb-6 neon-text">
                  📝 오늘의 기록
                </h3>
                
                <div className="space-y-6">
                  {/* 날짜 선택 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">날짜</label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20 transition-all"
                    />
                  </div>

                  {/* 기분 선택 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">오늘의 기분</label>
                    <div className="grid grid-cols-5 gap-3">
                      {moodOptions.map((mood) => (
                        <button
                          key={mood}
                          onClick={() => setCurrentEntry({...currentEntry, mood})}
                          className={`p-3 rounded-lg border transition-all ${
                            currentEntry.mood === mood
                              ? 'border-eno-400 bg-eno-400/20 text-eno-400'
                              : 'border-slate-600 text-gray-300 hover:border-slate-500'
                          }`}
                        >
                          {mood}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 에너지 레벨 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">
                      에너지 레벨: {currentEntry.energy}/10
                    </label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={currentEntry.energy}
                      onChange={(e) => setCurrentEntry({...currentEntry, energy: parseInt(e.target.value)})}
                      className="w-full h-3 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-sm text-gray-400 mt-1">
                      <span>매우 낮음</span>
                      <span>매우 높음</span>
                    </div>
                  </div>

                  {/* 활동 기록 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">주요 활동</label>
                    <div className="space-y-2">
                      {currentEntry.activities.map((activity, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={activity}
                            onChange={(e) => {
                              const newActivities = [...currentEntry.activities];
                              newActivities[index] = e.target.value;
                              setCurrentEntry({...currentEntry, activities: newActivities});
                            }}
                            className="flex-1 p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20"
                            placeholder="활동을 입력하세요"
                          />
                          <button
                            onClick={() => {
                              const newActivities = currentEntry.activities.filter((_, i) => i !== index);
                              setCurrentEntry({...currentEntry, activities: newActivities});
                            }}
                            className="p-3 text-red-400 hover:text-red-300 transition-colors"
                          >
                            ❌
                          </button>
                        </div>
                      ))}
                      <button
                        onClick={() => setCurrentEntry({
                          ...currentEntry, 
                          activities: [...currentEntry.activities, '']
                        })}
                        className="w-full p-3 border-2 border-dashed border-slate-600 rounded-lg text-slate-400 hover:border-slate-500 hover:text-slate-300 transition-all"
                      >
                        + 활동 추가
                      </button>
                    </div>
                  </div>

                  {/* 페르소나 선택 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">MKM12 페르소나</label>
                    <div className="grid grid-cols-3 gap-3">
                      {personaTypes.map((persona) => (
                        <button
                          key={persona}
                          onClick={() => setCurrentEntry({...currentEntry, persona})}
                          className={`p-3 rounded-lg border transition-all ${
                            currentEntry.persona === persona
                              ? 'border-eno-400 bg-eno-400/20 text-eno-400'
                              : 'border-slate-600 text-gray-300 hover:border-slate-500'
                          }`}
                        >
                          {persona}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 인사이트 */}
                  <div>
                    <label className="block text-gray-300 font-semibold mb-2">오늘의 인사이트</label>
                    <textarea
                      value={currentEntry.insights}
                      onChange={(e) => setCurrentEntry({...currentEntry, insights: e.target.value})}
                      rows={4}
                      className="w-full p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20 resize-none"
                      placeholder="오늘 하루를 돌아보며 느낀 점을 기록하세요..."
                    />
                  </div>

                  {/* 저장 버튼 */}
                  <button className="w-full glass-button text-lg py-4 font-semibold neon-glow">
                    💾 일기 저장하기
                  </button>
                </div>
              </div>
            </div>

            {/* 오른쪽: 통계 및 인사이트 */}
            <div className="space-y-6">
              {/* 오늘의 요약 */}
              <div className="glass-card p-6 rounded-2xl">
                <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                  📊 오늘의 요약
                </h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">기분</span>
                    <span className="text-white font-semibold">{currentEntry.mood}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">에너지</span>
                    <span className="text-white font-semibold">{currentEntry.energy}/10</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">활동</span>
                    <span className="text-white font-semibold">{currentEntry.activities.length}개</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">페르소나</span>
                    <span className="text-eno-400 font-semibold">{currentEntry.persona}</span>
                  </div>
                </div>
              </div>

              {/* 주간 트렌드 */}
              <div className="glass-card p-6 rounded-2xl">
                <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                  📈 주간 트렌드
                </h4>
                <div className="space-y-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-eno-400 neon-glow">7일 연속</div>
                    <div className="text-sm text-gray-400">일기 작성</div>
                  </div>
                  <div className="h-20 bg-slate-800 rounded-lg flex items-end justify-center p-2">
                    <div className="flex items-end space-x-1">
                      {[65, 80, 45, 90, 70, 85, 75].map((height, index) => (
                        <div
                          key={index}
                          className="w-3 bg-gradient-to-t from-eno-400 to-eno-600 rounded-t"
                          style={{ height: `${height}%` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* MKM12 인사이트 */}
              <div className="glass-card p-6 rounded-2xl">
                <h4 className="text-lg font-orbitron font-bold text-white mb-4 neon-text">
                  🧠 MKM12 인사이트
                </h4>
                <div className="space-y-3 text-sm">
                  <p className="text-gray-300">
                    <span className="text-eno-400 font-semibold">태양형(A1)</span> 페르소나가 
                    이번 주에 가장 자주 나타났습니다.
                  </p>
                  <p className="text-gray-300">
                    에너지 레벨이 높을 때 <span className="text-eno-400 font-semibold">창의적 활동</span>을 
                    선호하는 경향이 있습니다.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
