'use client';

import React, { useState } from 'react';

interface PrivacyConsentProps {
  onConsent: (consent: {
    requiredConsent: boolean;
    optionalConsent: boolean;
  }) => void;
}

const PrivacyConsent: React.FC<PrivacyConsentProps> = ({ onConsent }) => {
  const [requiredConsent, setRequiredConsent] = useState(false);
  const [optionalConsent, setOptionalConsent] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const handleConsent = () => {
    onConsent({
      requiredConsent,
      optionalConsent
    });
  };

  return (
    <div className="glass-card p-6 border-2 border-neon-cyan mt-6">
      <h3 className="text-xl font-bold text-neon-cyan mb-4">
        🛡️ 개인정보보호 동의
      </h3>
      
      <div className="space-y-4 mb-6">
        {/* 필수 동의 항목 */}
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            id="required-consent"
            checked={requiredConsent}
            onChange={(e) => setRequiredConsent(e.target.checked)}
            className="mt-1 w-5 h-5 bg-gray-800 border-gray-600 text-neon-cyan focus:ring-neon-cyan rounded"
          />
          <div className="flex-1">
            <label htmlFor="required-consent" className="font-medium text-white cursor-pointer">
              필수 동의 항목
            </label>
            <p className="text-sm text-gray-400 mt-1">
              얼굴 영상, 음성 데이터 수집 및 분석, 측정 결과 저장
            </p>
          </div>
        </div>
        
        {/* 선택 동의 항목 */}
        <div className="flex items-start space-x-3">
          <input
            type="checkbox"
            id="optional-consent"
            checked={optionalConsent}
            onChange={(e) => setOptionalConsent(e.target.checked)}
            className="mt-1 w-5 h-5 bg-gray-800 border-gray-600 text-neon-cyan focus:ring-neon-cyan rounded"
          />
          <div className="flex-1">
            <label htmlFor="optional-consent" className="font-medium text-white cursor-pointer">
              선택 동의 항목
            </label>
            <p className="text-sm text-gray-400 mt-1">
              개인 맞춤 건강 조언, 서비스 개선을 위한 데이터 활용
            </p>
          </div>
        </div>
      </div>

      {/* 상세 내용 보기 */}
      <div className="mb-6">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-neon-cyan hover:text-neon-sky text-sm underline flex items-center space-x-2"
        >
          <span>📋</span>
          <span>{showDetails ? '상세 내용 숨기기' : '상세 내용 보기'}</span>
        </button>
        
        {showDetails && (
          <div className="mt-3 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
            <h4 className="font-medium text-white mb-2">개인정보 수집 및 이용 안내</h4>
            <div className="text-sm text-gray-300 space-y-2">
              <p><strong>수집 목적:</strong> AI 기반 건강 상태 분석 및 개인 맞춤 건강 조언 제공</p>
              <p><strong>수집 항목:</strong> 얼굴 영상, 음성 데이터, 측정 결과</p>
              <p><strong>보관 기간:</strong> 서비스 이용 종료 시까지 (최대 5년)</p>
              <p><strong>처리 방식:</strong> 비식별 처리 후 암호화 저장</p>
              <p><strong>사용자 권리:</strong> 언제든지 데이터 삭제 요청 가능</p>
            </div>
          </div>
        )}
      </div>

      {/* 동의 후 측정 시작 버튼 */}
      <button
        onClick={handleConsent}
        disabled={!requiredConsent}
        className={`w-full py-3 px-6 rounded-lg font-bold transition-all duration-300 ${
          requiredConsent
            ? 'bg-gradient-to-r from-neon-cyan to-neon-sky hover:from-neon-sky hover:to-neon-cyan text-gray-900 shadow-lg hover:shadow-neon-cyan/50'
            : 'bg-gray-600 text-gray-400 cursor-not-allowed'
        }`}
      >
        {requiredConsent ? '동의하고 측정 시작하기' : '필수 동의 후 측정 가능'}
      </button>

      {/* 개인정보보호 관련 안내 */}
      <p className="text-xs text-gray-500 text-center mt-4">
        모든 데이터는 비식별 처리되어 안전하게 관리됩니다.
      </p>
    </div>
  );
};

export default PrivacyConsent;
