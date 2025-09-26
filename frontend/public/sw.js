// 엔오건강도우미 PWA 서비스 워커
const CACHE_NAME = 'eno-health-helper-v2.0.0';
const urlsToCache = [
  '/',
  '/measure',
  '/result',
  '/dashboard',
  '/static/css/app.css',
  '/static/js/app.js',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Service Worker 설치
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Cache installation failed:', error);
      })
  );
});

// Service Worker 활성화
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// 네트워크 요청 가로채기
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 캐시에서 찾은 경우 반환
        if (response) {
          return response;
        }

        // 네트워크 요청 시도
        return fetch(event.request)
          .then((response) => {
            // 유효한 응답이 아닌 경우 캐시하지 않음
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 응답을 복제하여 캐시에 저장
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // 네트워크 실패 시 오프라인 페이지 반환
            if (event.request.mode === 'navigate') {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// 백그라운드 동기화
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// 백그라운드 동기화 작업
async function doBackgroundSync() {
  try {
    // 오프라인 상태에서 수집된 데이터를 서버로 전송
    const offlineData = await getOfflineData();
    if (offlineData.length > 0) {
      await sendOfflineData(offlineData);
      await clearOfflineData();
    }
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// 오프라인 데이터 가져오기
async function getOfflineData() {
  try {
    const db = await openDB();
    const transaction = db.transaction(['measurements'], 'readonly');
    const store = transaction.objectStore('measurements');
    return await store.getAll();
  } catch (error) {
    console.error('Failed to get offline data:', error);
    return [];
  }
}

// 오프라인 데이터 서버 전송
async function sendOfflineData(data) {
  try {
    const response = await fetch('/api/measurements/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error('Failed to send offline data');
    }
    
    console.log('Offline data sent successfully');
  } catch (error) {
    console.error('Failed to send offline data:', error);
    throw error;
  }
}

// 오프라인 데이터 정리
async function clearOfflineData() {
  try {
    const db = await openDB();
    const transaction = db.transaction(['measurements'], 'readwrite');
    const store = transaction.objectStore('measurements');
    await store.clear();
    console.log('Offline data cleared');
  } catch (error) {
    console.error('Failed to clear offline data:', error);
  }
}

// IndexedDB 열기
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('ENOHealthDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // 측정 데이터 저장소 생성
      if (!db.objectStoreNames.contains('measurements')) {
        const store = db.createObjectStore('measurements', { 
          keyPath: 'id', 
          autoIncrement: true 
        });
        store.createIndex('timestamp', 'timestamp', { unique: false });
      }
    };
  });
}

// 푸시 알림 처리
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '새로운 건강 측정 알림이 있습니다.',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '확인하기',
        icon: '/icons/checkmark.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/icons/x-mark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('ENO Health Helper', options)
  );
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

// 메시지 처리
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
}); 