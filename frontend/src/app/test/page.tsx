'use client';

import React, { useState, useRef } from 'react';

export default function TestPage() {
  const [cameraPermission, setCameraPermission] = useState<string>('대기 중');
  const [microphonePermission, setMicrophonePermission] = useState<string>('대기 중');
  const videoRef = useRef<HTMLVideoElement>(null);

  const testCamera = async () => {
    try {
      setCameraPermission('테스트 중...');
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setCameraPermission('✅ 성공');
    } catch (error) {
      setCameraPermission(`❌ 실패: ${error}`);
    }
  };

  const testMicrophone = async () => {
    try {
      setMicrophonePermission('테스트 중...');
      await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicrophonePermission('✅ 성공');
    } catch (error) {
      setMicrophonePermission(`❌ 실패: ${error}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">카메라/마이크 테스트</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 카메라 테스트 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">카메라 테스트</h2>
            <button
              onClick={testCamera}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4"
            >
              카메라 권한 요청
            </button>
            <p className="mb-2">상태: {cameraPermission}</p>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-48 bg-gray-200 rounded"
            />
          </div>

          {/* 마이크 테스트 */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">마이크 테스트</h2>
            <button
              onClick={testMicrophone}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mb-4"
            >
              마이크 권한 요청
            </button>
            <p>상태: {microphonePermission}</p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <a
            href="/"
            className="bg-gray-500 text-white px-6 py-2 rounded hover:bg-gray-600"
          >
            홈으로 돌아가기
          </a>
        </div>
      </div>
    </div>
  );
} 