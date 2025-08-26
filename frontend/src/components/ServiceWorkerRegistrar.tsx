"use client";

import { useEffect } from 'react';

export default function ServiceWorkerRegistrar() {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!('serviceWorker' in navigator)) return;

    const register = async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
        if (registration?.update) {
          registration.update().catch(() => {});
        }

        // Prompt to skipWaiting when a new SW is found
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          // no-op but ensures page picks up new SW
        });

        if (registration?.waiting) {
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Service worker registration failed:', error);
      }
    };

    // Register after page is idle for quicker TTI on mobile
    if ('requestIdleCallback' in window) {
      (window as any).requestIdleCallback(register);
    } else {
      setTimeout(register, 1500);
    }
  }, []);

  return null;
}

