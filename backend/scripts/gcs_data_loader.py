#!/usr/bin/env python3
"""
구글 클라우드 스토리지에서 RPPG 및 음성 데이터 로더
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile

# Google Cloud 라이브러리 import
try:
    from google.cloud import storage
    from google.auth import default
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    logging.warning("Google Cloud Storage 라이브러리가 설치되지 않음")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GCSDataLoader:
    """구글 클라우드 스토리지 데이터 로더"""
    
    def __init__(self, project_id: str = None, bucket_name: str = None):
        """
        GCS 데이터 로더 초기화
        
        Args:
            project_id: Google Cloud 프로젝트 ID
            bucket_name: GCS 버킷 이름
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME')
        
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError("Google Cloud Storage 라이브러리가 설치되지 않았습니다")
        
        # GCS 클라이언트 초기화
        self.storage_client = None
        self.bucket = None
        
        # 데이터 저장 디렉토리
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info(f"GCS 데이터 로더 초기화 (프로젝트: {self.project_id})")
    
    def authenticate(self, key_path: str = None) -> bool:
        """
        Google Cloud 인증
        
        Args:
            key_path: 서비스 계정 키 파일 경로
            
        Returns:
            인증 성공 여부
        """
        try:
            if key_path and os.path.exists(key_path):
                # 서비스 계정 키 파일 사용
                credentials = service_account.Credentials.from_service_account_file(
                    key_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                logger.info(f"서비스 계정 키 파일로 인증: {key_path}")
            else:
                # 기본 인증 사용 (gcloud auth application-default login)
                credentials, project = default()
                if not self.project_id:
                    self.project_id = project
                logger.info("기본 인증 사용")
            
            self.storage_client = storage.Client(
                credentials=credentials,
                project=self.project_id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"인증 실패: {e}")
            return False
    
    def connect_to_bucket(self) -> bool:
        """
        GCS 버킷에 연결
        
        Returns:
            연결 성공 여부
        """
        try:
            if not self.storage_client:
                raise ValueError("스토리지 클라이언트가 초기화되지 않았습니다")
            
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            # 버킷 존재 확인
            if not self.bucket.exists():
                logger.error(f"버킷이 존재하지 않음: {self.bucket_name}")
                return False
            
            logger.info(f"GCS 버킷 연결 성공: {self.bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"버킷 연결 실패: {e}")
            return False
    
    def list_data_files(self, prefix: str = "") -> List[Dict]:
        """
        GCS 버킷의 데이터 파일 목록 조회
        
        Args:
            prefix: 파일 경로 접두사
            
        Returns:
            파일 정보 리스트
        """
        try:
            if not self.bucket:
                raise ValueError("버킷에 연결되지 않았습니다")
            
            files = []
            blobs = self.bucket.list_blobs(prefix=prefix)
            
            for blob in blobs:
                if not blob.name.endswith('/'):  # 디렉토리 제외
                    file_info = {
                        "name": blob.name,
                        "size": blob.size,
                        "updated": blob.updated,
                        "content_type": blob.content_type
                    }
                    files.append(file_info)
            
            logger.info(f"총 {len(files)}개 파일 발견")
            return files
            
        except Exception as e:
            logger.error(f"파일 목록 조회 실패: {e}")
            return []
    
    def download_rppg_data(self, prefix: str = "rppg/") -> List[Path]:
        """
        RPPG 데이터 다운로드
        
        Args:
            prefix: RPPG 데이터 접두사
            
        Returns:
            다운로드된 파일 경로 리스트
        """
        try:
            logger.info("RPPG 데이터 다운로드 시작...")
            
            # RPPG 데이터 파일 목록 조회
            rppg_files = self.list_data_files(prefix=prefix)
            
            if not rppg_files:
                logger.warning("RPPG 데이터 파일을 찾을 수 없습니다")
                return []
            
            downloaded_files = []
            rppg_dir = self.data_dir / "rppg"
            rppg_dir.mkdir(exist_ok=True)
            
            for file_info in rppg_files:
                try:
                    # 파일명 추출
                    filename = Path(file_info["name"]).name
                    local_path = rppg_dir / filename
                    
                    # 파일 다운로드
                    blob = self.bucket.blob(file_info["name"])
                    blob.download_to_filename(local_path)
                    
                    logger.info(f"RPPG 파일 다운로드 완료: {filename}")
                    downloaded_files.append(local_path)
                    
                except Exception as e:
                    logger.error(f"파일 다운로드 실패 {file_info['name']}: {e}")
                    continue
            
            logger.info(f"RPPG 데이터 다운로드 완료: {len(downloaded_files)}개 파일")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"RPPG 데이터 다운로드 실패: {e}")
            return []
    
    def download_voice_data(self, prefix: str = "voice/") -> List[Path]:
        """
        음성 데이터 다운로드
        
        Args:
            prefix: 음성 데이터 접두사
            
        Returns:
            다운로드된 파일 경로 리스트
        """
        try:
            logger.info("음성 데이터 다운로드 시작...")
            
            # 음성 데이터 파일 목록 조회
            voice_files = self.list_data_files(prefix=prefix)
            
            if not voice_files:
                logger.warning("음성 데이터 파일을 찾을 수 없습니다")
                return []
            
            downloaded_files = []
            voice_dir = self.data_dir / "voice"
            voice_dir.mkdir(exist_ok=True)
            
            for file_info in voice_files:
                try:
                    # 파일명 추출
                    filename = Path(file_info["name"]).name
                    local_path = voice_dir / filename
                    
                    # 파일 다운로드
                    blob = self.bucket.blob(file_info["name"])
                    blob.download_to_filename(local_path)
                    
                    logger.info(f"음성 파일 다운로드 완료: {filename}")
                    downloaded_files.append(local_path)
                    
                except Exception as e:
                    logger.error(f"파일 다운로드 실패 {file_info['name']}: {e}")
                    continue
            
            logger.info(f"음성 데이터 다운로드 완료: {len(downloaded_files)}개 파일")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"음성 데이터 다운로드 실패: {e}")
            return []
    
    def get_data_summary(self) -> Dict:
        """
        다운로드된 데이터 요약 정보
        
        Returns:
            데이터 요약 정보
        """
        try:
            summary = {
                "rppg_files": [],
                "voice_files": [],
                "total_size": 0,
                "file_types": {}
            }
            
            # RPPG 데이터 요약
            rppg_dir = self.data_dir / "rppg"
            if rppg_dir.exists():
                for file_path in rppg_dir.glob("*"):
                    if file_path.is_file():
                        file_info = {
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "path": str(file_path)
                        }
                        summary["rppg_files"].append(file_info)
                        summary["total_size"] += file_info["size"]
                        
                        # 파일 타입 분류
                        ext = file_path.suffix.lower()
                        summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
            
            # 음성 데이터 요약
            voice_dir = self.data_dir / "voice"
            if voice_dir.exists():
                for file_path in voice_dir.glob("*"):
                    if file_path.is_file():
                        file_info = {
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "path": str(file_path)
                        }
                        summary["voice_files"].append(file_info)
                        summary["total_size"] += file_info["size"]
                        
                        # 파일 타입 분류
                        ext = file_path.suffix.lower()
                        summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"데이터 요약 생성 실패: {e}")
            return {}


def main():
    """메인 실행 함수"""
    print("🚀 구글 클라우드 스토리지 데이터 로더")
    print("=" * 50)
    
    try:
        # 환경 변수 확인
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        bucket_name = os.getenv('GCS_BUCKET_NAME')
        
        if not project_id:
            print("❌ GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다")
            print("💡 해결방법: export GOOGLE_CLOUD_PROJECT=your-project-id")
            return
        
        if not bucket_name:
            print("❌ GCS_BUCKET_NAME 환경 변수가 설정되지 않았습니다")
            print("💡 해결방법: export GCS_BUCKET_NAME=your-bucket-name")
            return
        
        print(f"📁 프로젝트: {project_id}")
        print(f"🪣 버킷: {bucket_name}")
        
        # 데이터 로더 초기화
        loader = GCSDataLoader(project_id, bucket_name)
        
        # 인증
        print("\n🔑 Google Cloud 인증 중...")
        if not loader.authenticate():
            print("❌ 인증 실패")
            return
        
        # 버킷 연결
        print("\n🔗 GCS 버킷 연결 중...")
        if not loader.connect_to_bucket():
            print("❌ 버킷 연결 실패")
            return
        
        # 데이터 다운로드
        print("\n📥 RPPG 데이터 다운로드 중...")
        rppg_files = loader.download_rppg_data()
        
        print("\n🎤 음성 데이터 다운로드 중...")
        voice_files = loader.download_voice_data()
        
        # 결과 요약
        print("\n📊 다운로드 결과 요약")
        print("=" * 50)
        
        summary = loader.get_data_summary()
        
        print(f"RPPG 파일: {len(summary['rppg_files'])}개")
        print(f"음성 파일: {len(summary['voice_files'])}개")
        print(f"총 크기: {summary['total_size'] / 1024 / 1024:.2f} MB")
        
        if summary['file_types']:
            print("\n파일 타입별 분포:")
            for ext, count in summary['file_types'].items():
                print(f"  {ext}: {count}개")
        
        if rppg_files or voice_files:
            print("\n✅ 데이터 다운로드 완료!")
            print("💡 이제 eno-health-helper에서 실제 데이터를 사용할 수 있습니다")
        else:
            print("\n⚠️ 다운로드된 파일이 없습니다")
            print("💡 GCS 버킷에 데이터가 있는지 확인해주세요")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n💡 문제 해결 방법:")
        print("1. Google Cloud SDK 설치 및 인증")
        print("2. 환경 변수 설정")
        print("3. 필요한 라이브러리 설치: pip install google-cloud-storage")


if __name__ == "__main__":
    main() 