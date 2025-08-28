# 🚀 Firebase 수동 배포 가이드

## 📋 배포 전 준비사항

### 1. Firebase 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름: `eno-health-helper`
4. Google Analytics 비활성화 (선택사항)

### 2. Firebase Hosting 활성화
1. 프로젝트 대시보드에서 "Hosting" 클릭
2. "시작하기" 클릭
3. "웹 앱에 Firebase 추가" 클릭

### 3. 정적 파일 업로드
1. `frontend/out` 폴더의 모든 파일을 Firebase Hosting에 업로드
2. 또는 Firebase CLI를 사용하여 `firebase deploy` 실행

## 🔧 배포 후 설정

### 1. 도메인 확인
- 기본 도메인: `https://eno-health-helper.web.app`
- 커스텀 도메인 설정 가능

### 2. HTTPS 확인
- Firebase에서 자동으로 SSL 인증서 발급
- 카메라/마이크 접근 가능

## 📱 모바일 테스트

### 1. 카메라 테스트
- 모바일 브라우저에서 사이트 접속
- 카메라 권한 요청 확인
- RPPG 측정 기능 테스트

### 2. 마이크 테스트
- 마이크 권한 요청 확인
- 음성 분석 기능 테스트

## 🚨 문제 해결

### Firebase CLI 오류
- Node.js 버전 호환성 문제
- 수동 배포로 우회
- 또는 Node.js 18 LTS 버전 사용

### 권한 문제
- HTTPS 환경에서만 카메라/마이크 접근 가능
- Firebase Hosting 사용으로 해결 