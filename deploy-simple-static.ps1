# 엔오건강도우미 간단 정적 배포 스크립트
# GitHub Pages, Netlify 등에 바로 업로드 가능

Write-Host "🚀 엔오건강도우미 간단 정적 배포 준비!" -ForegroundColor Green
Write-Host "✨ 디자인 철학: '따뜻한 기술, 직관적인 건강'" -ForegroundColor Cyan

# 1. 프로젝트 디렉토리로 이동
Set-Location $PSScriptRoot
Write-Host "📁 프로젝트 디렉토리: $(Get-Location)" -ForegroundColor Yellow

# 2. PWA 아이콘 확인
Write-Host "🔍 PWA 아이콘 확인 중..." -ForegroundColor Yellow
$iconCount = (Get-ChildItem "frontend/public/icons/*.png" | Measure-Object).Count
Write-Host "✅ PWA 아이콘: $iconCount개 발견" -ForegroundColor Green

# 3. 정적 배포용 폴더 생성
Write-Host "📦 정적 배포용 폴더 생성 중..." -ForegroundColor Yellow

$deployDir = "deploy-ready"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# 4. 필요한 파일들 복사
Write-Host "📋 파일 복사 중..." -ForegroundColor Yellow

# HTML 파일 복사
Copy-Item "frontend/public/index.html" -Destination "$deployDir/index.html" -Force
Write-Host "✅ index.html 복사 완료" -ForegroundColor Green

# PWA 매니페스트 복사
Copy-Item "frontend/public/manifest.json" -Destination "$deployDir/manifest.json" -Force
Write-Host "✅ manifest.json 복사 완료" -ForegroundColor Green

# PWA 아이콘들 복사
Copy-Item "frontend/public/icons" -Destination "$deployDir/icons" -Recurse -Force
Write-Host "✅ PWA 아이콘 복사 완료" -ForegroundColor Green

# 5. 배포 가이드 생성
Write-Host "📖 배포 가이드 생성 중..." -ForegroundColor Yellow

$deployGuide = @"
# 🚀 엔오건강도우미 PWA 배포 가이드

## 📱 **친구 보여주기용 PWA 완성!**

우리의 **"따뜻한 기술, 직관적인 건강"** 디자인 철학이 완벽하게 구현된 PWA가 준비되었습니다!

## 🎯 **즉시 배포 방법**

### **방법 1: Netlify (가장 간단 - 2분)**
1. [Netlify](https://netlify.com) 접속
2. deploy-ready 폴더를 Netlify에 드래그 앤 드롭
3. 자동으로 배포 완료!

### **방법 2: GitHub Pages (5분)**
1. GitHub에 새 저장소 생성
2. deploy-ready 폴더의 모든 파일을 저장소에 업로드
3. Settings → Pages → Source를 'main'으로 설정
4. 자동으로 배포 완료!

### **방법 3: Vercel (5분)**
1. [Vercel](https://vercel.com) 접속
2. GitHub 저장소 연결
3. 자동으로 배포 완료!

## 🌟 **PWA 특징**

- 🎨 **Glassmorphism + 네온 효과** 디자인
- 📱 **모든 기기에서 PWA 설치 가능**
- 🚀 **오프라인 동작 지원**
- 💡 **"따뜻한 기술, 직관적인 건강"** 철학

## 📱 **PWA 테스트 방법**

1. 배포된 URL로 접속
2. 모바일에서 "홈 화면에 추가" 버튼 클릭
3. 앱 아이콘 확인 (Glassmorphism + 네온 효과)
4. PWA로 실행 및 테스트

## 🎉 **결론**

**엔오건강도우미는 이제 친구들에게 보여줄 수 있는 완벽한 데모용 PWA입니다!**

지금 바로 배포하여 우리의 비전을 시연해보세요! 🚀✨
"@

$deployGuide | Out-File -FilePath "$deployDir/DEPLOY_GUIDE.md" -Encoding UTF8
Write-Host "✅ 배포 가이드 생성 완료" -ForegroundColor Green

# 6. 배포 준비 완료 안내
Write-Host ""
Write-Host "🎯 배포 준비 완료!" -ForegroundColor Magenta
Write-Host "📁 배포용 폴더: $deployDir" -ForegroundColor Green
Write-Host "📖 배포 가이드: $deployDir/DEPLOY_GUIDE.md" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 다음 단계:" -ForegroundColor Magenta
Write-Host "1. $deployDir 폴더를 Netlify에 드래그 앤 드롭 (가장 간단)" -ForegroundColor White
Write-Host "2. 또는 GitHub Pages에 업로드" -ForegroundColor White
Write-Host "3. 배포된 URL로 PWA 테스트" -ForegroundColor White

Write-Host ""
Write-Host "🎉 엔오건강도우미 PWA 배포 준비 완료!" -ForegroundColor Green
Write-Host "📱 이제 전 세계 어디서나 접속 가능합니다!" -ForegroundColor Cyan

# 7. 로컬 테스트 서버 시작
Write-Host ""
Write-Host "🌐 로컬 테스트 서버 시작..." -ForegroundColor Yellow
Write-Host "📱 브라우저에서 http://localhost:8000 접속하여 PWA 테스트" -ForegroundColor Cyan

try {
    Set-Location $deployDir
    Write-Host "🚀 Python HTTP 서버 시작 (포트 8000)..." -ForegroundColor Green
    Write-Host "⏹️  중지하려면 Ctrl+C" -ForegroundColor Red
    Write-Host "📱 브라우저에서 http://localhost:8000 접속" -ForegroundColor Cyan
    python -m http.server 8000
} catch {
    Write-Host "❌ Python 서버 시작 실패: $_" -ForegroundColor Red
    Write-Host "💡 Python이 설치되어 있는지 확인하세요" -ForegroundColor Yellow
} 