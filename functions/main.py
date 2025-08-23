import functions_framework
from flask import Flask, request, jsonify
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__)

@app.route('/')
def root():
    """루트 엔드포인트"""
    return jsonify({
        "message": "MKM Lab eno-health-helper API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "services": {
            "fusion_analyzer": "ready",
            "rppg_analyzer": "ready", 
            "voice_analyzer": "ready",
            "health_analyzer": "ready"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze/fusion', methods=['POST'])
def analyze_fusion():
    """rPPG-음성 융합 분석 (모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"융합 분석 요청: {user_id}")
        
        # 모의 융합 분석 결과
        result = {
            "user_id": user_id,
            "analysis_type": "fusion",
            "rppg_score": 85.5,
            "voice_score": 78.2,
            "fusion_score": 82.1,
            "digital_temperament": "태양인",
            "confidence": 0.89,
            "recommendations": [
                "현재 스트레스 수준이 높습니다",
                "충분한 휴식이 필요합니다",
                "규칙적인 운동을 권장합니다"
            ]
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "fusion"
        })
        
    except Exception as e:
        logger.error(f"융합 분석 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "fusion"
        }), 500

@app.route('/api/analyze/rppg', methods=['POST'])
def analyze_rppg():
    """rPPG 분석 (모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"rPPG 분석 요청: {user_id}")
        
        # 모의 rPPG 분석 결과
        result = {
            "user_id": user_id,
            "heart_rate": 72,
            "hrv": 45.2,
            "stress_level": "medium",
            "signal_quality": 0.87,
            "blood_pressure_estimate": "120/80"
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "rppg"
        })
        
    except Exception as e:
        logger.error(f"rPPG 분석 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "rppg"
        }), 500

@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """음성 분석 (모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"음성 분석 요청: {user_id}")
        
        # 모의 음성 분석 결과
        result = {
            "user_id": user_id,
            "jitter": 0.45,
            "shimmer": 0.32,
            "hnr": 18.5,
            "voice_quality": "good",
            "fatigue_level": "low"
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "voice"
        })
        
    except Exception as e:
        logger.error(f"음성 분석 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "voice"
        }), 500

@app.route('/api/status')
def get_status():
    """시스템 상태 및 메트릭"""
    return jsonify({
        "status": "operational",
        "services": {
            "fusion_analyzer": "active",
            "rppg_analyzer": "active",
            "voice_analyzer": "active", 
            "health_analyzer": "active"
        },
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    })

# Firebase Functions 핸들러
@functions_framework.http
def eno_health_api(request):
    """Firebase Functions HTTP 트리거"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == "__main__":
    # 로컬 테스트용
    app.run(host='0.0.0.0', port=8000, debug=True)