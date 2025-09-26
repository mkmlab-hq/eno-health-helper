#!/usr/bin/env python3
"""
상위 모델 자문 요청 스크립트
현재 시스템의 문제점과 개선 방향을 상세히 분석하여 상위 모델에게 자문을 구합니다.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeniorModelConsultationRequest:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.consultation_file = self.project_root / "docs" / "SENIOR_MODEL_CONSULTATION_REQUEST.md"
        
    def analyze_current_system(self):
        """현재 시스템 상태 분석"""
        logger.info("🔍 현재 시스템 상태 분석 시작...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_overview": {
                "project_name": "엔오건강도우미",
                "current_version": "v1.0.0",
                "technology_stack": ["FastAPI", "Next.js", "Python", "RPPG", "Voice Analysis"]
            },
            "current_performance": {},
            "identified_problems": [],
            "improvement_requests": [],
            "technical_details": {}
        }
        
        # 1. 성능 데이터 분석
        self._analyze_performance_data(analysis)
        
        # 2. 문제점 식별
        self._identify_problems(analysis)
        
        # 3. 개선 요청 사항 정리
        self._prepare_improvement_requests(analysis)
        
        # 4. 기술적 세부사항 수집
        self._collect_technical_details(analysis)
        
        return analysis
    
    def _analyze_performance_data(self, analysis):
        """성능 데이터 분석"""
        try:
            # 정확도 테스트 결과 분석
            accuracy_file = self.backend_dir / "accuracy_test_results.json"
            if accuracy_file.exists():
                with open(accuracy_file, 'r', encoding='utf-8') as f:
                    accuracy_data = json.load(f)
                
                analysis["current_performance"] = {
                    "overall_accuracy": accuracy_data.get("overall_accuracy", 0),
                    "rppg_accuracy": accuracy_data.get("rppg_results", {}).get("accuracy", 0),
                    "voice_accuracy": accuracy_data.get("voice_results", {}).get("accuracy", 0),
                    "test_duration": accuracy_data.get("test_duration", 0),
                    "last_test": accuracy_data.get("timestamp", "")
                }
            
            # 훈련 결과 분석
            training_file = self.backend_dir / "medical_grade_training_results.json"
            if training_file.exists():
                with open(training_file, 'r', encoding='utf-8') as f:
                    training_data = json.load(f)
                
                analysis["training_performance"] = {
                    "best_overall_accuracy": training_data.get("best_overall_accuracy", 0),
                    "best_rppg_accuracy": training_data.get("best_rppg_accuracy", 0),
                    "best_voice_accuracy": training_data.get("best_voice_accuracy", 0),
                    "total_epochs": training_data.get("total_epochs", 0)
                }
                
        except Exception as e:
            logger.error(f"성능 데이터 분석 실패: {e}")
    
    def _identify_problems(self, analysis):
        """문제점 식별"""
        problems = []
        
        # 1. 과적합 문제
        if "training_performance" in analysis and "current_performance" in analysis:
            training_acc = analysis["training_performance"]["best_overall_accuracy"]
            current_acc = analysis["current_performance"]["overall_accuracy"]
            overfitting_gap = abs(training_acc - current_acc)
            
            if overfitting_gap > 10:
                problems.append({
                    "type": "과적합 (Overfitting)",
                    "severity": "심각",
                    "description": f"훈련 정확도({training_acc}%)와 실제 성능({current_acc}%) 간 {overfitting_gap:.1f}% 차이",
                    "impact": "시스템 신뢰성 저하, 실제 환경에서 성능 저하"
                })
        
        # 2. 낮은 정확도 문제
        if analysis["current_performance"]["overall_accuracy"] < 80:
            problems.append({
                "type": "낮은 정확도",
                "severity": "중간",
                "description": f"전체 정확도 {analysis['current_performance']['overall_accuracy']}%로 의료기기 수준(95%+)에 미달",
                "impact": "의료적 활용 불가, 사용자 신뢰도 저하"
            })
        
        # 3. 한글 폰트 문제
        problems.append({
            "type": "한글 폰트 렌더링",
            "severity": "낮음",
            "description": "matplotlib에서 한글 텍스트 렌더링 실패",
            "impact": "그래프 가독성 저하, 사용자 경험 악화"
        })
        
        # 4. 데이터 품질 문제
        problems.append({
            "type": "데이터 품질",
            "severity": "중간",
            "description": "가상 데이터 기반 훈련으로 실제 환경 적응성 부족",
            "impact": "실제 사용 환경에서 성능 저하"
        })
        
        analysis["identified_problems"] = problems
    
    def _prepare_improvement_requests(self, analysis):
        """개선 요청 사항 정리"""
        requests = []
        
        # 1. 알고리즘 개선 요청
        requests.append({
            "category": "알고리즘 개선",
            "priority": "높음",
            "request": "RPPG 및 음성 분석 알고리즘의 정확도 향상 방안 제시",
            "target": "전체 정확도 66.2% → 85% 이상",
            "details": [
                "신호 처리 알고리즘 최적화",
                "노이즈 제거 기법 개선",
                "특징 추출 방법론 개선"
            ]
        })
        
        # 2. 과적합 방지 요청
        requests.append({
            "category": "과적합 방지",
            "priority": "높음",
            "request": "훈련 데이터와 실제 성능 간 격차 해소 방안",
            "target": "과적합 갭 10% 이하",
            "details": [
                "교차 검증 방법론",
                "정규화 기법",
                "데이터 증강 전략"
            ]
        })
        
        # 3. 데이터 품질 개선 요청
        requests.append({
            "category": "데이터 품질",
            "priority": "중간",
            "request": "실제 환경 데이터 기반 훈련 방법론",
            "target": "가상 데이터 의존도 제거",
            "details": [
                "실제 생체신호 데이터 수집 방법",
                "데이터 전처리 파이프라인",
                "품질 관리 체계"
            ]
        })
        
        # 4. 시스템 아키텍처 개선 요청
        requests.append({
            "category": "시스템 아키텍처",
            "priority": "중간",
            "request": "확장 가능한 모듈형 아키텍처 설계",
            "target": "유지보수성 및 확장성 향상",
            "details": [
                "마이크로서비스 아키텍처",
                "API 설계 개선",
                "모니터링 및 로깅 체계"
            ]
        })
        
        analysis["improvement_requests"] = requests
    
    def _collect_technical_details(self, analysis):
        """기술적 세부사항 수집"""
        technical = {
            "current_implementation": {},
            "dependencies": {},
            "performance_metrics": {},
            "system_requirements": {}
        }
        
        # 현재 구현 상태
        try:
            requirements_file = self.backend_dir / "requirements.txt"
            if requirements_file.exists():
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    dependencies = f.read().strip().split('\n')
                technical["dependencies"] = dependencies
        except Exception as e:
            logger.error(f"의존성 정보 수집 실패: {e}")
        
        # 성능 지표
        if "current_performance" in analysis:
            technical["performance_metrics"] = {
                "rppg_mae": analysis["current_performance"].get("rppg_mae", "N/A"),
                "rppg_rmse": analysis["current_performance"].get("rppg_rmse", "N/A"),
                "voice_mae": analysis["current_performance"].get("voice_mae", "N/A"),
                "voice_rmse": analysis["current_performance"].get("voice_rmse", "N/A")
            }
        
        # 시스템 요구사항
        technical["system_requirements"] = {
            "python_version": "3.11+",
            "memory_requirements": "4GB+",
            "processing_power": "중간급 CPU",
            "camera_quality": "720p 이상",
            "microphone_quality": "노이즈 캔슬링 지원"
        }
        
        analysis["technical_details"] = technical
    
    def generate_consultation_report(self):
        """상위 모델 자문 요청 보고서 생성"""
        logger.info("📋 상위 모델 자문 요청 보고서 생성 시작...")
        
        # 분석 수행
        analysis = self.analyze_current_system()
        
        # 보고서 생성
        report = self._format_consultation_report(analysis)
        
        # 파일 저장
        self.consultation_file.parent.mkdir(exist_ok=True)
        with open(self.consultation_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"✅ 상위 모델 자문 요청 보고서 생성 완료: {self.consultation_file}")
        return self.consultation_file
    
    def _format_consultation_report(self, analysis):
        """자문 요청 보고서 포맷팅"""
        report = f"""# 🚨 상위 모델 자문 요청 보고서

## 📅 요청 일시
{analysis['timestamp']}

## 🎯 프로젝트 개요
- **프로젝트명**: {analysis['system_overview']['project_name']}
- **현재 버전**: {analysis['system_overview']['current_version']}
- **기술 스택**: {', '.join(analysis['system_overview']['technology_stack'])}

## 📊 현재 시스템 성능

### 전체 성능
- **종합 정확도**: {analysis['current_performance'].get('overall_accuracy', 'N/A')}%
- **RPPG 정확도**: {analysis['current_performance'].get('rppg_accuracy', 'N/A')}%
- **음성 정확도**: {analysis['current_performance'].get('voice_accuracy', 'N/A')}%
- **마지막 테스트**: {analysis['current_performance'].get('last_test', 'N/A')}

### 훈련 성능
- **최고 전체 정확도**: {analysis.get('training_performance', {}).get('best_overall_accuracy', 'N/A')}%
- **최고 RPPG 정확도**: {analysis.get('training_performance', {}).get('best_rppg_accuracy', 'N/A')}%
- **총 훈련 에포크**: {analysis.get('training_performance', {}).get('total_epochs', 'N/A')}

## ⚠️ 식별된 문제점

"""
        
        for i, problem in enumerate(analysis['identified_problems'], 1):
            report += f"""### {i}. {problem['type']}
- **심각도**: {problem['severity']}
- **설명**: {problem['description']}
- **영향**: {problem['impact']}

"""
        
        report += """## 🆘 상위 모델 개선 요청

"""
        
        for i, request in enumerate(analysis['improvement_requests'], 1):
            report += f"""### {i}. {request['category']}
- **우선순위**: {request['priority']}
- **요청사항**: {request['request']}
- **목표**: {request['target']}
- **세부사항**:
"""
            for detail in request['details']:
                report += f"  - {detail}\n"
            report += "\n"
        
        report += f"""## 🔧 기술적 세부사항

### 의존성
```
{chr(10).join(analysis['technical_details'].get('dependencies', []))}
```

### 성능 지표
- **RPPG MAE**: {analysis['technical_details'].get('performance_metrics', {}).get('rppg_mae', 'N/A')}
- **RPPG RMSE**: {analysis['technical_details'].get('performance_metrics', {}).get('rppg_rmse', 'N/A')}
- **음성 MAE**: {analysis['technical_details'].get('performance_metrics', {}).get('voice_mae', 'N/A')}
- **음성 RMSE**: {analysis['technical_details'].get('performance_metrics', {}).get('voice_rmse', 'N/A')}

### 시스템 요구사항
- **Python 버전**: {analysis['technical_details']['system_requirements']['python_version']}
- **메모리**: {analysis['technical_details']['system_requirements']['memory_requirements']}
- **처리 성능**: {analysis['technical_details']['system_requirements']['processing_power']}
- **카메라 품질**: {analysis['technical_details']['system_requirements']['camera_quality']}
- **마이크 품질**: {analysis['technical_details']['system_requirements']['microphone_quality']}

## 🎯 상위 모델에게 요청하는 것

1. **알고리즘 개선 방안**: RPPG 및 음성 분석 정확도 향상 방법론
2. **과적합 방지 전략**: 훈련과 실제 성능 간 격차 해소 방안
3. **데이터 품질 향상**: 실제 환경 데이터 기반 훈련 방법론
4. **시스템 아키텍처**: 확장 가능한 모듈형 설계 방안
5. **성능 최적화**: 메모리 및 처리 성능 최적화 기법

## 📞 연락처
- **프로젝트**: 엔오건강도우미
- **현재 개발자**: AI Assistant
- **요청 수준**: 상위 모델 전문가 자문 필요

---
*이 보고서는 현재 시스템의 문제점을 정확히 파악하고, 상위 모델의 전문적인 조언을 구하기 위해 작성되었습니다.*
"""
        
        return report

def main():
    """메인 실행 함수"""
    logger.info("🚀 상위 모델 자문 요청 스크립트 시작")
    
    try:
        # 자문 요청 객체 생성
        consultation = SeniorModelConsultationRequest()
        
        # 보고서 생성
        report_file = consultation.generate_consultation_report()
        
        logger.info("=" * 60)
        logger.info("🏆 상위 모델 자문 요청 완료!")
        logger.info(f"📁 보고서 위치: {report_file}")
        logger.info("📤 이 보고서를 상위 모델에게 전달하여 전문적인 조언을 구하세요.")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 자문 요청 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 