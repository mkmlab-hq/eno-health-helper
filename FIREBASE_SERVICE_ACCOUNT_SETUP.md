# Firebase 서비스 계정 키 생성 가이드

## 🎯 개요
이 가이드는 Firebase Admin SDK를 위한 새로운 서비스 계정 키를 생성하고 설정하는 방법을 설명합니다.

## 🔑 새 서비스 계정 키 생성 이유

### **보안 강화**
- 기존 키의 노출 가능성 제거
- 새로운 키로 최소 권한 원칙 적용
- 키 순환으로 보안 강화

### **권한 최적화**
- 필요한 기능만 접근 권한 부여
- Firestore, Storage, Authentication 등 선택적 권한

## 🔧 1단계: Firebase 콘솔에서 새 키 생성

### 1.1 Firebase 콘솔 접속
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. `eno-health-helper` 프로젝트 선택

### 1.2 서비스 계정 설정
1. **프로젝트 설정** (⚙️ 아이콘) 클릭
2. **서비스 계정** 탭 선택
3. **"새 비공개 키 생성"** 버튼 클릭

### 1.3 키 다운로드
1. **"키 생성"** 확인
2. **JSON 파일 자동 다운로드**
3. 파일명: `eno-health-helper-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`

## 📁 2단계: 키 파일 배치

### 2.1 백엔드 폴더에 저장
```bash
# 다운로드된 JSON 파일을 다음 경로로 이동
eno-health-helper/backend/serviceAccountKey.json
```

### 2.2 파일 권한 확인
- **Windows**: 일반 파일 권한
- **Linux/Mac**: `chmod 600 serviceAccountKey.json`

## 🔒 3단계: 보안 설정

### 3.1 .gitignore 확인
```bash
# 다음 내용이 .gitignore에 포함되어 있는지 확인
serviceAccountKey.json
*.json.key
```

### 3.2 환경 변수 설정 (선택사항)
```bash
# .env 파일에 키 정보 저장 (보안 강화)
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json
```

## 🧪 4단계: 연결 테스트

### 4.1 백엔드 서버 시작
```bash
cd eno-health-helper/backend
.venv\Scripts\activate  # Windows
python firebase_backend.py
```

### 4.2 연결 상태 확인
```bash
# 브라우저에서 확인
http://localhost:8000/

# 응답 예시
{
  "message": "Firebase 우선 연동 백엔드 서버",
  "status": "running",
  "firebase_connected": true,
  "version": "1.0.0"
}
```

## 🚨 5단계: 문제 해결

### 5.1 일반적인 오류
- **"Service account key file not found"**: 파일 경로 확인
- **"Invalid service account key"**: JSON 파일 형식 확인
- **"Permission denied"**: 파일 권한 확인

### 5.2 디버깅 팁
```python
# firebase_backend.py에 디버깅 코드 추가
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    print(f"✅ 서비스 계정 키 로드 성공: {cred.service_account_email}")
except Exception as e:
    print(f"❌ 서비스 계정 키 로드 실패: {e}")
```

## 📋 6단계: 권한 확인

### 6.1 필요한 권한
- **Firestore**: 읽기/쓰기 권한
- **Storage**: 파일 업로드/다운로드 권한
- **Authentication**: 사용자 관리 권한

### 6.2 권한 설정 확인
1. **Firebase 콘솔** → **Authentication** → **사용자** 탭
2. **Firestore Database** → **규칙** 탭
3. **Storage** → **규칙** 탭

## 🔄 7단계: 키 순환 정책

### 7.1 정기적 키 교체
- **권장 주기**: 90일마다
- **교체 방법**: 새 키 생성 후 기존 키 삭제
- **백업**: 키 교체 전 데이터 백업

### 7.2 모니터링
- **사용량 추적**: Firebase 콘솔에서 API 사용량 확인
- **오류 로그**: 연결 실패 시 로그 분석
- **성능 모니터링**: 응답 시간 및 처리량 확인

## 📞 지원 및 문의

### 문제 발생 시
1. **Firebase 공식 문서** 확인
2. **Firebase 커뮤니티** 포럼 검색
3. **프로젝트 팀**에 문의

### 유용한 링크
- [Firebase Admin SDK 시작하기](https://firebase.google.com/docs/admin/setup)
- [서비스 계정 키 관리](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
- [Firebase 보안 규칙](https://firebase.google.com/docs/rules)

---

**마지막 업데이트**: 2025-01-22
**버전**: 1.0.0
**보안 등급**: 🔒 높음 