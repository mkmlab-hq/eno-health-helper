import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import traceback
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """에러 심각도 등급"""
    LOW = "low"           # 경고, 측정 계속 가능
    MEDIUM = "medium"     # 주의, 재시도 권장
    HIGH = "high"         # 심각, 측정 중단 필요
    CRITICAL = "critical" # 치명적, 시스템 오류

class ErrorCategory(Enum):
    """에러 카테고리"""
    CAMERA = "camera"           # 카메라 관련
    SIGNAL = "signal"           # 신호 처리 관련
    ENVIRONMENT = "environment" # 환경 관련
    SYSTEM = "system"           # 시스템 관련
    USER = "user"               # 사용자 관련
    NETWORK = "network"         # 네트워크 관련

class MeasurementErrorHandler:
    """
    생체신호 측정 에러 핸들링 시스템
    
    측정 과정에서 발생하는 다양한 에러를 분류하고,
    사용자에게 적절한 해결 방안을 제시합니다.
    """
    
    def __init__(self):
        self.error_log = []
        self.recovery_strategies = self._initialize_recovery_strategies()
        logger.info("측정 에러 핸들링 시스템 초기화 완료")
    
    def _initialize_recovery_strategies(self) -> Dict[str, Dict]:
        """복구 전략 초기화"""
        return {
            "camera_access_denied": {
                "severity": ErrorSeverity.HIGH,
                "category": ErrorCategory.CAMERA,
                "user_message": "카메라 접근이 거부되었습니다.",
                "recovery_steps": [
                    "브라우저 설정에서 카메라 권한을 허용해주세요.",
                    "페이지를 새로고침하고 다시 시도해주세요.",
                    "다른 브라우저로 시도해보세요."
                ],
                "technical_details": "navigator.mediaDevices.getUserMedia 권한 거부"
            },
            "camera_not_found": {
                "severity": ErrorSeverity.HIGH,
                "category": ErrorCategory.CAMERA,
                "user_message": "카메라를 찾을 수 없습니다.",
                "recovery_steps": [
                    "카메라가 연결되어 있는지 확인해주세요.",
                    "다른 애플리케이션에서 카메라를 사용 중인지 확인해주세요.",
                    "카메라 드라이버를 업데이트해주세요."
                ],
                "technical_details": "카메라 하드웨어 감지 실패"
            },
            "face_not_detected": {
                "severity": ErrorSeverity.MEDIUM,
                "category": ErrorCategory.USER,
                "user_message": "얼굴이 감지되지 않았습니다.",
                "recovery_steps": [
                    "얼굴이 카메라 화면에 완전히 보이도록 해주세요.",
                    "적절한 조명에서 측정해주세요.",
                    "안경이나 마스크를 제거하고 시도해주세요.",
                    "카메라에서 30-50cm 거리를 유지해주세요."
                ],
                "technical_details": "OpenCV 얼굴 감지 실패"
            },
            "poor_lighting": {
                "severity": ErrorSeverity.MEDIUM,
                "category": ErrorCategory.ENVIRONMENT,
                "user_message": "조명이 부족합니다.",
                "recovery_steps": [
                    "더 밝은 곳에서 측정해주세요.",
                    "직사광선을 피하고 적당한 조명을 사용해주세요.",
                    "측정 중 조명이 일정하게 유지되도록 해주세요."
                ],
                "technical_details": "평균 밝기 < 50 (0-255 스케일)"
            },
            "excessive_motion": {
                "severity": ErrorSeverity.MEDIUM,
                "category": ErrorCategory.USER,
                "user_message": "움직임이 너무 많습니다.",
                "recovery_steps": [
                    "가능한 한 정지 상태를 유지해주세요.",
                    "카메라를 고정하고 안정적인 자세를 취해주세요.",
                    "호흡을 조절하고 긴장을 풀어주세요."
                ],
                "technical_details": "신호 변화량 > 임계값"
            },
            "weak_signal": {
                "severity": ErrorSeverity.MEDIUM,
                "category": ErrorCategory.SIGNAL,
                "user_message": "신호가 너무 약합니다.",
                "recovery_steps": [
                    "카메라와의 거리를 조정해주세요.",
                    "조명을 밝게 해주세요.",
                    "배경을 단순하게 만들어주세요.",
                    "측정 전 5분간 안정 상태를 유지해주세요."
                ],
                "technical_details": "신호 대비 노이즈 비율 < 임계값"
            },
            "measurement_timeout": {
                "severity": ErrorSeverity.LOW,
                "category": ErrorCategory.USER,
                "user_message": "측정 시간이 초과되었습니다.",
                "recovery_steps": [
                    "30초 동안 측정을 유지해주세요.",
                    "중간에 중단하지 말고 계속해주세요.",
                    "측정 중 다른 작업을 하지 마세요."
                ],
                "technical_details": "측정 시간 < 최소 요구 시간"
            },
            "network_error": {
                "severity": ErrorSeverity.HIGH,
                "category": ErrorCategory.NETWORK,
                "user_message": "네트워크 연결에 문제가 있습니다.",
                "recovery_steps": [
                    "인터넷 연결을 확인해주세요.",
                    "페이지를 새로고침해주세요.",
                    "잠시 후 다시 시도해주세요."
                ],
                "technical_details": "API 요청 실패 또는 타임아웃"
            },
            "system_error": {
                "severity": ErrorSeverity.CRITICAL,
                "category": ErrorCategory.SYSTEM,
                "user_message": "시스템 오류가 발생했습니다.",
                "recovery_steps": [
                    "페이지를 새로고침해주세요.",
                    "브라우저를 재시작해주세요.",
                    "잠시 후 다시 시도해주세요.",
                    "문제가 지속되면 관리자에게 문의해주세요."
                ],
                "technical_details": "내부 시스템 오류"
            }
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        에러 처리 및 복구 방안 제공
        
        Args:
            error: 발생한 에러 객체
            context: 에러 발생 컨텍스트 정보
            
        Returns:
            에러 처리 결과 및 복구 방안
        """
        try:
            # 에러 정보 추출
            error_info = self._extract_error_info(error, context)
            
            # 에러 로깅
            self._log_error(error_info)
            
            # 복구 전략 결정
            recovery_strategy = self._determine_recovery_strategy(error_info)
            
            # 사용자 친화적 메시지 생성
            user_friendly_message = self._create_user_message(recovery_strategy)
            
            # 에러 응답 생성
            error_response = {
                "error_id": error_info["error_id"],
                "timestamp": error_info["timestamp"],
                "severity": recovery_strategy["severity"].value,
                "category": recovery_strategy["category"].value,
                "user_message": user_friendly_message,
                "recovery_steps": recovery_strategy["recovery_steps"],
                "can_retry": recovery_strategy["severity"] in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM],
                "requires_restart": recovery_strategy["severity"] == ErrorSeverity.CRITICAL,
                "technical_details": recovery_strategy.get("technical_details", ""),
                "support_info": self._get_support_info(recovery_strategy)
            }
            
            return error_response
            
        except Exception as e:
            logger.error(f"에러 처리 중 추가 오류 발생: {str(e)}")
            return self._create_fallback_error_response(str(e))
    
    def _extract_error_info(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """에러 정보 추출"""
        error_info = {
            "error_id": f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}",
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        # 에러 타입별 추가 정보 추출
        if "camera" in str(error).lower() or "permission" in str(error).lower():
            error_info["category"] = "camera_access_denied"
        elif "face" in str(error).lower() or "detection" in str(error).lower():
            error_info["category"] = "face_not_detected"
        elif "light" in str(error).lower() or "brightness" in str(error).lower():
            error_info["category"] = "poor_lighting"
        elif "motion" in str(error).lower() or "movement" in str(error).lower():
            error_info["category"] = "excessive_motion"
        elif "signal" in str(error).lower() or "weak" in str(error).lower():
            error_info["category"] = "weak_signal"
        elif "timeout" in str(error).lower() or "duration" in str(error).lower():
            error_info["category"] = "measurement_timeout"
        elif "network" in str(error).lower() or "connection" in str(error).lower():
            error_info["category"] = "network_error"
        else:
            error_info["category"] = "system_error"
        
        return error_info
    
    def _determine_recovery_strategy(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """복구 전략 결정"""
        category = error_info.get("category", "system_error")
        
        if category in self.recovery_strategies:
            return self.recovery_strategies[category]
        else:
            return self.recovery_strategies["system_error"]
    
    def _create_user_message(self, recovery_strategy: Dict[str, Any]) -> str:
        """사용자 친화적 메시지 생성"""
        base_message = recovery_strategy["user_message"]
        
        # 심각도에 따른 추가 안내
        severity = recovery_strategy["severity"]
        if severity == ErrorSeverity.CRITICAL:
            return f"🚨 {base_message} (긴급 조치 필요)"
        elif severity == ErrorSeverity.HIGH:
            return f"⚠️ {base_message} (즉시 조치 필요)"
        elif severity == ErrorSeverity.MEDIUM:
            return f"⚠️ {base_message} (조치 권장)"
        else:
            return f"ℹ️ {base_message} (참고사항)"
    
    def _get_support_info(self, recovery_strategy: Dict[str, Any]) -> Dict[str, str]:
        """지원 정보 제공"""
        return {
            "contact": "support@eno-health-helper.com",
            "documentation": "https://github.com/mkmlab-hq/eno-health-helper/wiki",
            "faq": "https://github.com/mkmlab-hq/eno-health-helper/wiki/FAQ",
            "emergency": "의료 응급 상황 시 119 또는 가까운 병원으로 연락"
        }
    
    def _log_error(self, error_info: Dict[str, Any]):
        """에러 로깅"""
        self.error_log.append(error_info)
        
        # 로그 파일에 저장
        log_entry = {
            "timestamp": error_info["timestamp"],
            "error_id": error_info["error_id"],
            "category": error_info["category"],
            "message": error_info["error_message"],
            "context": error_info["context"]
        }
        
        logger.error(f"측정 에러 발생: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # 에러 로그 크기 제한 (최근 100개만 유지)
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
    
    def _create_fallback_error_response(self, error_message: str) -> Dict[str, Any]:
        """폴백 에러 응답 생성"""
        return {
            "error_id": f"ERR_FALLBACK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "severity": "critical",
            "category": "system",
            "user_message": "예상치 못한 오류가 발생했습니다.",
            "recovery_steps": [
                "페이지를 새로고침해주세요.",
                "브라우저를 재시작해주세요.",
                "문제가 지속되면 관리자에게 문의해주세요."
            ],
            "can_retry": False,
            "requires_restart": True,
            "technical_details": f"폴백 에러 처리 실패: {error_message}",
            "support_info": {
                "contact": "support@eno-health-helper.com",
                "emergency": "의료 응급 상황 시 119 또는 가까운 병원으로 연락"
            }
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """에러 통계 정보 제공"""
        if not self.error_log:
            return {
                "total_errors": 0,
                "error_categories": {},
                "severity_distribution": {},
                "recent_errors": []
            }
        
        # 카테고리별 에러 수
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_log:
            category = error.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # 심각도별 에러 수 (복구 전략에서 추출)
            if category in self.recovery_strategies:
                severity = self.recovery_strategies[category]["severity"].value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.error_log),
            "error_categories": category_counts,
            "severity_distribution": severity_counts,
            "recent_errors": self.error_log[-10:],  # 최근 10개 에러
            "last_error_time": self.error_log[-1]["timestamp"] if self.error_log else None
        }
    
    def clear_error_log(self):
        """에러 로그 초기화"""
        self.error_log.clear()
        logger.info("에러 로그가 초기화되었습니다.")
    
    def export_error_log(self, filepath: str = None) -> str:
        """에러 로그 내보내기"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"error_log_{timestamp}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.error_log, f, ensure_ascii=False, indent=2)
            
            logger.info(f"에러 로그가 {filepath}에 저장되었습니다.")
            return filepath
            
        except Exception as e:
            logger.error(f"에러 로그 내보내기 실패: {str(e)}")
            raise
