#!/bin/bash

# MKM12 Eno Health Helper - CodeSpaces Setup Script

echo "🚀 MKM12 Eno Health Helper 개발 환경 설정을 시작합니다..."

# Python 가상환경 생성 및 활성화
echo "📦 Python 가상환경 설정 중..."
cd backend
python -m venv venv
source venv/bin/activate

# Python 의존성 설치
echo "📚 Python 의존성 설치 중..."
pip install -r requirements.txt

# MKM12 백엔드 서버 시작 (백그라운드)
echo "🔧 MKM12 백엔드 서버 시작 중..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 프론트엔드 의존성 설치
echo "🎨 프론트엔드 의존성 설치 중..."
cd ../frontend
npm install

# 프론트엔드 개발 서버 시작 (백그라운드)
echo "🌐 프론트엔드 개발 서버 시작 중..."
npm run dev &
FRONTEND_PID=$!

# 서버 상태 확인
echo "⏳ 서버 시작 대기 중..."
sleep 5

# 백엔드 서버 상태 확인
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MKM12 백엔드 서버가 성공적으로 시작되었습니다 (포트 8000)"
else
    echo "❌ MKM12 백엔드 서버 시작 실패"
fi

# 프론트엔드 서버 상태 확인
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 프론트엔드 개발 서버가 성공적으로 시작되었습니다 (포트 3000)"
else
    echo "❌ 프론트엔드 개발 서버 시작 실패"
fi

echo ""
echo "🎉 MKM12 Eno Health Helper 개발 환경이 준비되었습니다!"
echo ""
echo "📱 프론트엔드: http://localhost:3000"
echo "🔧 백엔드 API: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""
echo "💡 개발을 시작하세요!"
echo "   - 프론트엔드 코드는 frontend/ 디렉토리에서 수정"
echo "   - 백엔드 코드는 backend/ 디렉토리에서 수정"
echo "   - 서버는 자동으로 재시작됩니다"

# 프로세스 ID 저장 (나중에 정리용)
echo $BACKEND_PID > /tmp/backend.pid
echo $FRONTEND_PID > /tmp/frontend.pid

# 대기
wait
