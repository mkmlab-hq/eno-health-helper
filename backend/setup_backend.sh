#!/bin/bash
# 백엔드 환경 설정 스크립트

echo "🚀 ENO Health Helper 백엔드 환경 설정 시작"

# Python 가상환경 생성
echo "📦 Python 가상환경 생성 중..."
python3 -m venv venv

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "⬆️ pip 업그레이드 중..."
pip install --upgrade pip

# 의존성 설치
echo "📚 의존성 설치 중..."
pip install -r requirements.txt

echo "✅ 백엔드 환경 설정 완료!"
echo "💡 다음 명령어로 서버를 실행하세요:"
echo "   source venv/bin/activate"
echo "   python main.py"
