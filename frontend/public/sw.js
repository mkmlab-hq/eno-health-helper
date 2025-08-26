// 엔오건강도우미 PWA 서비스 워커
const CACHE_NAME = 'eno-health-helper-v1.1.0';
const OFFLINE_URL = '/offline.html';
const urlsToCache = [
  '/',
  '/measurement',
  '/results',
  '/tracking',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  OFFLINE_URL
];

// 서비스 워커 설치
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('캐시가 열렸습니다');
        return cache.addAll(urlsToCache);
      })
  );
});

// 서비스 워커 활성화
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('이전 캐시를 삭제합니다:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// 네트워크 요청 가로채기
self.addEventListener('fetch', (event) => {
  const { request } = event;
  // Only handle GET
  if (request.method !== 'GET') return;

  // HTML navigation requests: Network-first with offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((networkResponse) => {
          const copy = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          return networkResponse;
        })
        .catch(async () => {
          const cached = await caches.match(request);
          return cached || caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  // For same-origin static assets: Stale-while-revalidate
  if (request.url.startsWith(self.location.origin)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const networkFetch = fetch(request)
          .then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              const copy = networkResponse.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
            }
            return networkResponse;
          })
          .catch(() => cached);

        return cached || networkFetch;
      })
    );
  }
});

// Support manual skipWaiting from client
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 백그라운드 동기화 (오프라인 데이터 동기화)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

// 백그라운드 동기화 함수
function doBackgroundSync() {
  // 오프라인에서 수집된 데이터를 서버로 전송
  return new Promise((resolve) => {
    console.log('백그라운드 동기화를 수행합니다');
    resolve();
  });
}

// 푸시 알림 처리
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : '새로운 알림이 있습니다',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '확인하기',
        icon: '/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: '닫기',
        icon: '/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('엔오건강도우미', options)
  );
});

// 알림 클릭 처리
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
}); 