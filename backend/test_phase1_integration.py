#!/usr/bin/env python3
"""
Phase 1 통합 테스트 스크립트
MediaPipe Face Mesh + MAE 모델 통합 테스트
"""

import sys
import os
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mediapipe_integration():
    """MediaPipe Face Mesh 통합 테스트"""
    try:
        logger.info("🧪 MediaPipe Face Mesh 통합 테스트 시작...")
        
        # MediaPipe import 테스트
        import mediapipe as mp
        logger.info("✅ MediaPipe import 성공")
        
        # Face Mesh 초기화 테스트
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("✅ MediaPipe Face Mesh 초기화 성공")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MediaPipe 통합 테스트 실패: {e}")
        return False

def test_mae_model_integration():
    """MAE 모델 통합 테스트"""
    try:
        logger.info("🧪 MAE 모델 통합 테스트 시작...")
        
        # PyTorch import 테스트
        import torch
        logger.info(f"✅ PyTorch import 성공: {torch.__version__}")
        
        # MAE 분석기 import 테스트
        from app.services.mae_rppg_analyzer import MAERPPGAnalyzer
        logger.info("✅ MAE rPPG 분석기 import 성공")
        
        # MAE 분석기 인스턴스 생성 테스트
        analyzer = MAERPPGAnalyzer()
        logger.info(f"✅ MAE 분석기 생성 성공: 모델 로드={analyzer.model_loaded}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MAE 모델 통합 테스트 실패: {e}")
        return False

def test_rppg_analyzer_integration():
    """rPPG 분석기 통합 테스트"""
    try:
        logger.info("🧪 rPPG 분석기 통합 테스트 시작...")
        
        # rPPG 분석기 import 테스트
        from app.services.real_rppg_analyzer import RealRPPGAnalyzer
        logger.info("✅ rPPG 분석기 import 성공")
        
        # rPPG 분석기 인스턴스 생성 테스트
        analyzer = RealRPPGAnalyzer()
        logger.info(f"✅ rPPG 분석기 생성 성공: MediaPipe={analyzer.face_mesh is not None}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ rPPG 분석기 통합 테스트 실패: {e}")
        return False

def test_end_to_end_analysis():
    """End-to-End 분석 테스트"""
    try:
        logger.info("🧪 End-to-End 분석 테스트 시작...")
        
        # 테스트 데이터 생성
        test_video_data = b"test_video_data_for_analysis"
        test_frame_count = 200
        
        # rPPG 분석기로 테스트
        from app.services.real_rppg_analyzer import RealRPPGAnalyzer
        rppg_analyzer = RealRPPGAnalyzer()
        
        rppg_result = rppg_analyzer.analyze_video_frames(test_video_data, test_frame_count)
        logger.info(f"✅ rPPG 분석 완료: {rppg_result['analysis_method']}")
        
        # MAE 분석기로 테스트
        from app.services.mae_rppg_analyzer import MAERPPGAnalyzer
        mae_analyzer = MAERPPGAnalyzer()
        
        mae_result = mae_analyzer.analyze_rppg_with_mae(test_video_data, test_frame_count)
        logger.info(f"✅ MAE 분석 완료: {mae_result['analysis_method']}")
        
        # 결과 비교
        logger.info("📊 분석 결과 비교:")
        logger.info(f"   rPPG: HR={rppg_result['heart_rate']} BPM, 품질={rppg_result['signal_quality']}")
        logger.info(f"   MAE:  HR={mae_result['heart_rate']} BPM, 품질={mae_result['signal_quality']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ End-to-End 분석 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 실행"""
    logger.info("🚀 Phase 1 통합 테스트 시작")
    logger.info("=" * 50)
    
    test_results = []
    
    # 1. MediaPipe 통합 테스트
    test_results.append(("MediaPipe Face Mesh", test_mediapipe_integration()))
    
    # 2. MAE 모델 통합 테스트
    test_results.append(("MAE 모델", test_mae_model_integration()))
    
    # 3. rPPG 분석기 통합 테스트
    test_results.append(("rPPG 분석기", test_rppg_analyzer_integration()))
    
    # 4. End-to-End 분석 테스트
    test_results.append(("End-to-End 분석", test_end_to_end_analysis()))
    
    # 결과 요약
    logger.info("=" * 50)
    logger.info("📋 Phase 1 통합 테스트 결과 요약:")
    
    success_count = 0
    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"   {test_name}: {status}")
        if result:
            success_count += 1
    
    logger.info(f"📊 전체 테스트: {success_count}/{len(test_results)} 성공")
    
    if success_count == len(test_results):
        logger.info("🎉 Phase 1 통합 완료! 모든 테스트 통과")
        return True
    else:
        logger.warning(f"⚠️ Phase 1 통합 미완성: {len(test_results) - success_count}개 테스트 실패")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
