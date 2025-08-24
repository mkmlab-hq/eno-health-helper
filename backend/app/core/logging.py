import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from app.core.config import settings

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return str(log)

def setup_logging():
    """로깅 시스템을 설정합니다."""
    
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(settings.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 포맷 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 루트 로거 가져오기
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # 기존 핸들러 제거 후 재설정
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    # 파일 핸들러 (일 단위 로테이션, 7일 보관)
    file_handler = TimedRotatingFileHandler(settings.LOG_FILE, when='D', interval=1, backupCount=7, encoding='utf-8')
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
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
        
        file_handler = TimedRotatingFileHandler(audit_file, when='D', interval=1, backupCount=14, encoding='utf-8')
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
        
        file_handler = TimedRotatingFileHandler(filter_file, when='D', interval=1, backupCount=14, encoding='utf-8')
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