'use client';

import React from 'react';

export default function Features() {
  return (
    <section id="tech" className="py-20">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-white mb-12 font-orbitron">핵심 기술력</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
            <h3 className="text-xl font-bold text-sky-400 mb-2">rPPG 건강 측정</h3>
            <p className="text-gray-400 text-sm">
              카메라를 통해 심박수, HRV, 스트레스 수준을 비접촉으로 정밀하게 측정하는 기술
            </p>
          </div>
          <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
            <h3 className="text-xl font-bold text-sky-400 mb-2">음성 품질 분석</h3>
            <p className="text-gray-400 text-sm">
              목소리의 미세 떨림(Jitter, Shimmer)을 분석하여 건강 상태 및 스트레스를 추론하는 기술
            </p>
          </div>
          <div className="glassmorphism p-6 rounded-lg transition-all duration-300 feature-card">
            <h3 className="text-xl font-bold text-sky-400 mb-2">AI 기반 기질 분석</h3>
            <p className="text-gray-400 text-sm">
              57만개 동적 데이터를 통해 4가지 '디지털 기질'을 발견하고 사상의학과 연결하는 기술
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
