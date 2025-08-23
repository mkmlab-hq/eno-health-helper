# 엔오건강도우미 Frontend

엔오플렉스 건강기능식품과 함께하는 혁신적인 건강 측정 웹 애플리케이션입니다.

## 🚀 주요 기능

- **rPPG 기술 기반 심박수 측정**: 카메라를 통한 비접촉 심박수 및 심박변이도 측정
- **AI 음성 분석**: 음성 특성을 분석하여 건강 상태 평가
- **실시간 건강 모니터링**: 측정 결과를 실시간으로 확인하고 저장
- **개인 맞춤형 권장사항**: 측정 결과를 바탕으로 한 건강 관리 방안 제시
- **다중 인증 방식**: 이메일/비밀번호, Google, 카카오 로그인 지원

## 🛠 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Firebase Authentication
- **Database**: Cloud Firestore
- **Hosting**: Firebase Hosting (준비됨)
- **Fonts**: Orbitron (제목), Noto Sans KR (본문)

## 🎨 디자인 가이드라인

- **테마**: 미래지향적 다크 모드, Glassmorphism 효과
- **색상**: 청록색(Cyan)/하늘색(Sky) 네온 효과
- **애니메이션**: 부드러운 전환(Fade-in, Slide-up) 및 인터랙티브한 호버 효과
- **UI**: 반투명 유리 질감의 모던한 인터페이스

## 📁 프로젝트 구조

```
src/
├── app/                    # Next.js App Router
│   ├── login/            # 로그인 페이지
│   ├── signup/           # 회원가입 페이지
│   ├── measure/          # 건강 측정 페이지
│   ├── result/           # 측정 결과 페이지
│   ├── globals.css       # 전역 스타일
│   ├── layout.tsx        # 루트 레이아웃
│   └── page.tsx          # 메인 페이지
├── context/              # React Context
│   └── AuthContext.tsx   # 인증 상태 관리
└── lib/                  # 유틸리티 라이브러리
    └── firebase.ts       # Firebase 설정 및 함수
```

## 🚀 시작하기

### 1. 의존성 설치

```bash
npm install
```

### 2. Firebase 설정

1. [Firebase Console](https://console.firebase.google.com/)에서 프로젝트 생성
2. `FIREBASE_SETUP.md` 파일의 안내에 따라 설정
3. 프로젝트 루트에 `.env.local` 파일 생성 및 환경 변수 설정

### 3. 개발 서버 실행

```bash
npm run dev
```

4. 브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

## 🔧 환경 변수

프로젝트 루트에 `.env.local` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# Firebase 설정
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id

# 카카오 로그인 설정 (선택사항)
NEXT_PUBLIC_KAKAO_APP_KEY=your_kakao_app_key_here
NEXT_PUBLIC_KAKAO_REDIRECT_URI=http://localhost:3000/auth/kakao/callback
```

## 📱 사용법

### 1. 회원가입/로그인
- 이메일/비밀번호 또는 Google 계정으로 가입/로그인
- 카카오 로그인은 현재 UI만 준비됨 (추후 구현 예정)

### 2. 건강 측정
- 카메라 권한 허용 후 얼굴 측정 시작
- 음성 권한 허용 후 "아" 소리로 음성 측정
- AI 분석을 통한 종합 건강 지표 도출

### 3. 결과 확인 및 저장
- 측정 결과를 상세하게 확인
- Firebase에 결과 저장
- 건강 권장사항 확인

## 🔒 보안

- Firebase Authentication을 통한 안전한 사용자 인증
- Firestore 보안 규칙을 통한 데이터 접근 제어
- 환경 변수를 통한 API 키 보호

## 🚧 개발 상태

- [x] Firebase 통합
- [x] 사용자 인증 시스템
- [x] 건강 측정 UI/UX
- [x] 결과 저장 및 조회
- [x] 반응형 디자인
- [ ] 카카오 로그인 구현
- [ ] 실제 rPPG 알고리즘 연동
- [ ] 음성 분석 알고리즘 연동

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.
