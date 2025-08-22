# Firebase 연동 설정 가이드

## 🎯 개요
이 가이드는 엔오건강도우미 프로젝트의 Firebase 연동을 위한 상세한 설정 방법을 제공합니다.

## 📋 사전 요구사항
- Firebase 프로젝트 생성 완료
- Firebase 프로젝트 ID
- Firebase API 키
- Firebase 서비스 계정 키 파일

## 🔧 1단계: Firebase 프로젝트 설정

### 1.1 Firebase 콘솔에서 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. "프로젝트 만들기" 클릭
3. 프로젝트 이름: `eno-health-helper` (또는 원하는 이름)
4. Google Analytics 활성화 (선택사항)

### 1.2 웹 앱 추가
1. 프로젝트 대시보드에서 "웹 앱 추가" 클릭
2. 앱 닉네임: `eno-health-web`
3. Firebase 호스팅 설정 (선택사항)

### 1.3 인증 설정
1. 왼쪽 메뉴에서 "Authentication" 클릭
2. "시작하기" 클릭
3. "이메일/비밀번호" 제공업체 활성화
4. "사용자 등록" 활성화

### 1.4 Firestore 데이터베이스 설정
1. 왼쪽 메뉴에서 "Firestore Database" 클릭
2. "데이터베이스 만들기" 클릭
3. 보안 규칙: "테스트 모드에서 시작" 선택
4. 위치: `asia-northeast3 (서울)` 선택

### 1.5 Storage 설정
1. 왼쪽 메뉴에서 "Storage" 클릭
2. "시작하기" 클릭
3. 보안 규칙: "테스트 모드에서 시작" 선택
4. 위치: `asia-northeast3 (서울)` 선택

## 🔑 2단계: 환경 변수 설정

### 2.1 프론트엔드 환경 변수
`eno-health-helper/frontend/.env.local` 파일 생성:

```bash
# Firebase 설정
NEXT_PUBLIC_FIREBASE_API_KEY=your_actual_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id

# 앱 설정
NEXT_PUBLIC_APP_NAME=엔오건강도우미
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 2.2 백엔드 환경 변수
`eno-health-helper/backend/.env` 파일 생성:

```bash
# Firebase Admin SDK
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your_cert_url

# 서버 설정
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,https://eno.no1kmedi.com
```

## 📁 3단계: 서비스 계정 키 설정

### 3.1 서비스 계정 키 다운로드
1. Firebase 콘솔 → 프로젝트 설정 → 서비스 계정
2. "새 비공개 키 생성" 클릭
3. JSON 파일 다운로드
4. `eno-health-helper/backend/serviceAccountKey.json`으로 저장

### 3.2 보안 주의사항
- 서비스 계정 키는 절대 Git에 커밋하지 마세요
- `.gitignore`에 `serviceAccountKey.json` 추가
- 프로덕션에서는 환경 변수로 관리

## 🚀 4단계: 의존성 설치

### 4.1 백엔드 의존성
```bash
cd eno-health-helper/backend
pip install -r requirements_firebase.txt
```

### 4.2 프론트엔드 의존성
```bash
cd eno-health-helper/frontend
npm install firebase
```

## 🔒 5단계: 보안 규칙 설정

### 5.1 Firestore 보안 규칙
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 인증 확인
    match /rppg_analyses/{document} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    match /voice_analyses/{document} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    match /measurement_files/{document} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
  }
}
```

### 5.2 Storage 보안 규칙
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{userId}/{dataType}/{fileName} {
      allow read, write: if request.auth != null && 
        request.auth.uid == userId;
    }
  }
}
```

## 🧪 6단계: 테스트 및 검증

### 6.1 백엔드 서버 시작
```bash
cd eno-health-helper/backend
python firebase_backend.py
```

### 6.2 프론트엔드 개발 서버 시작
```bash
cd eno-health-helper/frontend
npm run dev
```

### 6.3 API 테스트
```bash
# 루트 엔드포인트 테스트
curl http://localhost:8000/

# Firebase 연결 상태 확인
curl http://localhost:8000/api/v1/health
```

## 📊 7단계: 데이터 구조

### 7.1 Firestore 컬렉션 구조
```
rppg_analyses/
  - document_id
    - user_id: string
    - heart_rate: number
    - hrv: number
    - stress_level: string
    - confidence: number
    - timestamp: timestamp
    - firebase_id: string

voice_analyses/
  - document_id
    - user_id: string
    - f0: number
    - jitter: number
    - shimmer: number
    - hnr: number
    - confidence: number
    - timestamp: timestamp
    - firebase_id: string

measurement_files/
  - document_id
    - filename: string
    - user_id: string
    - data_type: string
    - upload_time: string
    - analysis_result: object
```

### 7.2 Storage 폴더 구조
```
{userId}/
  rppg_video/
    - 20250101_120000.bin
  voice_audio/
    - 20250101_120000.bin
  combined_video/
    - 20250101_120000.bin
  combined_audio/
    - 20250101_120000.bin
```

## 🚨 8단계: 문제 해결

### 8.1 일반적인 오류
- **Firebase 연결 실패**: 서비스 계정 키 경로 확인
- **CORS 오류**: 백엔드 CORS 설정 확인
- **권한 오류**: Firestore/Storage 보안 규칙 확인

### 8.2 디버깅 팁
- Firebase 콘솔에서 실시간 로그 확인
- 브라우저 개발자 도구에서 네트워크 요청 확인
- 백엔드 로그에서 상세 오류 메시지 확인

## 📈 9단계: 모니터링 및 최적화

### 9.1 Firebase 콘솔 모니터링
- 사용량 대시보드 확인
- 성능 모니터링
- 오류 보고서 확인

### 9.2 비용 최적화
- Storage 사용량 모니터링
- Firestore 읽기/쓰기 횟수 최적화
- 불필요한 데이터 정리

## 🔄 10단계: 배포 준비

### 10.1 환경별 설정
- 개발/스테이징/프로덕션 환경 분리
- 환경별 Firebase 프로젝트 설정
- CI/CD 파이프라인 구성

### 10.2 보안 강화
- 프로덕션 보안 규칙 적용
- API 키 순환 정책
- 접근 로그 모니터링

## 📞 지원 및 문의

Firebase 연동 관련 문제가 발생하면:
1. Firebase 공식 문서 확인
2. Firebase 커뮤니티 포럼 검색
3. 프로젝트 팀에 문의

---

**마지막 업데이트**: 2025-01-22
**버전**: 1.0.0 