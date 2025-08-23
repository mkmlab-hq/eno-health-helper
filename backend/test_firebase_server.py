"""
Firebase 연결 테스트 서버
간단한 FastAPI 서버로 Firebase 연결 상태 확인
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(title="Firebase 연결 테스트 서버", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    logger.info("✅ Firebase 연결 성공")
    firebase_connected = True
    
except Exception as e:
    logger.error(f"❌ Firebase 연결 실패: {e}")
    db = None
    firebase_connected = False

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Firebase 연결 테스트 서버",
        "status": "running",
        "firebase_connected": firebase_connected,
        "version": "1.0.0"
    }

@app.get("/test")
async def test_firebase():
    """Firebase 연결 테스트"""
    if not firebase_connected:
        return {"error": "Firebase 연결 실패"}
    
    try:
        # 간단한 Firestore 테스트
        test_doc = db.collection('test').document('connection_test')
        test_doc.set({
            'message': 'Firebase 연결 테스트 성공',
            'timestamp': '2025-01-22'
        })
        
        return {
            "success": True,
            "message": "Firebase 연결 및 쓰기 테스트 성공",
            "firebase_status": "connected"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "firebase_status": "error"
        }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "firebase": "connected" if firebase_connected else "disconnected",
        "timestamp": "2025-01-22"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Firebase 테스트 서버 시작 중...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 