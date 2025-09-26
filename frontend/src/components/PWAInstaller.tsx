'use client';

import { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export default function PWAInstaller() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // PWA 지원 여부 확인
    const checkPWASupport = () => {
      const isSupported = 'serviceWorker' in navigator && 'PushManager' in window;
      setIsSupported(isSupported);
      
      if (isSupported) {
        // Service Worker 등록
        registerServiceWorker();
        
        // 설치 상태 확인
        checkInstallStatus();
      }
    };

    // Service Worker 등록
    const registerServiceWorker = async () => {
      try {
        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.register('/sw.js');
          console.log('Service Worker registered:', registration);
          
          // 업데이트 확인
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // 새 버전이 설치됨
                  showUpdateNotification();
                }
              });
            }
          });
        }
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    };

    // 설치 상태 확인
    const checkInstallStatus = () => {
      if (window.matchMedia('(display-mode: standalone)').matches) {
        setIsInstalled(true);
      }
    };

    // 설치 프롬프트 이벤트 리스너
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };

    // 설치 완료 이벤트 리스너
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setDeferredPrompt(null);
      console.log('PWA was installed');
    };

    checkPWASupport();

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // PWA 설치
  const handleInstall = async () => {
    if (!deferredPrompt) return;

    try {
      // 설치 프롬프트 표시
      await deferredPrompt.prompt();
      
      // 사용자 선택 대기
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      
      setDeferredPrompt(null);
    } catch (error) {
      console.error('Installation failed:', error);
    }
  };

  // 업데이트 알림 표시
  const showUpdateNotification = () => {
    if (confirm('새로운 버전이 사용 가능합니다. 업데이트하시겠습니까?')) {
      window.location.reload();
    }
  };

  // PWA가 지원되지 않는 경우
  if (!isSupported) {
    return null;
  }

  // 이미 설치된 경우
  if (isInstalled) {
    return (
      <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg">
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          <span>앱으로 설치됨</span>
        </div>
      </div>
    );
  }

  // 설치 가능한 경우
  if (deferredPrompt) {
    return (
      <div className="fixed bottom-4 right-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white px-6 py-3 rounded-lg shadow-lg cursor-pointer hover:from-cyan-600 hover:to-blue-700 transition-all duration-300">
        <div className="flex items-center space-x-3" onClick={handleInstall}>
          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          <div>
            <div className="font-semibold">앱으로 설치</div>
            <div className="text-sm opacity-90">홈 화면에 추가</div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}

// PWA 설치 상태를 전역으로 관리하는 훅
export function usePWAStatus() {
  const [isInstalled, setIsInstalled] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    const checkStatus = () => {
      const supported = 'serviceWorker' in navigator && 'PushManager' in window;
      const installed = window.matchMedia('(display-mode: standalone)').matches;
      
      setIsSupported(supported);
      setIsInstalled(installed);
    };

    checkStatus();
    
    const mediaQuery = window.matchMedia('(display-mode: standalone)');
    mediaQuery.addEventListener('change', checkStatus);
    
    return () => mediaQuery.removeEventListener('change', checkStatus);
  }, []);

  return { isInstalled, isSupported };
}
