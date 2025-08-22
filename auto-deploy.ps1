# 엔오건강도우미 자동 배포 스크립트

Write-Host "🚀 엔오건강도우미 자동 배포 시작!" -ForegroundColor Green

# 1. 현재 상태 확인
Write-Host "📁 현재 디렉토리: $(Get-Location)" -ForegroundColor Yellow

# 2. deploy-ready 폴더 확인
if (Test-Path "deploy-ready") {
    Write-Host "✅ deploy-ready 폴더 발견" -ForegroundColor Green
} else {
    Write-Host "❌ deploy-ready 폴더가 없습니다" -ForegroundColor Red
    exit 1
}

# 3. 파일 목록 확인
Write-Host "📋 배포할 파일들:" -ForegroundColor Yellow
Get-ChildItem "deploy-ready" -Recurse | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}

# 4. 자동 배포 옵션 제공
Write-Host ""
Write-Host "🎯 자동 배포 옵션:" -ForegroundColor Magenta
Write-Host "1. GitHub Pages (GitHub 저장소 필요)" -ForegroundColor White
Write-Host "2. Netlify (웹 브라우저에서 드래그 앤 드롭)" -ForegroundColor White
Write-Host "3. Vercel (GitHub 저장소 필요)" -ForegroundColor White

# 5. GitHub 저장소 확인
Write-Host ""
Write-Host "🔍 GitHub 저장소 확인 중..." -ForegroundColor Yellow

try {
    $gitRemote = git remote get-url origin 2>$null
    if ($gitRemote) {
        Write-Host "✅ GitHub 저장소 발견: $gitRemote" -ForegroundColor Green
        Write-Host "🚀 GitHub Pages 자동 배포 가능!" -ForegroundColor Green
        
        # GitHub Pages 배포를 위한 설정
        Write-Host "📝 GitHub Pages 설정 중..." -ForegroundColor Yellow
        
        # deploy-ready 폴더를 루트로 이동
        Copy-Item "deploy-ready/*" -Destination "." -Recurse -Force
        Write-Host "✅ 배포 파일을 루트로 이동 완료" -ForegroundColor Green
        
        # .nojekyll 파일 생성 (GitHub Pages 호환성)
        "" | Out-File -FilePath ".nojekyll" -Encoding UTF8
        Write-Host "✅ .nojekyll 파일 생성 완료" -ForegroundColor Green
        
        # Git 커밋 및 푸시
        Write-Host "📝 Git 커밋 중..." -ForegroundColor Yellow
        git add .
        git commit -m "🚀 엔오건강도우미 PWA 자동 배포" 2>$null
        
        Write-Host "📤 Git 푸시 중..." -ForegroundColor Yellow
        git push origin main 2>$null
        
        Write-Host "🎉 GitHub Pages 자동 배포 완료!" -ForegroundColor Green
        Write-Host "📱 잠시 후 GitHub Pages에서 확인 가능합니다" -ForegroundColor Cyan
        
    } else {
        Write-Host "❌ GitHub 저장소가 설정되지 않았습니다" -ForegroundColor Red
        Write-Host "💡 GitHub 저장소를 먼저 설정하거나 Netlify를 사용하세요" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Git 명령어 실행 실패: $_" -ForegroundColor Red
}

# 6. Netlify 배포 안내
Write-Host ""
Write-Host "🌐 Netlify 배포 방법:" -ForegroundColor Magenta
Write-Host "1. [Netlify](https://netlify.com) 접속" -ForegroundColor White
Write-Host "2. deploy-ready 폴더를 Netlify에 드래그 앤 드롭" -ForegroundColor White
Write-Host "3. 자동으로 배포 완료!" -ForegroundColor White

# 7. 로컬 테스트 서버 시작
Write-Host ""
Write-Host "🌐 로컬 테스트 서버 시작..." -ForegroundColor Yellow
Write-Host "📱 브라우저에서 http://localhost:8000 접속하여 PWA 테스트" -ForegroundColor Cyan

try {
    Set-Location "deploy-ready"
    Write-Host "🚀 Python HTTP 서버 시작 (포트 8000)..." -ForegroundColor Green
    Write-Host "⏹️  중지하려면 Ctrl+C" -ForegroundColor Red
    Write-Host "📱 브라우저에서 http://localhost:8000 접속" -ForegroundColor Cyan
    python -m http.server 8000
} catch {
    Write-Host "❌ Python 서버 시작 실패: $_" -ForegroundColor Red
    Write-Host "💡 Python이 설치되어 있는지 확인하세요" -ForegroundColor Yellow
} 