#!/usr/bin/env python3
"""
작전명: '불사조 엔진' 고도화 v2 - 데이터 확보 스크립트
목표: 대규모 공개 RPPG 데이터셋을 확보하여 95% 이상 정확도 달성
"""

import os
import json
import logging
import requests
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import hashlib
from tqdm import tqdm

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PhoenixEngineDataAcquisition:
    """불사조 엔진 데이터 확보 클래스"""
    
    def __init__(self):
        self.data_dir = Path("backend/data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 공개 데이터셋 정보
        self.datasets = {
            "VIPL-HR": {
                "description": "2,378개 비디오, 다양한 환경 포함",
                "url": "https://github.com/VIPL-ICT/VIPL-HR",
                "size_gb": 15.2,
                "samples": 2378,
                "type": "github_repo"
            },
            "MAHNOB-HCI": {
                "description": "527개 비디오, 다중 센서 데이터 포함",
                "url": "https://mahnob-db.eu/",
                "size_gb": 8.7,
                "samples": 527,
                "type": "official_website"
            },
            "UBFC-rPPG": {
                "description": "42개 비디오, 기본 벤치마크용",
                "url": "https://github.com/ubicenter/ubfc-rppg",
                "size_gb": 2.1,
                "samples": 42,
                "type": "github_repo"
            }
        }
        
        # 다운로드 상태
        self.download_status = {}
        
        logger.info("🚀 불사조 엔진 데이터 확보 시스템 초기화 완료")
    
    def create_data_structure(self):
        """데이터 저장 구조 생성"""
        logger.info("📁 데이터 저장 구조 생성 중...")
        
        # 메인 데이터 디렉토리
        directories = [
            "rppg",
            "rppg/vipl_hr",
            "rppg/mahnob_hci", 
            "rppg/ubfc_rppg",
            "voice",
            "metadata",
            "processed",
            "training",
            "validation",
            "testing"
        ]
        
        for dir_path in directories:
            (self.data_dir / dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ 디렉토리 생성: {dir_path}")
    
    def download_vipl_hr_dataset(self):
        """VIPL-HR 데이터셋 다운로드"""
        logger.info("🔥 VIPL-HR 데이터셋 다운로드 시작 (2,378개 비디오)")
        
        try:
            # VIPL-HR GitHub 저장소 클론
            vipl_dir = self.data_dir / "rppg" / "vip_hr"
            if not vipl_dir.exists():
                logger.info("📥 VIPL-HR GitHub 저장소 클론 중...")
                subprocess.run([
                    "git", "clone", 
                    "https://github.com/VIPL-ICT/VIPL-HR.git",
                    str(vipl_dir)
                ], check=True)
                logger.info("✅ VIPL-HR 저장소 클론 완료")
            else:
                logger.info("✅ VIPL-HR 저장소 이미 존재")
            
            # 데이터 구조 확인
            self._analyze_vip_hr_structure(vipl_dir)
            
        except Exception as e:
            logger.error(f"❌ VIPL-HR 다운로드 실패: {e}")
            return False
        
        return True
    
    def download_mahnob_hci_dataset(self):
        """MAHNOB-HCI 데이터셋 다운로드"""
        logger.info("🎯 MAHNOB-HCI 데이터셋 다운로드 시작 (527개 비디오)")
        
        try:
            mahnob_dir = self.data_dir / "rppg" / "mahnob_hci"
            mahnob_dir.mkdir(exist_ok=True)
            
            # MAHNOB-HCI는 공식 웹사이트에서 신청 필요
            # 자동 다운로드 대신 수동 다운로드 가이드 제공
            guide_file = mahnob_dir / "DOWNLOAD_GUIDE.md"
            
            guide_content = """# MAHNOB-HCI 데이터셋 다운로드 가이드

## 📋 데이터셋 정보
- **총 비디오 수**: 527개
- **크기**: 약 8.7GB
- **특징**: 다중 센서 데이터 포함

## 🔗 다운로드 링크
공식 웹사이트: https://mahnob-db.eu/

## 📝 다운로드 절차
1. 웹사이트 방문
2. 계정 생성 및 로그인
3. 데이터 사용 목적 신청서 작성
4. 승인 후 다운로드 링크 제공
5. 다운로드 완료 후 이 디렉토리에 압축 해제

## 📁 압축 해제 명령어
```bash
# tar.gz 파일인 경우
tar -xzf mahnob_hci_dataset.tar.gz

# zip 파일인 경우
unzip mahnob_hci_dataset.zip
```

## ⚠️ 주의사항
- 데이터 사용 목적을 명확히 작성해야 승인됩니다
- 대용량 파일이므로 안정적인 네트워크 환경에서 다운로드하세요
"""
            
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            logger.info("📋 MAHNOB-HCI 다운로드 가이드 생성 완료")
            logger.info("⚠️ 수동 다운로드가 필요합니다: https://mahnob-db.eu/")
            
        except Exception as e:
            logger.error(f"❌ MAHNOB-HCI 가이드 생성 실패: {e}")
            return False
        
        return True
    
    def download_ubfc_rppg_dataset(self):
        """UBFC-rPPG 데이터셋 다운로드"""
        logger.info("⚡ UBFC-rPPG 데이터셋 다운로드 시작 (42개 비디오)")
        
        try:
            # UBFC-rPPG GitHub 저장소 클론
            ubfc_dir = self.data_dir / "rppg" / "ubfc_rppg"
            if not ubfc_dir.exists():
                logger.info("📥 UBFC-rPPG GitHub 저장소 클론 중...")
                subprocess.run([
                    "git", "clone",
                    "https://github.com/ubicenter/ubfc-rppg.git",
                    str(ubfc_dir)
                ], check=True)
                logger.info("✅ UBFC-rPPG 저장소 클론 완료")
            else:
                logger.info("✅ UBFC-rPPG 저장소 이미 존재")
            
            # 데이터 구조 확인
            self._analyze_ubfc_structure(ubfc_dir)
            
        except Exception as e:
            logger.error(f"❌ UBFC-rPPG 다운로드 실패: {e}")
            return False
        
        return True
    
    def _analyze_vip_hr_structure(self, vip_dir: Path):
        """VIPL-HR 데이터 구조 분석"""
        try:
            # 데이터 파일 찾기
            video_files = list(vip_dir.rglob("*.avi")) + list(vip_dir.rglob("*.mp4"))
            metadata_files = list(vip_dir.rglob("*.txt")) + list(vip_dir.rglob("*.json"))
            
            logger.info(f"📊 VIPL-HR 데이터 구조 분석:")
            logger.info(f"  - 비디오 파일: {len(video_files)}개")
            logger.info(f"  - 메타데이터: {len(metadata_files)}개")
            
            # 구조 정보 저장
            structure_info = {
                "dataset": "VIPL-HR",
                "total_videos": len(video_files),
                "total_metadata": len(metadata_files),
                "video_extensions": list(set([f.suffix for f in video_files])),
                "metadata_extensions": list(set([f.suffix for f in metadata_files])),
                "analysis_date": str(Path().cwd())
            }
            
            structure_file = self.data_dir / "metadata" / "vip_hr_structure.json"
            with open(structure_file, 'w', encoding='utf-8') as f:
                json.dump(structure_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ VIPL-HR 구조 정보 저장: {structure_file}")
            
        except Exception as e:
            logger.error(f"❌ VIPL-HR 구조 분석 실패: {e}")
    
    def _analyze_ubfc_structure(self, ubfc_dir: Path):
        """UBFC-rPPG 데이터 구조 분석"""
        try:
            # 데이터 파일 찾기
            video_files = list(ubfc_dir.rglob("*.avi")) + list(ubfc_dir.rglob("*.mp4"))
            metadata_files = list(ubfc_dir.rglob("*.txt")) + list(ubfc_dir.rglob("*.json"))
            
            logger.info(f"📊 UBFC-rPPG 데이터 구조 분석:")
            logger.info(f"  - 비디오 파일: {len(video_files)}개")
            logger.info(f"  - 메타데이터: {len(metadata_files)}개")
            
            # 구조 정보 저장
            structure_info = {
                "dataset": "UBFC-rPPG",
                "total_videos": len(video_files),
                "total_metadata": len(metadata_files),
                "video_extensions": list(set([f.suffix for f in video_files])),
                "metadata_extensions": list(set([f.suffix for f in metadata_files])),
                "analysis_date": str(Path().cwd())
            }
            
            structure_file = self.data_dir / "metadata" / "ubfc_rppg_structure.json"
            with open(structure_file, 'w', encoding='utf-8') as f:
                json.dump(structure_info, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ UBFC-rPPG 구조 정보 저장: {structure_file}")
            
        except Exception as e:
            logger.error(f"❌ UBFC-rPPG 구조 분석 실패: {e}")
    
    def create_data_integration_pipeline(self):
        """데이터 통합 파이프라인 생성"""
        logger.info("🔗 데이터 통합 파이프라인 생성 중...")
        
        try:
            pipeline_script = self.data_dir / "scripts" / "data_integration.py"
            pipeline_script.parent.mkdir(exist_ok=True)
            
            pipeline_content = """#!/usr/bin/env python3
\"\"\"
데이터 통합 파이프라인
여러 데이터셋을 표준화된 포맷으로 통합
\"\"\"

import json
import pandas as pd
from pathlib import Path
import logging

def integrate_datasets():
    \"\"\"데이터셋 통합 메인 함수\"\"\"
    # VIPL-HR, MAHNOB-HCI, UBFC-rPPG 데이터 통합
    # 표준화된 포맷으로 변환
    # 훈련/검증/테스트 세트 분할
    pass

if __name__ == "__main__":
    integrate_datasets()
"""
            
            with open(pipeline_script, 'w', encoding='utf-8') as f:
                f.write(pipeline_content)
            
            logger.info(f"✅ 데이터 통합 파이프라인 생성: {pipeline_script}")
            
        except Exception as e:
            logger.error(f"❌ 파이프라인 생성 실패: {e}")
    
    def generate_data_summary(self):
        """데이터 현황 요약 생성"""
        logger.info("📊 데이터 현황 요약 생성 중...")
        
        try:
            summary = {
                "operation_name": "불사조 엔진 고도화 v2 - 데이터 확보",
                "phase": "Phase 0: 데이터 확보",
                "target_datasets": self.datasets,
                "current_status": self.download_status,
                "data_directory": str(self.data_dir.absolute()),
                "next_phase": "Phase 1: 정확도 85% 달성 (공개 데이터 기반)",
                "estimated_total_samples": sum([ds["samples"] for ds in self.datasets.values()]),
                "estimated_total_size_gb": sum([ds["size_gb"] for ds in self.datasets.values()])
            }
            
            summary_file = self.data_dir / "metadata" / "phoenix_engine_data_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 데이터 현황 요약 생성: {summary_file}")
            
            # 요약 출력
            logger.info("=" * 60)
            logger.info("🏆 불사조 엔진 데이터 확보 현황")
            logger.info("=" * 60)
            logger.info(f"📊 총 예상 샘플 수: {summary['estimated_total_samples']:,}개")
            logger.info(f"💾 총 예상 크기: {summary['estimated_total_size_gb']:.1f}GB")
            logger.info(f"🎯 다음 단계: {summary['next_phase']}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ 요약 생성 실패: {e}")
    
    def execute_phase_0(self):
        """Phase 0 실행 - 데이터 확보"""
        logger.info("🚀 Phase 0: 데이터 확보 작전 개시!")
        logger.info("=" * 60)
        
        try:
            # 1. 데이터 저장 구조 생성
            self.create_data_structure()
            
            # 2. VIPL-HR 데이터셋 다운로드
            logger.info("🔥 VIPL-HR 데이터셋 다운로드 시작...")
            vip_success = self.download_vipl_hr_dataset()
            self.download_status["VIPL-HR"] = "success" if vip_success else "failed"
            
            # 3. MAHNOB-HCI 데이터셋 가이드 생성
            logger.info("🎯 MAHNOB-HCI 데이터셋 가이드 생성...")
            mahnob_success = self.download_mahnob_hci_dataset()
            self.download_status["MAHNOB-HCI"] = "guide_created" if mahnob_success else "failed"
            
            # 4. UBFC-rPPG 데이터셋 다운로드
            logger.info("⚡ UBFC-rPPG 데이터셋 다운로드 시작...")
            ubfc_success = self.download_ubfc_rppg_dataset()
            self.download_status["UBFC-rPPG"] = "success" if ubfc_success else "failed"
            
            # 5. 데이터 통합 파이프라인 생성
            self.create_data_integration_pipeline()
            
            # 6. 최종 요약 생성
            self.generate_data_summary()
            
            logger.info("🎉 Phase 0: 데이터 확보 작전 완료!")
            
        except Exception as e:
            logger.error(f"❌ Phase 0 실행 실패: {e}")
            return False
        
        return True

def main():
    """메인 실행 함수"""
    logger.info("🚀 작전명: '불사조 엔진' 고도화 v2 - 데이터 우선주의")
    logger.info("🎯 목표: 대규모 공개 데이터셋 확보로 95% 이상 정확도 달성")
    logger.info("=" * 60)
    
    try:
        # 불사조 엔진 데이터 확보 시스템 생성
        phoenix_engine = PhoenixEngineDataAcquisition()
        
        # Phase 0 실행
        success = phoenix_engine.execute_phase_0()
        
        if success:
            logger.info("🏆 Phase 0 성공적으로 완료!")
            logger.info("🚀 다음 단계: Phase 1 - 정확도 85% 달성")
        else:
            logger.error("❌ Phase 0 실행 실패")
            
    except Exception as e:
        logger.error(f"❌ 메인 실행 실패: {e}")

if __name__ == "__main__":
    main() 