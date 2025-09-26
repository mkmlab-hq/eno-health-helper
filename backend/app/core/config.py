from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "엔오건강도우미"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS 설정
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://eno-health-helper.vercel.app"
    ]
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql://user:password@localhost/eno_health"
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MKM Core AI 설정
    MKM_CORE_AI_URL: str = "http://localhost:8001"
    MKM_CORE_AI_TIMEOUT: int = 30
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/eno_health.log"
    
    # Redis 설정
    REDIS_URL: str = "redis://localhost:6379"
    
    # 의료어 필터 설정
    MEDICAL_TERMS_FILTER_ENABLED: bool = True
    MEDICAL_TERMS_FILE: str = "data/medical_terms_filter.json"
    
    # 데이터 보호 설정
    DATA_RETENTION_SECONDS: int = 0  # 즉시 파기
    AUDIT_LOG_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()

# 환경별 설정 오버라이드
if os.getenv("ENVIRONMENT") == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
    settings.ALLOWED_HOSTS = [
        "https://eno-health-helper.vercel.app",
        "https://eno-health-helper.com"
    ] 