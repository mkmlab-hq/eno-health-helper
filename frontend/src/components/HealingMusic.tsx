import React, { useState, useEffect } from 'react';

interface HealingMusicProps {
  healthData?: any;
  onClose?: () => void;
}

export default function HealingMusic({ healthData, onClose }: HealingMusicProps) {
  return (
    <div className="healing-music-container">
      <h2>Healing Music</h2>
      <p>건강 데이터 기반 맞춤 음악을 생성합니다.</p>
      {onClose && (
        <button onClick={onClose} className="close-button">
          닫기
        </button>
      )}
    </div>
  );
} 
