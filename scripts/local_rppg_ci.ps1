# RPPG 정확도 향상 로컬 CI/CD 스크립트 (PowerShell)
# 사용법: .\scripts\local_rppg_ci.ps1

Write-Host "🚀 RPPG 정확도 향상 CI/CD 시작..." -ForegroundColor Green

try {
    # 1. 백엔드 디렉토리로 이동
    Set-Location backend
    
    # 2. 의존성 설치
    Write-Host "📦 의존성 설치 중..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    # 3. RPPG 정확도 향상 훈련 실행
    Write-Host "🧠 RPPG 정확도 향상 훈련 시작..." -ForegroundColor Cyan
    python advanced_accuracy_training.py
    
    # 4. 정확도 테스트 실행
    Write-Host "🧪 정확도 테스트 실행..." -ForegroundColor Magenta
    python test_accuracy.py
    
    # 5. 결과 확인
    Write-Host "📊 결과 확인 중..." -ForegroundColor Yellow
    
    if (Test-Path "medical_grade_training_results.json") {
        Write-Host "✅ 의료급 정확도 훈련 결과 생성됨" -ForegroundColor Green
        $results = Get-Content "medical_accuracy_training_results.json" | ConvertFrom-Json
        Write-Host "정확도: $($results.accuracy)" -ForegroundColor White
    }
    
    if (Test-Path "accuracy_test_results.json") {
        Write-Host "✅ 정확도 테스트 결과 생성됨" -ForegroundColor Green
        $testResults = Get-Content "accuracy_test_results.json" | ConvertFrom-Json
        Write-Host "전체 정확도: $($testResults.overall_accuracy)" -ForegroundColor White
    }
    
    Write-Host "🎉 RPPG 정확도 향상 CI/CD 완료!" -ForegroundColor Green
    Write-Host "📁 결과 파일들:" -ForegroundColor Cyan
    Get-ChildItem *.json, *.png | ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor White }
    
} catch {
    Write-Host "❌ 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    # 원래 디렉토리로 복귀
    Set-Location ..
} 