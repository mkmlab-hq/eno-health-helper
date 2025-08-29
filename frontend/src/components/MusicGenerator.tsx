'use client';

import React from 'react';

interface MusicGeneratorProps {
  emotionData?: any;
  onMusicGenerated?: (music: any) => void;
}

export default function MusicGenerator({ emotionData, onMusicGenerated }: MusicGeneratorProps) {
  // 임시로 비활성화 - 빌드 오류 수정 후 활성화 예정
  return (
    <div className="p-4 text-center text-gray-500">
      음악 생성 기능이 일시적으로 비활성화되었습니다.
    </div>
  );
} 