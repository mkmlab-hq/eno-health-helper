# Firebase 설정 가이드

## 1. Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. "프로젝트 만들기" 클릭
3. 프로젝트 이름 입력 (예: "eno-health-helper")
4. Google Analytics 설정 (선택사항)
5. 프로젝트 생성 완료

## 2. 웹 앱 추가

1. 프로젝트 대시보드에서 "웹" 아이콘 클릭
2. 앱 닉네임 입력 (예: "eno-health-helper-web")
3. "Firebase Hosting 설정" 체크 해제 (현재는 사용하지 않음)
4. "앱 등록" 클릭

## 3. Firebase 설정 정보 복사

앱 등록 후 표시되는 설정 정보를 복사하여 `.env.local` 파일에 입력:

```bash
# .env.local 파일 생성
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your_measurement_id
```

## 4. Authentication 설정

1. 왼쪽 메뉴에서 "Authentication" 클릭
2. "시작하기" 클릭
3. "로그인 방법" 탭에서 다음 제공업체 활성화:
   - 이메일/비밀번호
   - Google
4. Google 로그인 설정:
   - "사용 설정" 체크
   - 프로젝트 지원 이메일 선택
   - "저장" 클릭

## 5. Firestore Database 설정

1. 왼쪽 메뉴에서 "Firestore Database" 클릭
2. "데이터베이스 만들기" 클릭
3. 보안 규칙 선택:
   - "테스트 모드에서 시작" 선택 (개발용)
   - "다음" 클릭
4. 데이터베이스 위치 선택 (가까운 지역 선택)
5. "완료" 클릭

## 6. Firestore 보안 규칙 설정

Firestore Database > 규칙 탭에서 다음 규칙 설정:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 프로필: 본인만 읽기/쓰기
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 측정 결과: 본인만 읽기/쓰기
    match /measurements/{measurementId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.userId;
    }
  }
}
```

## 7. 카카오 로그인 설정 (선택사항)

1. [Kakao Developers](https://developers.kakao.com/)에서 앱 생성
2. 플랫폼 > Web 설정에서 사이트 도메인 등록
3. JavaScript 키 복사하여 `.env.local`에 추가:

```bash
NEXT_PUBLIC_KAKAO_APP_KEY=your_kakao_app_key_here
NEXT_PUBLIC_KAKAO_REDIRECT_URI=http://localhost:3000/auth/kakao/callback
```

## 8. 환경 변수 파일 생성

프로젝트 루트에 `.env.local` 파일 생성:

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

## 9. 개발 서버 실행

```bash
npm run dev
```

## 10. 테스트

1. http://localhost:3000 접속
2. 회원가입/로그인 테스트
3. 건강 측정 기능 테스트
4. 결과 저장 및 조회 테스트

## 주의사항

- `.env.local` 파일은 `.gitignore`에 포함되어 있어야 합니다
- 실제 프로덕션 배포 시에는 적절한 보안 규칙을 설정해야 합니다
- 카카오 로그인은 추가 구현이 필요합니다 (현재는 UI만 준비됨)
