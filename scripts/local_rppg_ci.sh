#!/bin/bash

# RPPG 정확도 향상 로컬 CI/CD 스크립트
# 사용법: ./scripts/local_rppg_ci.sh

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 RPPG 정확도 향상 CI/CD 시작..."

# 1. 백엔드 디렉토리로 이동
cd backend

# 2. 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 3. RPPG 정확도 향상 훈련 실행
echo "🧠 RPPG 정확도 향상 훈련 시작..."
python advanced_accuracy_training.py

# 4. 정확도 테스트 실행
echo "🧪 정확도 테스트 실행..."
python test_accuracy.py

# 5. 결과 확인
echo "📊 결과 확인 중..."
if [ -f "medical_grade_training_results.json" ]; then
    echo "✅ 의료급 정확도 훈련 결과 생성됨"
    cat medical_grade_training_results.json | jq '.accuracy' 2>/dev/null || echo "결과 파일 확인됨"
fi

if [ -f "accuracy_test_results.json" ]; then
    echo "✅ 정확도 테스트 결과 생성됨"
    cat accuracy_test_results.json | jq '.overall_accuracy' 2>/dev/null || echo "결과 파일 확인됨"
fi

echo "🎉 RPPG 정확도 향상 CI/CD 완료!"
echo "📁 결과 파일들:"
ls -la *.json *.png 2>/dev/null || echo "결과 파일이 없습니다" 