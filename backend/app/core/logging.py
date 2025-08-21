import logging
import os
from datetime import datetime
from app.core.config import settings

def setup_logging():
    """로깅 시스템을 설정합니다."""
    
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(settings.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 포맷 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 루트 로거 설정
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 콘솔 출력
            logging.StreamHandler(),
            # 파일 출력
            logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
        ]
    )
    
    # 특정 모듈 로그 레벨 설정
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # 로그 시작 메시지
    logger = logging.getLogger(__name__)
    logger.info("로깅 시스템이 초기화되었습니다.")
    logger.info(f"로그 레벨: {settings.LOG_LEVEL}")
    logger.info(f"로그 파일: {settings.LOG_FILE}")

def get_logger(name: str) -> logging.Logger:
    """지정된 이름의 로거를 반환합니다."""
    return logging.getLogger(name)

# 감사 로그 전용 함수
def log_audit_event(
    event_type: str,
    user_id: str = None,
    details: dict = None,
    ip_address: str = None
):
    """감사 로그를 기록합니다."""
    if not settings.AUDIT_LOG_ENABLED:
        return
    
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(logging.INFO)
    
    # 감사 로그 파일 핸들러 추가
    if not audit_logger.handlers:
        audit_file = "logs/audit.log"
        audit_dir = os.path.dirname(audit_file)
        if not os.path.exists(audit_dir):
            os.makedirs(audit_dir)
        
        file_handler = logging.FileHandler(audit_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        audit_logger.addHandler(file_handler)
    
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details or {}
    }
    
    audit_logger.info(f"AUDIT: {audit_data}")

# 의료어 필터 로그 전용 함수
def log_medical_term_filter(
    original_text: str,
    filtered_text: str,
    filtered_terms: list,
    session_id: str
):
    """의료어 필터 로그를 기록합니다."""
    filter_logger = logging.getLogger("medical_filter")
    filter_logger.setLevel(logging.INFO)
    
    # 필터 로그 파일 핸들러 추가
    if not filter_logger.handlers:
        filter_file = "logs/medical_filter.log"
        filter_dir = os.path.dirname(filter_file)
        if not os.path.exists(filter_dir):
            os.makedirs(filter_dir)
        
        file_handler = logging.FileHandler(filter_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        filter_logger.addHandler(file_handler)
    
    filter_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "original_text": original_text,
        "filtered_text": filtered_text,
        "filtered_terms": filtered_terms,
        "filter_count": len(filtered_terms)
    }
    
    filter_logger.info(f"MEDICAL_FILTER: {filter_data}") 