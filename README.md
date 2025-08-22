# 엔오건강도우미 (ENO Health Helper)

AI 기반 rPPG와 음성 분석을 통한 정확한 건강 측정 서비스

## 🚀 **즉시 배포 및 확인 방법**

### **GitHub Pages 설정 (필수!)**

GitHub Pages가 작동하지 않는 경우 다음 단계를 따라 설정하세요:

1. **GitHub 저장소 설정**:
   - [GitHub 저장소](https://github.com/mkmlab-hq/eno-health-helper) 접속
   - Settings → Pages 클릭
   - Source를 "Deploy from a branch"로 설정
   - Branch를 "main"으로 설정
   - Folder를 "/ (root)"로 설정
   - Save 클릭

2. **대기 시간**: 설정 후 5-10분 대기

3. **배포 확인**: `https://mkmlab-hq.github.io/eno-health-helper` 접속

### **대안 배포 방법 (더 빠름!)**

#### **방법 1: Netlify (2분 - 추천!)**
1. [Netlify](https://netlify.com) 접속
2. `deploy-ready` 폴더를 Netlify에 드래그 앤 드롭
3. 자동으로 배포 완료!

#### **방법 2: Vercel (5분)**
1. [Vercel](https://vercel.com) 접속
2. GitHub 저장소 연결
3. 자동으로 배포 완료!

## 🚀 주요 기능

- **rPPG 건강 측정**: 카메라를 통한 비접촉 심박수, 심박변이도, 스트레스 수준 측정
- **음성 품질 분석**: Jitter, Shimmer 등 음성 지표를 통한 건강 상태 평가
- **Firebase 통합**: 안전한 사용자 인증 및 데이터 저장
- **실시간 모니터링**: 건강 변화 추이 관리
- **미래지향적 UI**: Glassmorphism 디자인과 네온 효과

## 🛠️ 기술 스택

### Frontend
- **Next.js 14** - React 기반 풀스택 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 유틸리티 퍼스트 CSS 프레임워크
- **Lucide React** - 아이콘 라이브러리

### Backend & Database
- **Firebase Authentication** - 사용자 인증
- **Cloud Firestore** - NoSQL 데이터베이스
- **Firebase Storage** - 파일 저장소

### AI & Analysis
- **rPPG (Remote Photoplethysmography)** - 비접촉 심박수 측정
- **음성 분석** - Jitter, Shimmer 등 음성 품질 지표

## 📱 사용 방법

1. **계정 생성**: 간단한 회원가입으로 시작
2. **얼굴 촬영**: 카메라를 정면으로 바라보고 정지 상태 유지
3. **음성 녹음**: "아" 소리를 10초간 지속해서 발성
4. **결과 확인**: AI 분석 결과 및 건강 지표 확인
5. **데이터 저장**: Firebase에 측정 결과 저장

## 🚀 빠른 시작

### **1. 저장소 클론**
```bash
git clone https://github.com/mkmlab-hq/eno-health-helper.git
cd eno-health-helper
```

### **2. 의존성 설치**
```bash
cd frontend
npm install
```

### **3. Firebase 설정**
1. [Firebase Console](https://console.firebase.google.com)에서 새 프로젝트 생성
2. 웹 앱 추가 및 설정 값 복사
3. `.env.local` 파일 생성 및 Firebase 설정 값 입력:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### **4. 개발 서버 실행**
```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

## 🔧 환경 설정

### Firebase 설정
1. **Authentication**: 이메일/비밀번호 로그인 활성화
2. **Firestore Database**: 데이터베이스 생성 및 보안 규칙 설정
3. **Storage**: 파일 업로드 권한 설정

### 보안 규칙 예시
```javascript
// Firestore 보안 규칙
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /measurements/{document} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.userId;
    }
  }
}
```

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── login/          # 로그인 페이지
│   │   ├── signup/         # 회원가입 페이지
│   │   ├── measure/        # 건강 측정 페이지
│   │   ├── result/         # 결과 페이지
│   │   ├── layout.tsx      # 루트 레이아웃
│   │   └── page.tsx        # 메인 페이지
│   ├── context/            # React Context
│   │   └── AuthContext.tsx # 인증 상태 관리
│   ├── lib/                # 유틸리티
│   │   └── firebase.ts     # Firebase 설정
│   └── globals.css         # 전역 스타일
├── tailwind.config.js      # Tailwind CSS 설정
├── postcss.config.js       # PostCSS 설정
└── package.json            # 의존성 관리
```

## 🎨 디자인 시스템

### 테마
- **미래지향적 다크 모드**: 깊이감 있는 어두운 배경
- **Glassmorphism**: 반투명 유리 질감 효과
- **네온 효과**: 청록색(Cyan)/하늘색(Sky) 강조색

### 폰트
- **Orbitron**: 주요 제목용 (미래지향적)
- **Noto Sans KR**: 본문용 (한글 최적화)

### 애니메이션
- **부드러운 전환**: Fade-in, Slide-up 효과
- **인터랙티브 호버**: 마우스 오버 시 반응
- **로딩 애니메이션**: 진행 상태 표시

## 🔒 보안 기능

- **Firebase Authentication**: 안전한 사용자 인증
- **환경 변수**: 민감한 정보 보호
- **권한 기반 접근**: 사용자별 데이터 격리
- **HTTPS**: 모든 통신 암호화

## 📊 건강 지표

### rPPG 측정
- **심박수 (BPM)**: 정상 범위 60-100
- **심박변이도 (HRV)**: 스트레스 및 회복력 지표
- **스트레스 수준**: 낮음/보통/높음

### 음성 분석
- **Jitter**: 음성 주파수 변동성
- **Shimmer**: 음성 진폭 변동성
- **전체 음성 품질**: 건강 상태 반영

## 🚀 배포

### Vercel 배포 (권장)
```bash
npm run build
vercel --prod
```

### Docker 배포
```bash
docker build -t eno-health-helper .
docker run -p 3000:3000 eno-health-helper
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/mkmlab-hq/eno-health-helper/issues)
- **문의**: your-email@example.com
- **문서**: [Wiki](https://github.com/mkmlab-hq/eno-health-helper/wiki)

## 🙏 감사의 말

- Firebase 팀 - 강력한 백엔드 서비스 제공
- Next.js 팀 - 훌륭한 React 프레임워크
- Tailwind CSS 팀 - 효율적인 CSS 프레임워크
- 모든 오픈소스 기여자들

---

**엔오건강도우미**와 함께 AI 기술로 더 건강한 삶을 만들어가세요! 🚀💪 