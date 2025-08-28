# 🔥 Firebase 설정 가이드

## 📋 Firebase Console에서 해야 할 일

### 1. 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com) 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름: `eno-health-helper`
4. Google Analytics: 비활성화

### 2. 웹 앱 추가
1. 프로젝트 대시보드에서 "웹 앱에 Firebase 추가" 클릭
2. 앱 닉네임: `eno-health-helper-web`
3. "Firebase Hosting 설정" 체크 해제
4. "앱 등록" 클릭

### 3. 설정 정보 복사
```javascript
const firebaseConfig = {
  apiKey: "실제_API_키_입력",
  authDomain: "eno-health-helper.firebaseapp.com",
  projectId: "eno-health-helper",
  storageBucket: "eno-health-helper.appspot.com",
  messagingSenderId: "실제_메시징_송신자_ID",
  appId: "실제_앱_ID"
};
```

### 4. Vercel 환경 변수 설정
```bash
# Vercel CLI로 환경 변수 설정
npx vercel env add NEXT_PUBLIC_FIREBASE_API_KEY
npx vercel env add NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
npx vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID
npx vercel env add NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
npx vercel env add NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
npx vercel env add NEXT_PUBLIC_FIREBASE_APP_ID
```

### 5. Firebase 서비스 활성화
- **Authentication**: 이메일/비밀번호, Google 로그인
- **Firestore Database**: 데이터베이스 생성
- **Functions**: 백엔드 함수 (선택사항)
- **Hosting**: 정적 사이트 (Vercel 사용하므로 비활성화)

## 🚨 주의사항
- 실제 Firebase 프로젝트를 생성해야 함
- 더미 값으로는 작동하지 않음
- Vercel 환경 변수 설정 필수 