# 🏥 ENO건강도우미 기능 분리 계획

## 📋 현재 상황

- **ENO건강도우미**: 현재 Railway에 배포된 통합 버전
- **기능**: MKM-12 분석 + 사상체질 분석 + 기본 건강 관리
- **목표**: 일반 사용자용(기본)과 전문가용(Pro)으로 분리

---

## 🎯 기능 분리 전략

### **ENO건강도우미 Basic (일반 사용자용)**

**배치**: mkmlife.com 통합 플랫폼

#### **핵심 기능**

```python
class EnoHealthBasic:
    """ENO건강도우미 기본 버전 - 일반 사용자용"""

    def core_features(self):
        return {
            "basic_health_analysis": {
                "heart_rate": "기본 심박수 측정",
                "stress_level": "스트레스 수준 측정",
                "health_score": "종합 건강 점수",
                "simple_recommendations": "간단한 건강 조언"
            },
            "persona_integration": {
                "mkm12_basic": "기본 MKM12 페르소나 분석",
                "persona_health_tips": "페르소나별 건강 팁",
                "lifestyle_coaching": "라이프스타일 코칭"
            },
            "user_experience": {
                "simple_ui": "간단한 사용자 인터페이스",
                "daily_checkin": "일일 체크인 기능",
                "progress_tracking": "진행 상황 추적",
                "basic_reports": "기본 보고서"
            }
        }

    def limitations(self):
        return {
            "advanced_analysis": "고급 분석 기능 제한",
            "medical_insights": "의료적 인사이트 제한",
            "detailed_reports": "상세 보고서 제한",
            "api_access": "API 접근 제한"
        }
```

### **ENO건강도우미 Pro (전문가용)**

**배치**: no1kmedi.com 전문가 플랫폼

#### **핵심 기능**

```python
class EnoHealthPro:
    """ENO건강도우미 전문가 버전 - 전문가용"""

    def core_features(self):
        return {
            "advanced_health_analysis": {
                "comprehensive_biomarkers": "종합 생체지표 분석",
                "medical_insights": "의료적 인사이트 제공",
                "detailed_reports": "상세한 분석 보고서",
                "professional_tools": "전문가용 분석 도구"
            },
            "research_capabilities": {
                "data_export": "데이터 내보내기",
                "statistical_analysis": "통계 분석",
                "research_integration": "연구 데이터 연동",
                "collaboration_tools": "협업 도구"
            },
            "professional_features": {
                "api_access": "API 접근",
                "custom_analysis": "맞춤형 분석",
                "batch_processing": "배치 처리",
                "hipaa_compliance": "HIPAA 준수"
            }
        }

    def advanced_features(self):
        return {
            "sasang_constitution": "사상체질 분석 (고급)",
            "mkm12_advanced": "고급 MKM12 분석",
            "multimodal_fusion": "멀티모달 데이터 융합",
            "predictive_analytics": "예측 분석"
        }
```

---

## 🚀 구현 계획

### **Phase 1: 기능 분리 (1-2주)**

#### **1.1 백엔드 API 분리**

```python
# eno-health-helper/backend/main.py 수정
@app.post("/analyze-basic")
async def analyze_basic_health(request: HealthMeasurementRequest):
    """기본 건강 분석 - 일반 사용자용"""
    # 기본 기능만 제공
    pass

@app.post("/analyze-pro")
async def analyze_pro_health(request: HealthMeasurementRequest):
    """고급 건강 분석 - 전문가용"""
    # 모든 고급 기능 제공
    pass
```

#### **1.2 프론트엔드 분리**

- **mkmlife.com**: 기본 UI, 간단한 결과 표시
- **no1kmedi.com**: 고급 UI, 상세한 분석 결과

### **Phase 2: 플랫폼 통합 (2-3주)**

#### **2.1 mkmlife.com 통합**

- 페르소나다이어리와 ENO Basic 통합
- 일관된 사용자 경험 제공
- 통합 대시보드 구축

#### **2.2 no1kmedi.com 업그레이드**

- ENO Pro와 AI차트어시스턴트 통합
- 전문가용 도구 통합
- 연구 플랫폼 기능 강화

### **Phase 3: 데이터 연동 (3-4주)**

#### **3.1 사용자 데이터 연동**

- 일반 사용자 → 전문가 플랫폼 이전 기능
- 데이터 동기화 시스템
- 권한 관리 시스템

---

## 💰 수익 모델 분리

### **ENO Basic (일반 사용자)**

- **구독료**: 월 ₩9,900
- **기능**: 기본 건강 분석, 페르소나 분석, 간단한 조언
- **대상**: 일반 사용자, 건강 관심자

### **ENO Pro (전문가)**

- **구독료**: 월 ₩29,900
- **기능**: 고급 분석, API 접근, 상세 보고서
- **대상**: 의료진, 연구자, 전문가

---

## 🔧 기술적 구현

### **공통 백엔드 구조**

```
eno-health-helper/
├── backend/
│   ├── main.py (공통 API)
│   ├── basic_analyzer.py (기본 분석)
│   ├── pro_analyzer.py (고급 분석)
│   └── shared_models.py (공통 모델)
├── frontend/
│   ├── basic/ (기본 UI)
│   └── pro/ (고급 UI)
└── deployment/
    ├── basic/ (기본 배포)
    └── pro/ (고급 배포)
```

### **API 엔드포인트 분리**

```python
# 기본 버전
POST /analyze-basic
GET /health-score-basic
GET /recommendations-basic

# 전문가 버전
POST /analyze-pro
GET /health-score-pro
GET /recommendations-pro
GET /detailed-reports
GET /research-data
POST /batch-analysis
```

---

## 📊 성능 최적화

### **기본 버전 최적화**

- **빠른 응답**: 간단한 분석으로 빠른 결과
- **모바일 최적화**: 모바일 사용자 경험 중심
- **캐싱**: 자주 사용되는 결과 캐싱

### **전문가 버전 최적화**

- **정확성**: 고급 알고리즘으로 높은 정확도
- **상세성**: 상세한 분석 결과 제공
- **확장성**: 대규모 데이터 처리 가능

---

## 🎯 즉시 실행 계획

### **1주차: 백엔드 분리**

1. API 엔드포인트 분리
2. 기본/고급 분석 로직 분리
3. 권한 관리 시스템 구축

### **2주차: 프론트엔드 분리**

1. mkmlife.com 기본 UI 구축
2. no1kmedi.com 고급 UI 구축
3. 사용자 경험 최적화

### **3주차: 통합 테스트**

1. 기능 분리 테스트
2. 사용자 경험 테스트
3. 성능 최적화

### **4주차: 배포 및 모니터링**

1. 단계적 배포
2. 사용자 피드백 수집
3. 지속적 개선

---

## 🏆 최종 목표

### **일반 사용자 경험**

- **간단함**: 복잡하지 않은 인터페이스
- **빠름**: 빠른 분석 결과
- **유용함**: 일상에 도움이 되는 조언

### **전문가 경험**

- **정확함**: 높은 정확도의 분석
- **상세함**: 상세한 분석 결과
- **전문성**: 전문가 수준의 도구

**지휘관님, 이 기능 분리 계획으로 진행하시겠습니까?** 🚀

