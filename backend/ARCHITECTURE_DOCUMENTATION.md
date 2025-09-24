# 🏗️ 엔오건강도우미 시스템 아키텍처 문서

## 📋 개요

엔오건강도우미는 RPPG(Remote Photoplethysmography)와 음성 분석을 통합한 건강 모니터링 시스템입니다. 이 문서는 시스템의 아키텍처, API, 그리고 운영 방법을 설명합니다.

## 🎯 시스템 목표

- **실시간 건강 분석**: 15초 내 RPPG 및 음성 분석 완료
- **고정밀 측정**: 95% 이상의 정확도 달성
- **확장성**: 동시 20명 이상 사용자 처리
- **안정성**: 99.9% 이상의 가동률 유지

## 🏛️ 아키텍처 개요

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   mkm-core-ai   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (RPPG Core)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Redis Cache   │    │   Voice         │
│   (Hosting)     │    │   (Session)     │    │   Analyzer      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 핵심 컴포넌트

### 1. Frontend (Next.js)
- **기술 스택**: Next.js 14, React 18, Tailwind CSS
- **주요 기능**: 
  - 실시간 비디오 캡처
  - 음성 녹음
  - 결과 시각화
  - 반응형 UI

### 2. Backend (FastAPI)
- **기술 스택**: FastAPI, Python 3.11+, Uvicorn
- **주요 기능**:
  - API 엔드포인트 제공
  - 데이터 검증 및 처리
  - 캐싱 및 세션 관리
  - 에러 핸들링

### 3. mkm-core-ai Integration
- **역할**: 고품질 RPPG 분석 엔진
- **주요 기능**:
  - CHROM 알고리즘
  - POS 알고리즘
  - 신호 처리 및 노이즈 제거
  - 실시간 분석

### 4. Voice Analyzer
- **기술 스택**: Python, SciPy, NumPy
- **주요 기능**:
  - 기본 주파수(F0) 분석
  - Jitter/Shimmer 측정
  - Harmonic-to-Noise Ratio 계산
  - 음성 품질 평가

### 5. Fusion Analyzer
- **역할**: RPPG와 음성 데이터 융합
- **주요 기능**:
  - 다중 데이터 소스 통합
  - 동적 가중치 적용
  - 이상치 필터링
  - 불확실성 추정

## 🌐 API 엔드포인트

### Health Check
```
GET /api/v1/health
```
**응답**:
```json
{
  "message": "엔오건강도우미 백엔드 서버 - 실제 건강 분석 도구",
  "status": "running",
  "real_analyzers": true,
  "version": "2.0.0"
}
```

### RPPG Analysis
```
POST /api/v1/measure/rppg
```
**요청**:
```json
{
  "video_data": "base64_encoded_video",
  "frame_count": 300
}
```
**응답**:
```json
{
  "hr": 72.0,
  "hrv": 45.2,
  "stress_level": 0.3,
  "confidence": 0.85,
  "timestamp": "2025-08-30T14:30:00Z"
}
```

### Voice Analysis
```
POST /api/v1/measure/voice
```
**요청**:
```json
{
  "audio_data": "base64_encoded_audio"
}
```
**응답**:
```json
{
  "f0": 180.5,
  "jitter": 0.02,
  "shimmer": 0.15,
  "hnr": 12.5,
  "confidence": 0.90,
  "timestamp": "2025-08-30T14:30:00Z"
}
```

### Combined Analysis
```
POST /api/v1/measure/combined
```
**요청**:
```json
{
  "video_data": "base64_encoded_video",
  "audio_data": "base64_encoded_audio",
  "frame_count": 300
}
```
**응답**:
```json
{
  "rppg": { ... },
  "voice": { ... },
  "fusion": {
    "overall_health_score": 0.87,
    "stress_assessment": "low",
    "recommendations": ["규칙적인 운동", "충분한 수면"],
    "confidence": 0.92
  }
}
```

## 📊 데이터 흐름

### 1. RPPG 분석 워크플로우
```
비디오 입력 → 프레임 추출 → ROI 검출 → 신호 처리 → 
CHROM/POS 알고리즘 → HR/HRV 계산 → 품질 평가 → 결과 반환
```

### 2. 음성 분석 워크플로우
```
오디오 입력 → 전처리 → F0 추출 → Jitter/Shimmer 계산 → 
HNR 계산 → 품질 평가 → 결과 반환
```

### 3. 융합 분석 워크플로우
```
RPPG + 음성 데이터 → 시간 동기화 → 특성 추출 → 
동적 가중치 적용 → 이상치 필터링 → 융합 모델 → 최종 결과
```

## ⚙️ 설정 및 환경 변수

### 환경 변수
```bash
# 서버 설정
HOST=127.0.0.1
PORT=8001
DEBUG=false

# Redis 설정
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# mkm-core-ai 설정
MKM_CORE_AI_URL=http://localhost:3000
MKM_CORE_AI_TIMEOUT=30

# 로깅 설정
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker 설정
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8001:8001"
    environment:
      - HOST=0.0.0.0
      - PORT=8001
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
```

## 🔍 모니터링 및 로깅

### 로그 레벨
- **DEBUG**: 상세한 디버깅 정보
- **INFO**: 일반적인 정보 메시지
- **WARNING**: 경고 메시지
- **ERROR**: 오류 메시지
- **CRITICAL**: 심각한 오류

### 성능 메트릭
- **응답 시간**: API 엔드포인트별 응답 시간
- **처리량**: 초당 처리 가능한 요청 수
- **에러율**: 실패한 요청의 비율
- **리소스 사용량**: CPU, 메모리, 디스크 사용량

## 🚀 배포 및 운영

### 개발 환경
```bash
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 프로덕션 환경
```bash
# 프로덕션 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# Docker 배포
docker-compose up -d

# Kubernetes 배포
kubectl apply -f k8s/
```

### 헬스체크
```bash
# 서버 상태 확인
curl http://localhost:8001/api/v1/health

# 상세 상태 확인
curl http://localhost:8001/api/v1/health/detailed
```

## 🧪 테스트

### 단위 테스트
```bash
# 모든 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_rppg_analyzer.py

# 커버리지 포함
pytest --cov=app tests/
```

### 통합 테스트
```bash
# 워크플로우 테스트
python integration_workflow_test.py

# 성능 테스트
python performance_test.py

# 부하 테스트
python load_test.py
```

### API 테스트
```bash
# Swagger UI
http://localhost:8001/docs

# ReDoc
http://localhost:8001/redoc
```

## 🔧 문제 해결

### 일반적인 문제

#### 1. 서버 시작 실패
```bash
# 포트 충돌 확인
netstat -ano | findstr :8001

# 프로세스 종료
taskkill /PID <PID> /F
```

#### 2. 메모리 부족
```bash
# 메모리 사용량 확인
Get-Process python | Select-Object ProcessName, Id, CPU, WorkingSet

# 가상 메모리 증가
python -X maxsize=2GB main.py
```

#### 3. 성능 저하
```bash
# CPU 사용량 확인
Get-Process python | Select-Object ProcessName, Id, CPU

# 로그 분석
Get-Content app.log | Select-String "ERROR"
```

## 📚 추가 자료

### 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [Redis 공식 문서](https://redis.io/documentation)

### 코드 저장소
- [eno-health-helper](https://github.com/mkmlab-v2/eno-health-helper)
- [mkm-core-ai](https://github.com/mkmlab-v2/mkm-core-ai)

### 연락처
- **개발팀**: MKM Lab
- **이메일**: dev@mkmlab.com
- **슬랙**: #eno-health-helper

---

**문서 버전**: 2.0.0  
**최종 업데이트**: 2025-08-30  
**작성자**: Veritas (AI Auditor)
