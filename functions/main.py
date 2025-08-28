import functions_framework
from flask import Flask, request, jsonify
from datetime import datetime
import logging
import os
import google.generativeai as genai

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__)

# Gemini API 설정
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        GEMINI_AVAILABLE = True
        logger.info("✅ Gemini API 초기화 완료")
    else:
        GEMINI_AVAILABLE = False
        logger.warning("⚠️ GOOGLE_API_KEY 환경 변수가 설정되지 않음")
except Exception as e:
    GEMINI_AVAILABLE = False
    logger.error(f"❌ Gemini API 초기화 실패: {e}")

# 실제 분석 엔진들 import
try:
    import sys
    import os
    
    # 현재 디렉토리를 Python path에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 실제 분석 엔진들 import
    from enhanced_rppg_analyzer import EnhancedRPPGAnalyzer
    from voice_analyzer import VoiceAnalyzer
    from fusion_analyzer import AdvancedFusionAnalyzer
    
    # 분석 엔진 초기화
    rppg_analyzer = EnhancedRPPGAnalyzer()
    voice_analyzer = VoiceAnalyzer()
    fusion_analyzer = AdvancedFusionAnalyzer()
    
    ANALYZERS_READY = True
    logger.info("✅ 실제 분석 엔진들 초기화 완료")
    
except ImportError as e:
    ANALYZERS_READY = False
    logger.warning(f"⚠️ 실제 분석 엔진 import 실패: {e}")
    logger.info("시뮬레이션 모드로 동작합니다")

@functions_framework.http
def root(request):
    """Google Cloud Functions HTTP 트리거 엔드포인트"""
    # URL 경로에 따라 적절한 함수 호출
    path = request.path
    method = request.method
    
    if path == '/' or path == '':
        return jsonify({
            "message": "MKM Lab eno-health-helper API",
            "version": "1.0.0",
            "status": "running",
            "analyzers_ready": ANALYZERS_READY,
            "gemini_available": GEMINI_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        })
    elif path == '/health':
        return health_check()
    elif path == '/api/analyze/fusion' and method == 'POST':
        return analyze_fusion()
    elif path == '/api/analyze/rppg' and method == 'POST':
        return analyze_rppg()
    elif path == '/api/analyze/voice' and method == 'POST':
        return analyze_voice()
    elif path == '/api/analyze/health' and method == 'POST':
        return analyze_health()
    elif path == '/api/ai-chat' and method == 'POST':
        return ai_chat()
    elif path == '/api/healing-music' and method == 'POST':
        return healing_music()
    else:
        return jsonify({"error": "Endpoint not found"}), 404

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "services": {
            "fusion_analyzer": "ready" if ANALYZERS_READY else "simulation",
            "rppg_analyzer": "ready" if ANALYZERS_READY else "simulation", 
            "voice_analyzer": "ready" if ANALYZERS_READY else "simulation",
            "health_analyzer": "ready" if ANALYZERS_READY else "simulation",
            "gemini_ai": "ready" if GEMINI_AVAILABLE else "unavailable",
            "healing_music": "ready"
        },
        "analyzers_ready": ANALYZERS_READY,
        "gemini_available": GEMINI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/healing-music', methods=['POST'])
def healing_music():
    """치유 음악 추천 및 AI 음악 생성 API"""
    try:
        data = request.get_json()
        health_data = data.get('healthData', {})
        request_type = data.get('requestType', 'recommendations')
        
        # 사용 횟수 제한 확인 (일일 3회)
        if request_type == 'recommendations':
            # 사용자별 사용 횟수 확인 로직
            # 실제 구현에서는 Firestore에서 사용 횟수를 확인해야 함
            # 현재는 간단한 시뮬레이션으로 처리
            # TODO: 실제 Firestore 연동 시 아래 로직을 구현
            # from firebase_admin import firestore
            # db = firestore.client()
            # usage_ref = db.collection('music_usage').document(user_id)
            # usage_doc = usage_ref.get()
            # if usage_doc.exists:
            #     usage_data = usage_doc.to_dict()
            #     daily_count = usage_data.get('dailyCount', 0)
            #     if daily_count >= daily_limit:
            #         return jsonify({
            #             "success": False,
            #             "error": "일일 사용량 제한에 도달했습니다",
            #             "daily_limit": daily_limit,
            #             "daily_count": daily_count,
            #             "remaining": 0
            #         }), 429
            
            return generate_music_recommendations(health_data)
        elif request_type == 'generate':
            return generate_ai_music(health_data)
        else:
            return jsonify({
                "success": False,
                "error": "지원하지 않는 요청 타입입니다"
            }), 400
            
    except Exception as e:
        logger.error(f"치유 음악 API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def generate_music_recommendations(health_data):
    """건강 데이터 기반 음악 추천 생성"""
    try:
        recommendations = []
        
        # 스트레스 지수 기반 추천
        if health_data.get('rppg', {}).get('stressIndex'):
            stress_level = health_data['rppg']['stressIndex']
            
            if stress_level > 0.7:
                recommendations.append({
                    "id": "stress-relief-high",
                    "title": "고요한 숲속 명상",
                    "artist": "Nature Sounds",
                    "genre": "명상/자연음",
                    "mood": "차분함",
                    "frequency": "432Hz (치유 주파수)",
                    "duration": "15분",
                    "description": "스트레스 해소를 위한 자연의 소리와 치유 주파수",
                    "healthBenefit": "스트레스 감소, 심신 안정",
                    "reason": f"현재 스트레스 지수가 {(stress_level * 100):.1f}%로 높아 안정적인 음악이 필요합니다.",
                    "isGenerated": False
                })
            elif stress_level > 0.4:
                recommendations.append({
                    "id": "stress-relief-medium",
                    "title": "부드러운 클래식 모음",
                    "artist": "Classical Collection",
                    "genre": "클래식",
                    "mood": "평온함",
                    "frequency": "528Hz (사랑의 주파수)",
                    "duration": "20분",
                    "description": "모차르트와 바흐의 평온한 선율",
                    "healthBenefit": "심박수 안정화, 집중력 향상",
                    "reason": f"적당한 스트레스 수준({(stress_level * 100):.1f}%)으로 부드러운 클래식이 적합합니다.",
                    "isGenerated": False
                })
            else:
                recommendations.append({
                    "id": "stress-relief-low",
                    "title": "활기찬 모닝 음악",
                    "artist": "Morning Vibes",
                    "genre": "팝/일렉트로닉",
                    "mood": "활기찬",
                    "frequency": "639Hz (관계의 주파수)",
                    "duration": "25분",
                    "description": "상쾌한 아침을 위한 경쾌한 비트",
                    "healthBenefit": "에너지 증진, 기분 전환",
                    "reason": f"낮은 스트레스 수준({(stress_level * 100):.1f}%)으로 활기찬 음악이 적합합니다.",
                    "isGenerated": False
                })
        
        # 체질 기반 추천
        if health_data.get('fusion', {}).get('digitalTemperament'):
            temperament = health_data['fusion']['digitalTemperament']
            
            if temperament == '태양인':
                recommendations.append({
                    "id": "temperament-sun",
                    "title": "태양인 맞춤 치유음",
                    "artist": "AI Generated",
                    "genre": "치유음악",
                    "mood": "활기찬",
                    "frequency": "639Hz (관계의 주파수)",
                    "duration": "25분",
                    "description": "태양인의 특성을 고려한 맞춤형 치유 음악",
                    "healthBenefit": "에너지 균형, 활력 증진",
                    "reason": "태양인 체질에 맞는 활기찬 치유 음악입니다.",
                    "isGenerated": True
                })
            elif temperament == '태음인':
                recommendations.append({
                    "id": "temperament-moon",
                    "title": "태음인 맞춤 치유음",
                    "artist": "AI Generated",
                    "genre": "치유음악",
                    "mood": "차분함",
                    "frequency": "741Hz (깨달음의 주파수)",
                    "duration": "30분",
                    "description": "태음인의 특성을 고려한 맞춤형 치유 음악",
                    "healthBenefit": "내면의 평화, 깊은 휴식",
                    "reason": "태음인 체질에 맞는 차분한 치유 음악입니다.",
                    "isGenerated": True
                })
            elif temperament == '소양인':
                recommendations.append({
                    "id": "temperament-small-sun",
                    "title": "소양인 맞춤 치유음",
                    "artist": "AI Generated",
                    "genre": "치유음악",
                    "mood": "균형감",
                    "frequency": "528Hz (사랑의 주파수)",
                    "duration": "22분",
                    "description": "소양인의 특성을 고려한 맞춤형 치유 음악",
                    "healthBenefit": "에너지 균형, 안정감",
                    "reason": "소양인 체질에 맞는 균형잡힌 치유 음악입니다.",
                    "isGenerated": True
                })
            elif temperament == '소음인':
                recommendations.append({
                    "id": "temperament-small-moon",
                    "title": "소음인 맞춤 치유음",
                    "artist": "AI Generated",
                    "genre": "치유음악",
                    "mood": "차분함",
                    "frequency": "396Hz (해방의 주파수)",
                    "duration": "28분",
                    "description": "소음인의 특성을 고려한 맞춤형 치유 음악",
                    "healthBenefit": "내면의 평화, 스트레스 해소",
                    "reason": "소음인 체질에 맞는 차분한 치유 음악입니다.",
                    "isGenerated": True
                })
        
        # 음성 감정 기반 추천
        if health_data.get('voice', {}).get('emotion'):
            emotion = health_data['voice']['emotion']
            
            if emotion in ['긴장', '불안', '스트레스']:
                recommendations.append({
                    "id": "emotion-calm",
                    "title": "긴장 해소 음악",
                    "artist": "Healing Sounds",
                    "genre": "치유음악",
                    "mood": "안정감",
                    "frequency": "396Hz (해방의 주파수)",
                    "duration": "18분",
                    "description": "긴장과 불안을 해소하는 부드러운 선율",
                    "healthBenefit": "긴장 해소, 마음의 평화",
                    "reason": f"음성 분석 결과 '{emotion}' 상태로 안정적인 음악이 필요합니다.",
                    "isGenerated": False
                })
            elif emotion in ['우울', '슬픔']:
                recommendations.append({
                    "id": "emotion-joy",
                    "title": "기분 전환 음악",
                    "artist": "Joyful Tunes",
                    "genre": "팝/록",
                    "mood": "활기찬",
                    "frequency": "639Hz (관계의 주파수)",
                    "duration": "20분",
                    "description": "우울한 기분을 밝게 전환하는 경쾌한 음악",
                    "healthBenefit": "기분 전환, 에너지 증진",
                    "reason": f"음성 분석 결과 '{emotion}' 상태로 활기찬 음악이 필요합니다.",
                    "isGenerated": False
                })
        
        # AI 기반 추가 추천 (Gemini API 활용)
        if GEMINI_AVAILABLE and health_data:
            try:
                ai_recommendations = generate_ai_music_recommendations(health_data)
                recommendations.extend(ai_recommendations)
            except Exception as e:
                logger.warning(f"AI 음악 추천 생성 실패: {e}")
        
        logger.info(f"✅ 음악 추천 생성 완료: {len(recommendations)}개")
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"음악 추천 생성 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def generate_ai_music_recommendations(health_data):
    """Gemini API를 활용한 AI 음악 추천"""
    try:
        # 건강 데이터 요약
        health_summary = ""
        if health_data.get('rppg'):
            rppg = health_data['rppg']
            health_summary += f"심혈관: 심박수 {rppg.get('heartRate', 'N/A')} BPM, 스트레스 {(rppg.get('stressIndex', 0) * 100):.1f}%\n"
        
        if health_data.get('voice'):
            voice = health_data['voice']
            health_summary += f"음성: 감정 {voice.get('emotion', 'N/A')}, 명확도 {(voice.get('clarity', 0) * 100):.1f}%\n"
        
        if health_data.get('fusion'):
            fusion = health_data['fusion']
            health_summary += f"체질: {fusion.get('digitalTemperament', 'N/A')}, 점수 {fusion.get('overallScore', 'N/A')}/100\n"
        
        # Gemini 프롬프트
        prompt = f"""당신은 음악 치료사이자 건강 음악 전문가입니다. 다음 건강 정보를 바탕으로 맞춤형 음악을 추천해주세요.

사용자 건강 정보:
{health_summary}

요구사항:
1. 건강 상태에 맞는 음악 장르와 분위기 추천
2. 치유 주파수(432Hz, 528Hz, 639Hz, 741Hz, 396Hz) 중 적합한 것 선택
3. 구체적인 음악 제목과 아티스트 추천
4. 건강 효과와 추천 이유를 명확하게 설명
5. 한국어로 답변

추천 형식:
- 제목: [음악 제목]
- 아티스트: [아티스트명]
- 장르: [음악 장르]
- 분위기: [음악 분위기]
- 주파수: [치유 주파수]
- 건강 효과: [구체적인 건강 효과]
- 추천 이유: [건강 데이터 기반 추천 이유]

3개의 음악을 추천해주세요."""

        # Gemini API 호출
        response = gemini_model.generate_content(prompt)
        ai_response = response.text
        
        # AI 응답을 구조화된 데이터로 변환 (간단한 파싱)
        ai_recommendations = []
        try:
            # AI 응답에서 음악 정보 추출하여 구조화
            # 실제 구현에서는 더 정교한 파싱 로직 필요
            ai_recommendations.append({
                "id": "ai-recommendation-1",
                "title": "AI 맞춤 추천 음악",
                "artist": "AI Generated",
                "genre": "치유음악",
                "mood": "맞춤형",
                "frequency": "432Hz (치유 주파수)",
                "duration": "25분",
                "description": "AI가 분석한 맞춤형 치유 음악",
                "healthBenefit": "개인 맞춤 건강 효과",
                "reason": "AI가 건강 데이터를 분석하여 추천한 맞춤 음악입니다.",
                "isGenerated": True,
                "aiAnalysis": ai_response[:200] + "..."  # AI 분석 결과 일부 포함
            })
        except:
            pass
        
        return ai_recommendations
        
    except Exception as e:
        logger.error(f"AI 음악 추천 생성 오류: {e}")
        return []

def generate_ai_music(health_data):
    """AI를 활용한 실제 음악 생성 (Suno AI 연동 예정)"""
    try:
        # 현재는 Suno AI 연동 전 단계로 기본 응답
        return jsonify({
            "success": True,
            "message": "AI 음악 생성 기능은 현재 개발 중입니다. Suno AI 연동 후 실제 음악을 생성할 수 있습니다.",
            "status": "development",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI 음악 생성 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """AI 채팅 API - Gemini를 통한 건강 상담"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        health_data = data.get('healthData', {})
        question_count = data.get('questionCount', 1)
        
        if not question:
            return jsonify({
                "success": False,
                "error": "질문이 제공되지 않았습니다"
            }), 400
        
        if not GEMINI_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "AI 서비스가 현재 사용할 수 없습니다"
            }), 503
        
        # 건강 데이터 요약
        health_summary = ""
        if health_data.get('rppg'):
            rppg = health_data['rppg']
            health_summary += f"심혈관 건강: 심박수 {rppg.get('heartRate', 'N/A')} BPM, 스트레스 지수 {(rppg.get('stressIndex', 0) * 100):.1f}%\n"
        
        if health_data.get('voice'):
            voice = health_data['voice']
            health_summary += f"음성 건강: 피치 {voice.get('pitch', 'N/A')} Hz, 명확도 {(voice.get('clarity', 0) * 100):.1f}%\n"
        
        if health_data.get('fusion'):
            fusion = health_data['fusion']
            health_summary += f"체질 분석: {fusion.get('digitalTemperament', 'N/A')}, 종합 점수 {fusion.get('overallScore', 'N/A')}/100\n"
        
        # Gemini 프롬프트 구성
        prompt = f"""당신은 한의학 사상체질 전문가이자 건강 상담사입니다. 다음 정보를 바탕으로 사용자의 질문에 답변해주세요.

사용자 건강 정보:
{health_summary}

사용자 질문: "{question}"

요구사항:
1. 한의학 사상체질 관점에서 답변
2. 사용자의 현재 건강 상태를 고려한 맞춤 조언
3. 구체적이고 실용적인 제안
4. 친근하고 이해하기 쉬운 한국어
5. 이모지 적절히 사용하여 가독성 향상
6. 질문 횟수 {question_count}회를 고려하여 점진적으로 깊이 있는 답변 제공

답변:"""

        # Gemini API 호출
        response = gemini_model.generate_content(prompt)
        ai_response = response.text
        
        logger.info(f"✅ AI 채팅 응답 생성 완료: 질문 {question_count}회")
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "question_count": question_count,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI 채팅 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/analyze/fusion', methods=['POST'])
def analyze_fusion():
    """rPPG-음성 융합 분석 (실제 또는 모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"융합 분석 요청: {user_id}")
        
        if ANALYZERS_READY:
            try:
                # 실제 융합 분석 수행
                rppg_data = data.get('rppg_data', {})
                voice_data = data.get('voice_data', {})
                
                import asyncio
                fusion_result = asyncio.run(fusion_analyzer.analyze_fusion(
                    rppg_data=rppg_data,
                    voice_data=voice_data
                ))
                
                logger.info(f"✅ 실제 융합 분석 완료: {fusion_result.get('digital_temperament', 'N/A')}")
                return jsonify({
                    "success": True,
                    "data": fusion_result,
                    "timestamp": datetime.now().isoformat(),
                    "analysis_type": "fusion",
                    "mode": "real"
                })
                
            except Exception as e:
                logger.error(f"실제 융합 분석 실패: {e}")
                logger.info("시뮬레이션 모드로 fallback")
        
        # 시뮬레이션 모드 (fallback)
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
            "analysis_type": "fusion",
            "mode": "simulation"
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
    """rPPG 분석 (실제 또는 모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"rPPG 분석 요청: {user_id}")
        
        if ANALYZERS_READY:
            try:
                # 실제 rPPG 분석 수행
                video_data = data.get('video_data', {})
                frames = video_data.get('frames', [])
                
                if frames:
                    rppg_result = rppg_analyzer.analyze_video_frames(frames, user_id)
                    
                    logger.info(f"✅ 실제 rPPG 분석 완료: HR={rppg_result.get('heart_rate', 'N/A')} BPM")
                    return jsonify({
                        "success": True,
                        "data": rppg_result,
                        "timestamp": datetime.now().isoformat(),
                        "analysis_type": "rppg",
                        "mode": "real"
                    })
                else:
                    logger.warning("비디오 프레임 데이터가 없습니다")
            except Exception as e:
                logger.error(f"실제 rPPG 분석 실패: {e}")
                logger.info("시뮬레이션 모드로 fallback")
        
        # 시뮬레이션 모드 (fallback)
        result = {
            "user_id": user_id,
            "analysis_type": "rppg",
            "heart_rate": 72,
            "hrv": 45.2,
            "stress_level": "보통",
            "confidence": 0.85,
            "quality_score": 78.5
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "rppg",
            "mode": "simulation"
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
    """음성 분석 (실제 또는 모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"음성 분석 요청: {user_id}")
        
        if ANALYZERS_READY:
            try:
                # 실제 음성 분석 수행
                audio_data = data.get('audio_data', {})
                audio_bytes = audio_data.get('audio_bytes', b'')
                
                if audio_bytes:
                    try:
                        import base64
                        audio_decoded = base64.b64decode(audio_bytes)
                        import asyncio
                        voice_result = asyncio.run(voice_analyzer.analyze_voice(audio_decoded))
                        
                        logger.info(f"✅ 실제 음성 분석 완료: F0={voice_result.get('f0', 'N/A')} Hz")
                        return jsonify({
                            "success": True,
                            "data": voice_result,
                            "timestamp": datetime.now().isoformat(),
                            "analysis_type": "voice",
                            "mode": "real"
                        })
                    except Exception as e:
                        logger.error(f"오디오 데이터 디코딩 실패: {e}")
                else:
                    logger.warning("오디오 데이터가 없습니다")
            except Exception as e:
                logger.error(f"실제 음성 분석 실패: {e}")
                logger.info("시뮬레이션 모드로 fallback")
        
        # 시뮬레이션 모드 (fallback)
        result = {
            "user_id": user_id,
            "analysis_type": "voice",
            "f0": 120.5,
            "jitter": 0.3,
            "shimmer": 0.4,
            "hnr": 15.2,
            "voice_quality": "좋음",
            "confidence": 0.82
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "voice",
            "mode": "simulation"
        })
        
    except Exception as e:
        logger.error(f"음성 분석 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "voice"
        }), 500

@app.route('/api/analyze/health', methods=['POST'])
def analyze_health():
    """종합 건강 분석 (모의)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'unknown')
        
        logger.info(f"종합 건강 분석 요청: {user_id}")
        
        # 모의 종합 건강 분석 결과
        result = {
            "user_id": user_id,
            "overall_health_score": 78.5,
            "risk_factors": ["stress", "sedentary_lifestyle"],
            "recommendations": [
                "규칙적인 운동을 권장합니다",
                "스트레스 관리를 위해 명상이나 요가를 시도해보세요",
                "충분한 수면을 취하세요"
            ],
            "next_checkup": "3개월 후"
        }
        
        return jsonify({
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "health"
        })
        
    except Exception as e:
        logger.error(f"종합 건강 분석 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "health"
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
            "health_analyzer": "active",
            "gemini_ai": "active" if GEMINI_AVAILABLE else "inactive",
            "healing_music": "active"
        },
        "analyzers_ready": ANALYZERS_READY,
        "gemini_available": GEMINI_AVAILABLE,
        "uptime": "running",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    # 로컬 테스트용
    app.run(host='0.0.0.0', port=8000, debug=True)
