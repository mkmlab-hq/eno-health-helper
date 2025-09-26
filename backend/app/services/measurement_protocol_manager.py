import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MeasurementPhase(Enum):
    """측정 단계"""
    PREPARATION = "preparation"     # 측정 준비
    CALIBRATION = "calibration"     # 보정
    BASELINE = "baseline"           # 기준선 측정
    MEASUREMENT = "measurement"     # 실제 측정
    VALIDATION = "validation"       # 검증
    COMPLETION = "completion"       # 완료

class ProtocolStatus(Enum):
    """프로토콜 상태"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProtocolStep:
    """프로토콜 단계 정보"""
    phase: MeasurementPhase
    name: str
    description: str
    duration: float  # 초 단위
    required: bool
    quality_threshold: float
    instructions: List[str]
    success_criteria: List[str]
    failure_handling: str

class MeasurementProtocolManager:
    """
    표준화된 측정 프로토콜 관리자
    
    엔오건강도우미의 생체신호 측정을 위한
    체계적이고 일관된 측정 절차를 제공합니다.
    """
    
    def __init__(self):
        self.protocols = self._initialize_protocols()
        self.current_protocol = None
        self.current_step = 0
        self.start_time = None
        self.status = ProtocolStatus.NOT_STARTED
        self.quality_metrics = {}
        self.completion_log = []
        
        logger.info("측정 프로토콜 관리자 초기화 완료")
    
    def _initialize_protocols(self) -> Dict[str, List[ProtocolStep]]:
        """표준 측정 프로토콜 초기화"""
        return {
            "standard_health_check": [
                ProtocolStep(
                    phase=MeasurementPhase.PREPARATION,
                    name="측정 준비",
                    description="측정 전 안정 상태 확보",
                    duration=300.0,  # 5분
                    required=True,
                    quality_threshold=0.8,
                    instructions=[
                        "측정 전 5분간 안정 상태를 유지하세요",
                        "카페인, 알코올 섭취를 금지하세요",
                        "과도한 운동을 피하세요",
                        "정상적인 호흡을 유지하세요",
                        "편안한 자세를 취하세요"
                    ],
                    success_criteria=[
                        "5분간 안정 상태 유지",
                        "정상적인 호흡 패턴",
                        "편안한 심리 상태"
                    ],
                    failure_handling="안정 상태가 되지 않으면 측정을 연기하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.CALIBRATION,
                    name="카메라 보정",
                    description="카메라 설정 및 얼굴 감지 보정",
                    duration=60.0,  # 1분
                    required=True,
                    quality_threshold=0.9,
                    instructions=[
                        "카메라를 얼굴에 맞춰주세요",
                        "얼굴이 화면 중앙에 위치하도록 하세요",
                        "적절한 조명을 확보하세요",
                        "안정적인 자세를 취하세요"
                    ],
                    success_criteria=[
                        "얼굴이 정확히 감지됨",
                        "얼굴이 화면 중앙에 위치",
                        "적절한 조명 조건",
                        "안정적인 자세"
                    ],
                    failure_handling="카메라 위치나 조명을 조정하고 다시 시도하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.BASELINE,
                    name="기준선 측정",
                    description="측정 전 초기 상태 기록",
                    duration=30.0,  # 30초
                    required=True,
                    quality_threshold=0.85,
                    instructions=[
                        "30초 동안 정지 상태를 유지하세요",
                        "정상적인 호흡을 계속하세요",
                        "카메라를 움직이지 마세요",
                        "편안한 마음가짐을 유지하세요"
                    ],
                    success_criteria=[
                        "30초 연속 측정 완료",
                        "안정적인 신호 품질",
                        "정상 범위 내 생체신호"
                    ],
                    failure_handling="측정을 중단하고 처음부터 다시 시작하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.MEASUREMENT,
                    name="주요 측정",
                    description="핵심 생체신호 측정",
                    duration=60.0,  # 1분
                    required=True,
                    quality_threshold=0.9,
                    instructions=[
                        "1분 동안 정지 상태를 유지하세요",
                        "정상적인 호흡을 계속하세요",
                        "카메라를 움직이지 마세요",
                        "편안한 마음가짐을 유지하세요"
                    ],
                    success_criteria=[
                        "1분 연속 측정 완료",
                        "높은 신호 품질",
                        "일관된 생체신호 패턴"
                    ],
                    failure_handling="측정을 중단하고 처음부터 다시 시작하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.VALIDATION,
                    name="측정 검증",
                    description="측정 결과 품질 검증",
                    duration=15.0,  # 15초
                    required=True,
                    quality_threshold=0.8,
                    instructions=[
                        "측정 결과를 확인하세요",
                        "품질 지표를 점검하세요",
                        "필요시 재측정을 고려하세요"
                    ],
                    success_criteria=[
                        "모든 품질 지표 통과",
                        "신뢰할 수 있는 측정 결과",
                        "일관된 데이터 패턴"
                    ],
                    failure_handling="품질 기준에 미달하면 재측정을 권장합니다"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.COMPLETION,
                    name="측정 완료",
                    description="측정 결과 정리 및 저장",
                    duration=10.0,  # 10초
                    required=True,
                    quality_threshold=1.0,
                    instructions=[
                        "측정 결과를 확인하세요",
                        "결과를 저장하세요",
                        "필요시 결과를 공유하세요"
                    ],
                    success_criteria=[
                        "측정 결과 저장 완료",
                        "사용자에게 결과 전달",
                        "측정 세션 정리 완료"
                    ],
                    failure_handling="결과 저장에 실패하면 다시 시도하세요"
                )
            ],
            "quick_check": [
                ProtocolStep(
                    phase=MeasurementPhase.PREPARATION,
                    name="빠른 준비",
                    description="1분 준비",
                    duration=60.0,  # 1분
                    required=True,
                    quality_threshold=0.7,
                    instructions=[
                        "1분간 안정 상태를 유지하세요",
                        "정상적인 호흡을 하세요"
                    ],
                    success_criteria=[
                        "1분간 안정 상태 유지",
                        "정상적인 호흡 패턴"
                    ],
                    failure_handling="안정 상태가 되지 않으면 측정을 연기하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.MEASUREMENT,
                    name="빠른 측정",
                    description="30초 측정",
                    duration=30.0,  # 30초
                    required=True,
                    quality_threshold=0.8,
                    instructions=[
                        "30초 동안 정지 상태를 유지하세요",
                        "정상적인 호흡을 계속하세요"
                    ],
                    success_criteria=[
                        "30초 연속 측정 완료",
                        "적절한 신호 품질"
                    ],
                    failure_handling="측정을 중단하고 다시 시도하세요"
                ),
                ProtocolStep(
                    phase=MeasurementPhase.COMPLETION,
                    name="빠른 완료",
                    description="결과 확인",
                    duration=5.0,  # 5초
                    required=True,
                    quality_threshold=1.0,
                    instructions=[
                        "측정 결과를 확인하세요"
                    ],
                    success_criteria=[
                        "측정 결과 확인 완료"
                    ],
                    failure_handling="결과 확인에 실패하면 다시 시도하세요"
                )
            ]
        }
    
    def start_protocol(self, protocol_name: str) -> Dict[str, Any]:
        """
        측정 프로토콜 시작
        
        Args:
            protocol_name: 프로토콜 이름
            
        Returns:
            프로토콜 시작 결과
        """
        try:
            if protocol_name not in self.protocols:
                raise ValueError(f"알 수 없는 프로토콜: {protocol_name}")
            
            self.current_protocol = protocol_name
            self.current_step = 0
            self.start_time = datetime.now()
            self.status = ProtocolStatus.IN_PROGRESS
            self.quality_metrics = {}
            self.completion_log = []
            
            protocol_info = self.protocols[protocol_name]
            first_step = protocol_info[0]
            
            logger.info(f"프로토콜 '{protocol_name}' 시작됨")
            
            return {
                "status": "started",
                "protocol_name": protocol_name,
                "current_step": 0,
                "total_steps": len(protocol_info),
                "current_phase": first_step.phase.value,
                "step_name": first_step.name,
                "instructions": first_step.instructions,
                "duration": first_step.duration,
                "estimated_completion": self.start_time + timedelta(seconds=first_step.duration)
            }
            
        except Exception as e:
            logger.error(f"프로토콜 시작 실패: {str(e)}")
            self.status = ProtocolStatus.FAILED
            raise
    
    def get_current_step_info(self) -> Optional[Dict[str, Any]]:
        """현재 단계 정보 조회"""
        if not self.current_protocol or self.status != ProtocolStatus.IN_PROGRESS:
            return None
        
        try:
            protocol = self.protocols[self.current_protocol]
            if self.current_step >= len(protocol):
                return None
            
            step = protocol[self.current_step]
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "step_index": self.current_step,
                "total_steps": len(protocol),
                "phase": step.phase.value,
                "name": step.name,
                "description": step.description,
                "duration": step.duration,
                "elapsed_time": elapsed_time,
                "remaining_time": max(0, step.duration - elapsed_time),
                "instructions": step.instructions,
                "success_criteria": step.success_criteria,
                "quality_threshold": step.quality_threshold,
                "progress_percentage": min(100, (elapsed_time / step.duration) * 100)
            }
            
        except Exception as e:
            logger.error(f"현재 단계 정보 조회 실패: {str(e)}")
            return None
    
    def advance_step(self, quality_score: float = None) -> Dict[str, Any]:
        """
        다음 단계로 진행
        
        Args:
            quality_score: 현재 단계의 품질 점수 (0.0 ~ 1.0)
            
        Returns:
            단계 진행 결과
        """
        try:
            if not self.current_protocol or self.status != ProtocolStatus.IN_PROGRESS:
                raise RuntimeError("진행 중인 프로토콜이 없습니다")
            
            protocol = self.protocols[self.current_protocol]
            current_step = protocol[self.current_step]
            
            # 품질 점수 기록
            if quality_score is not None:
                self.quality_metrics[f"step_{self.current_step}"] = {
                    "quality_score": quality_score,
                    "timestamp": datetime.now().isoformat(),
                    "threshold": current_step.quality_threshold,
                    "passed": quality_score >= current_step.quality_threshold
                }
            
            # 현재 단계 완료 로그
            self.completion_log.append({
                "step_index": self.current_step,
                "step_name": current_step.name,
                "phase": current_step.phase.value,
                "quality_score": quality_score,
                "completed_at": datetime.now().isoformat(),
                "duration": current_step.duration
            })
            
            # 다음 단계로 이동
            self.current_step += 1
            
            if self.current_step >= len(protocol):
                # 프로토콜 완료
                self.status = ProtocolStatus.COMPLETED
                completion_time = datetime.now()
                total_duration = (completion_time - self.start_time).total_seconds()
                
                logger.info(f"프로토콜 '{self.current_protocol}' 완료됨 (총 소요시간: {total_duration:.1f}초)")
                
                return {
                    "status": "completed",
                    "protocol_name": self.current_protocol,
                    "total_steps": len(protocol),
                    "total_duration": total_duration,
                    "quality_summary": self._generate_quality_summary(),
                    "completion_log": self.completion_log
                }
            else:
                # 다음 단계 정보
                next_step = protocol[self.current_step]
                return {
                    "status": "advanced",
                    "current_step": self.current_step,
                    "total_steps": len(protocol),
                    "next_phase": next_step.phase.value,
                    "next_step_name": next_step.name,
                    "next_instructions": next_step.instructions,
                    "next_duration": next_step.duration,
                    "estimated_completion": datetime.now() + timedelta(seconds=next_step.duration)
                }
                
        except Exception as e:
            logger.error(f"단계 진행 실패: {str(e)}")
            self.status = ProtocolStatus.FAILED
            raise
    
    def pause_protocol(self) -> Dict[str, Any]:
        """프로토콜 일시정지"""
        if self.status == ProtocolStatus.IN_PROGRESS:
            self.status = ProtocolStatus.PAUSED
            logger.info(f"프로토콜 '{self.current_protocol}' 일시정지됨")
            
            return {
                "status": "paused",
                "protocol_name": self.current_protocol,
                "current_step": self.current_step,
                "paused_at": datetime.now().isoformat()
            }
        else:
            raise RuntimeError("일시정지할 수 있는 프로토콜이 없습니다")
    
    def resume_protocol(self) -> Dict[str, Any]:
        """프로토콜 재개"""
        if self.status == ProtocolStatus.PAUSED:
            self.status = ProtocolStatus.IN_PROGRESS
            logger.info(f"프로토콜 '{self.current_protocol}' 재개됨")
            
            return {
                "status": "resumed",
                "protocol_name": self.current_protocol,
                "current_step": self.current_step,
                "resumed_at": datetime.now().isoformat()
            }
        else:
            raise RuntimeError("재개할 수 있는 프로토콜이 없습니다")
    
    def get_protocol_status(self) -> Dict[str, Any]:
        """프로토콜 상태 조회"""
        if not self.current_protocol:
            return {
                "status": "no_protocol",
                "message": "진행 중인 프로토콜이 없습니다"
            }
        
        protocol = self.protocols[self.current_protocol]
        elapsed_time = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "protocol_name": self.current_protocol,
            "status": self.status.value,
            "current_step": self.current_step,
            "total_steps": len(protocol),
            "elapsed_time": elapsed_time,
            "quality_metrics": self.quality_metrics,
            "completion_log": self.completion_log,
            "start_time": self.start_time.isoformat() if self.start_time else None
        }
    
    def _generate_quality_summary(self) -> Dict[str, Any]:
        """품질 요약 생성"""
        if not self.quality_metrics:
            return {
                "overall_quality": 0.0,
                "steps_passed": 0,
                "total_steps": 0,
                "quality_distribution": {}
            }
        
        quality_scores = list(self.quality_metrics.values())
        overall_quality = np.mean([qs["quality_score"] for qs in quality_scores])
        steps_passed = sum(1 for qs in quality_scores if qs["passed"])
        total_steps = len(quality_scores)
        
        quality_distribution = {
            "excellent": sum(1 for qs in quality_scores if qs["quality_score"] >= 0.9),
            "good": sum(1 for qs in quality_scores if 0.8 <= qs["quality_score"] < 0.9),
            "fair": sum(1 for qs in quality_scores if 0.7 <= qs["quality_score"] < 0.8),
            "poor": sum(1 for qs in quality_scores if qs["quality_score"] < 0.7)
        }
        
        return {
            "overall_quality": overall_quality,
            "steps_passed": steps_passed,
            "total_steps": total_steps,
            "pass_rate": steps_passed / total_steps if total_steps > 0 else 0,
            "quality_distribution": quality_distribution
        }
    
    def get_available_protocols(self) -> List[Dict[str, Any]]:
        """사용 가능한 프로토콜 목록 조회"""
        protocols_info = []
        
        for name, steps in self.protocols.items():
            total_duration = sum(step.duration for step in steps)
            phases = [step.phase.value for step in steps]
            
            protocols_info.append({
                "name": name,
                "description": f"{len(steps)}단계, 총 {total_duration/60:.1f}분",
                "total_steps": len(steps),
                "total_duration": total_duration,
                "phases": list(set(phases)),
                "estimated_time": f"{total_duration/60:.1f}분"
            })
        
        return protocols_info
    
    def reset_protocol(self):
        """프로토콜 초기화"""
        self.current_protocol = None
        self.current_step = 0
        self.start_time = None
        self.status = ProtocolStatus.NOT_STARTED
        self.quality_metrics = {}
        self.completion_log = []
        
        logger.info("프로토콜이 초기화되었습니다")
    
    def export_protocol_report(self, filepath: str = None) -> str:
        """프로토콜 실행 보고서 내보내기"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"protocol_report_{timestamp}.json"
        
        try:
            report = {
                "protocol_name": self.current_protocol,
                "status": self.status.value,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "completion_time": datetime.now().isoformat(),
                "total_duration": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "quality_metrics": self.quality_metrics,
                "completion_log": self.completion_log,
                "quality_summary": self._generate_quality_summary() if self.quality_metrics else None
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"프로토콜 보고서가 {filepath}에 저장되었습니다")
            return filepath
            
        except Exception as e:
            logger.error(f"프로토콜 보고서 내보내기 실패: {str(e)}")
            raise
