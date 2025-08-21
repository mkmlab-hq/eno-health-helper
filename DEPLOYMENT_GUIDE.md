# 🚀 eno.no1kmedi.com 배포 가이드

## 📋 **배포 개요**

**엔오건강도우미** 웹앱을 `eno.no1kmedi.com` 도메인에 배포하는 방법을 안내합니다.

## 🌐 **도메인 정보**

- **도메인**: `eno.no1kmedi.com`
- **서비스**: 엔오건강도우미 (ENO Health Helper)
- **QR 코드**: 엔오플렉스 포장지에 이미 인쇄됨
- **연결**: QR 스캔 시 해당 도메인으로 이동

## 🎯 **배포 옵션**

### **옵션 1: Vercel 배포 (권장)**

#### **1단계: Vercel 프로젝트 생성**
```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 로그인
vercel login

# 프로젝트 배포
cd eno-health-helper
vercel --prod
```

#### **2단계: 도메인 연결**
1. Vercel 대시보드에서 프로젝트 선택
2. Settings → Domains
3. `eno.no1kmedi.com` 도메인 추가
4. DNS 설정 안내에 따라 네임서버 변경

#### **3단계: 환경 변수 설정**
Vercel 대시보드에서:
```
NEXT_PUBLIC_API_URL=https://eno.no1kmedi.com/api
NEXT_PUBLIC_APP_NAME=엔오건강도우미
NEXT_PUBLIC_DOMAIN=eno.no1kmedi.com
```

### **옵션 2: Netlify 배포**

#### **1단계: Netlify 배포**
```bash
# Netlify CLI 설치
npm install -g netlify-cli

# 프로젝트 빌드
cd frontend
npm run build

# Netlify 배포
netlify deploy --prod --dir=out
```

#### **2단계: 도메인 연결**
1. Netlify 대시보드에서 Site settings
2. Domain management → Custom domains
3. `eno.no1kmedi.com` 추가
4. DNS 설정 업데이트

### **옵션 3: AWS Amplify 배포**

#### **1단계: Amplify 콘솔 설정**
1. AWS Amplify 콘솔 접속
2. New app → Host web app
3. GitHub 연결 및 레포지토리 선택
4. 빌드 설정 자동 감지

#### **2단계: 도메인 연결**
1. App settings → Domain management
2. Add domain → `eno.no1kmedi.com`
3. SSL 인증서 자동 발급

## 🔧 **DNS 설정**

### **네임서버 변경 (Vercel 사용 시)**
```
Name Server 1: ns1.vercel-dns.com
Name Server 2: ns2.vercel-dns.com
Name Server 3: ns3.vercel-dns.com
Name Server 4: ns4.vercel-dns.com
```

### **CNAME 설정 (Netlify/Amplify 사용 시)**
```
Type: CNAME
Name: eno
Value: your-app.netlify.app (또는 amplify.app)
TTL: 3600
```

## 📱 **PWA 설정 확인**

### **매니페스트 파일**
- `/public/manifest.json` 파일이 올바르게 생성되었는지 확인
- 아이콘 파일들이 `/public/icons/` 폴더에 존재하는지 확인

### **서비스 워커**
- `/public/sw.js` 파일이 올바르게 생성되었는지 확인
- 브라우저 개발자 도구에서 서비스 워커 등록 상태 확인

### **HTTPS 필수**
- PWA 기능을 위해서는 HTTPS가 필수
- Vercel, Netlify, Amplify 모두 자동으로 SSL 인증서 제공

## 🧪 **배포 후 테스트**

### **1. 기본 기능 테스트**
- [ ] 메인 페이지 로딩 확인
- [ ] QR 코드 스캔 기능 테스트
- [ ] 카메라/마이크 권한 요청 테스트
- [ ] PWA 설치 가능 여부 확인

### **2. 모바일 최적화 테스트**
- [ ] 반응형 디자인 확인
- [ ] 터치 인터페이스 테스트
- [ ] PWA 홈 화면 추가 테스트
- [ ] 오프라인 동작 테스트

### **3. 성능 테스트**
- [ ] 페이지 로딩 속도 측정
- [ ] Core Web Vitals 점수 확인
- [ ] 모바일 성능 테스트
- [ ] PWA 성능 점수 확인

## 🔒 **보안 설정**

### **CSP (Content Security Policy)**
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline' 'unsafe-eval'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:; 
               connect-src 'self' https:;">
```

### **보안 헤더**
```javascript
// next.config.js
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'X-Frame-Options',
          value: 'DENY',
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff',
        },
        {
          key: 'Referrer-Policy',
          value: 'strict-origin-when-cross-origin',
        },
      ],
    },
  ];
},
```

## 📊 **모니터링 설정**

### **Vercel Analytics**
```bash
# Vercel Analytics 설치
npm install @vercel/analytics

# _app.tsx에 추가
import { Analytics } from '@vercel/analytics/react';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Analytics />
    </>
  );
}
```

### **Google Analytics**
```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🚨 **문제 해결**

### **일반적인 배포 문제**

#### **빌드 실패**
```bash
# 의존성 문제 해결
rm -rf node_modules package-lock.json
npm install

# 빌드 캐시 정리
rm -rf .next
npm run build
```

#### **도메인 연결 실패**
- DNS 전파 대기 (최대 48시간)
- 네임서버 설정 확인
- SSL 인증서 발급 상태 확인

#### **PWA 동작 안함**
- HTTPS 확인
- 매니페스트 파일 경로 확인
- 서비스 워커 등록 상태 확인

## 📚 **다음 단계**

1. **백엔드 API 배포**: FastAPI 서버를 별도 서버에 배포
2. **데이터베이스 설정**: PostgreSQL 데이터베이스 구축
3. **모니터링 시스템**: 성능 및 오류 모니터링 구축
4. **CI/CD 파이프라인**: 자동 배포 시스템 구축

## 🤝 **지원**

- **Vercel 지원**: [Vercel Docs](https://vercel.com/docs)
- **Netlify 지원**: [Netlify Docs](https://docs.netlify.com)
- **AWS Amplify 지원**: [AWS Amplify Docs](https://docs.amplify.aws)

---

**성공적인 배포를 기원합니다! 🚀✨** 