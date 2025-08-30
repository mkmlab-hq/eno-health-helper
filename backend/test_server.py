from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Eno Health Helper Test Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 테스트용으로 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthQuery(BaseModel):
    query: str


@app.get("/")
async def root():
    return {"message": "Eno Health Helper Test Server is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "eno-health-helper-backend"}


@app.post("/analyze")
async def analyze_health(query: HealthQuery):
    """건강 분석 API (테스트용)"""
    return {
        "query": query.query,
        "analysis": "테스트 분석 결과입니다.",
        "confidence": 0.85,
        "recommendations": [
            "충분한 수면을 취하세요",
            "규칙적인 운동을 하세요",
            "균형 잡힌 식사를 하세요"
        ]
    }


@app.get("/test")
async def test_endpoint():
    """테스트용 엔드포인트"""
    return {
        "message": "백엔드 서버가 정상적으로 작동하고 있습니다!",
        "endpoints": [
            "/",
            "/health",
            "/analyze",
            "/test"
        ]
    }

if __name__ == "__main__":
    print("🚀 Eno Health Helper 테스트 서버 시작 중...")
    print("📍 서버 주소: http://localhost:8000")
    print("📋 API 문서: http://localhost:8000/docs")
    print("🔧 헬스체크: http://localhost:8000/health")
    print("🧪 테스트: http://localhost:8000/test")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
