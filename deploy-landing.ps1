# MKM LAB 랜딩페이지 배포 스크립트
# PowerShell 실행 정책: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "🚀 MKM LAB 랜딩페이지 배포 시작..." -ForegroundColor Green

# 1. 의존성 설치
Write-Host "📦 의존성 설치 중..." -ForegroundColor Yellow
Set-Location frontend
npm install

# 2. 프로덕션 빌드
Write-Host "🏗️ 프로덕션 빌드 중..." -ForegroundColor Yellow
npm run build

# 3. 루트로 이동
Set-Location ..

# 4. Firebase 배포
Write-Host "🔥 Firebase 배포 중..." -ForegroundColor Yellow
firebase deploy --only hosting

# 5. 배포 완료 메시지
Write-Host "✅ 랜딩페이지 배포 완료!" -ForegroundColor Green
Write-Host "🌐 URL: https://mkmlab.space" -ForegroundColor Cyan
Write-Host "📱 랜딩페이지: https://mkmlab.space/landing" -ForegroundColor Cyan

# 6. 도메인 연결 확인
Write-Host "🔍 도메인 연결 확인 중..." -ForegroundColor Yellow
Write-Host "💡 Firebase Console에서 커스텀 도메인 설정을 확인하세요:" -ForegroundColor White
Write-Host "   - Firebase Console > Hosting > Custom domains" -ForegroundColor White
Write-Host "   - mkmlab.space 추가" -ForegroundColor White
