# 엔오건강도우미 간단 배포 스크립트
# PowerShell용

Write-Host "🚀 엔오건강도우미 PWA 배포 시작!" -ForegroundColor Green
Write-Host "✨ 디자인 철학: '따뜻한 기술, 직관적인 건강'" -ForegroundColor Cyan

# 1. 프로젝트 디렉토리로 이동
Set-Location $PSScriptRoot
Write-Host "📁 프로젝트 디렉토리: $(Get-Location)" -ForegroundColor Yellow

# 2. PWA 아이콘 확인
Write-Host "🔍 PWA 아이콘 확인 중..." -ForegroundColor Yellow
$iconCount = (Get-ChildItem "frontend/public/icons/*.png" | Measure-Object).Count
Write-Host "✅ PWA 아이콘: $iconCount개 발견" -ForegroundColor Green

# 3. 정적 파일 배포 준비
Write-Host "📦 정적 파일 배포 준비 중..." -ForegroundColor Yellow

# 간단한 정적 배포를 위한 파일 복사
$deployDir = "deploy-static"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# 필요한 파일들 복사
Copy-Item "frontend/public/*" -Destination $deployDir -Recurse -Force
Copy-Item "frontend/public/icons" -Destination $deployDir -Recurse -Force

Write-Host "✅ 정적 파일 준비 완료: $deployDir" -ForegroundColor Green

# 4. 배포 옵션 안내
Write-Host ""
Write-Host "🎯 배포 옵션:" -ForegroundColor Magenta
Write-Host "1. GitHub Pages: $deployDir 폴더를 GitHub 저장소에 push" -ForegroundColor White
Write-Host "2. Netlify: $deployDir 폴더를 Netlify에 드래그 앤 드롭" -ForegroundColor White
Write-Host "3. Vercel: vercel --prod 명령어 실행" -ForegroundColor White
Write-Host "4. Firebase: firebase deploy 명령어 실행" -ForegroundColor White

# 5. 로컬 테스트 서버 시작
Write-Host ""
Write-Host "🌐 로컬 테스트 서버 시작..." -ForegroundColor Yellow
Write-Host "📱 브라우저에서 http://localhost:8000 접속하여 PWA 테스트" -ForegroundColor Cyan

# Python 간단 서버 시작
try {
    Set-Location $deployDir
    Write-Host "🚀 Python HTTP 서버 시작 (포트 8000)..." -ForegroundColor Green
    Write-Host "⏹️  중지하려면 Ctrl+C" -ForegroundColor Red
    python -m http.server 8000
} catch {
    Write-Host "❌ Python 서버 시작 실패: $_" -ForegroundColor Red
    Write-Host "💡 Python이 설치되어 있는지 확인하세요" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 엔오건강도우미 PWA 배포 준비 완료!" -ForegroundColor Green
Write-Host "📱 친구들에게 보여줄 준비가 되었습니다!" -ForegroundColor Cyan 