# 엔오건강도우미 (ENO Health Helper)

엔오플렉스 건강기능식품 전용 동반 서비스로, 복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.

## 🎯 **프로젝트 개요**

**엔오건강도우미(ENO Health Helper)**는 **엔오플렉스 건강기능식품 전용 동반 서비스**로, 복용 전후 생체신호 변화를 측정하여 개인화된 웰니스 가이드를 제공합니다.

### **핵심 기능**
- **QR 기반 접근**: 엔오플렉스 포장지 → 즉시 측정 시작
- **복용 전후 비교**: Baseline 측정 → 복용 후 추적 → 변화 분석
- **개인화 가이드**: 체질별 최적 복용법 및 라이프스타일 제안
- **장기 추적**: 지속적 모니터링으로 효과 시각화
- **재구매 연동**: 효과 확인 → 구매 의향 증대

## 🏗️ **기술 스택**

### **Frontend**
- **Framework**: Next.js 14 + TypeScript
- **Styling**: Tailwind CSS + Framer Motion
- **State Management**: Zustand
- **PWA**: Next.js PWA 플러그인

### **Backend**
- **Framework**: FastAPI + Python
- **AI Modules**: MKM Core AI (RPPG + Voice Analysis)
- **Database**: PostgreSQL + SQLAlchemy
- **Authentication**: JWT + OAuth2

### **AI/ML**
- **RPPG Analysis**: 얼굴 혈류 변화 기반 심박수 측정
- **Voice Analysis**: 음성 품질 분석 (F0, 지터, 쉬머, HNR)
- **MKM-12 Engine**: 체질별 개인화 분석

## 📁 **프로젝트 구조**

```
eno-health-helper/
├── frontend/                 # Next.js 프론트엔드
│   ├── src/
│   │   ├── app/             # App Router
│   │   ├── components/      # 재사용 컴포넌트
│   │   ├── hooks/           # 커스텀 훅
│   │   ├── lib/             # 유틸리티 함수
│   │   └── types/           # TypeScript 타입 정의
│   ├── public/              # 정적 파일
│   └── package.json
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/             # API 엔드포인트
│   │   ├── core/            # 핵심 로직
│   │   ├── models/          # 데이터 모델
│   │   └── services/        # 비즈니스 로직
│   ├── requirements.txt
│   └── main.py
├── shared/                   # 공통 타입/유틸리티
│   ├── types/               # TypeScript 타입 정의
│   └── constants/           # 상수 정의
├── docs/                     # 프로젝트 문서
└── docker-compose.yml        # 개발 환경 설정
```

## 🚀 **빠른 시작**

### **개발 환경 설정**
```bash
# 1. 레포지토리 클론
git clone https://github.com/mkmlab-hq/eno-health-helper.git
cd eno-health-helper

# 2. Frontend 설정
cd frontend
npm install
npm run dev

# 3. Backend 설정
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### **환경 변수 설정**
```bash
# .env.local (Frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=엔오건강도우미

# .env (Backend)
DATABASE_URL=postgresql://user:password@localhost/eno_health
SECRET_KEY=your-secret-key
MKM_CORE_AI_URL=http://localhost:8001
```

## 📱 **주요 페이지**

### **1. 메인 페이지 (/)**
- QR 코드 스캔
- 제품 정보 표시
- 측정 시작 버튼

### **2. 측정 페이지 (/measurement)**
- 카메라 권한 요청
- RPPG + 음성 측정
- 실시간 진행 상황

### **3. 결과 페이지 (/results)**
- 건강 분석 리포트
- Before/After 비교
- 개인화 웰니스 가이드

### **4. 추적 페이지 (/tracking)**
- 측정 히스토리
- 변화 추이 차트
- 다음 측정 리마인더

## 🔒 **법적 준수**

### **의료어 필터**
- 120개 의료 금지 용어 자동 필터링
- 실시간 필터 적용 및 로깅

### **면책 시스템**
- **Level A**: 화면 하단 고정 "의료 진단 아님 · 참고용"
- **Level B**: 결과 화면 상단 배너
- **Level C**: 상세 정보 모달

### **데이터 보호**
- RAM only 임시 저장
- 처리 완료 후 즉시 파기
- 감사 로그 시스템

## 🧪 **개발 가이드**

### **컴포넌트 개발**
```typescript
// components/QRScanner.tsx
interface QRScannerProps {
  onScan: (productId: string) => void;
  onError: (error: string) => void;
}

export const QRScanner: React.FC<QRScannerProps> = ({ onScan, onError }) => {
  // QR 스캔 로직 구현
};
```

### **API 개발**
```python
# backend/app/api/health.py
from fastapi import APIRouter, HTTPException
from app.services.health_service import HealthService

router = APIRouter()
health_service = HealthService()

@router.post("/measure")
async def measure_health(measurement_data: MeasurementRequest):
    try:
        result = await health_service.analyze(measurement_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📊 **성능 지표**

### **핵심 KPI**
- **응답 시간**: p95 < 1.2초
- **실패율**: < 4%
- **의료어 필터 누락**: 0건
- **7일 재사용률**: ≥ 40%

## 🤝 **기여하기**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **라이선스**

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 **문의**

- **프로젝트 관리**: MKM Lab
- **기술 문의**: [Issues](https://github.com/mkmlab-hq/eno-health-helper/issues)
- **보안 문의**: security@mkmlab.com

---

**엔오건강도우미** - 당신의 건강한 변화를 측정하고 가이드합니다. 🏥✨ 