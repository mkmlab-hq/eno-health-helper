# 엔오건강도우미 Vercel 자동 배포 스크립트
# 사용자 입력 없이 자동 배포

Write-Host "🚀 엔오건강도우미 Vercel 자동 배포 시작!" -ForegroundColor Green
Write-Host "✨ 디자인 철학: '따뜻한 기술, 직관적인 건강'" -ForegroundColor Cyan

# 1. 프로젝트 디렉토리로 이동
Set-Location $PSScriptRoot
Write-Host "📁 프로젝트 디렉토리: $(Get-Location)" -ForegroundColor Yellow

# 2. PWA 아이콘 확인
Write-Host "🔍 PWA 아이콘 확인 중..." -ForegroundColor Yellow
$iconCount = (Get-ChildItem "frontend/public/icons/*.png" | Measure-Object).Count
Write-Host "✅ PWA 아이콘: $iconCount개 발견" -ForegroundColor Green

# 3. Vercel 설정 파일 생성
Write-Host "⚙️ Vercel 설정 파일 생성 중..." -ForegroundColor Yellow

$vercelJson = @"
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/public/**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/public/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_APP_NAME": "엔오건강도우미",
    "NEXT_PUBLIC_DOMAIN": "eno-health-helper.vercel.app"
  }
}
"@

$vercelJson | Out-File -FilePath "vercel.json" -Encoding UTF8
Write-Host "✅ Vercel 설정 파일 생성 완료" -ForegroundColor Green

# 4. 정적 배포용 파일 준비
Write-Host "📦 정적 배포용 파일 준비 중..." -ForegroundColor Yellow

# frontend/public의 모든 파일을 루트로 복사
$publicDir = "frontend/public"
$files = Get-ChildItem $publicDir -Recurse -File

foreach ($file in $files) {
    $relativePath = $file.FullName.Substring($file.FullName.IndexOf($publicDir) + $publicDir.Length + 1)
    $targetPath = $relativePath
    
    # 디렉토리 생성
    $targetDir = Split-Path $targetPath -Parent
    if ($targetDir -and $targetDir -ne "") {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    # 파일 복사
    Copy-Item $file.FullName -Destination $targetPath -Force
}

Write-Host "✅ 정적 파일 준비 완료" -ForegroundColor Green

# 5. Vercel 자동 배포 실행
Write-Host "🚀 Vercel 자동 배포 실행 중..." -ForegroundColor Green
Write-Host "⏳ 잠시만 기다려주세요..." -ForegroundColor Yellow

try {
    # Vercel 배포 (자동 모드)
    $deployResult = npx vercel --prod --yes 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎉 Vercel 배포 성공!" -ForegroundColor Green
        Write-Host "📱 배포된 URL을 확인하세요!" -ForegroundColor Cyan
        
        # 배포 결과에서 URL 추출 시도
        if ($deployResult -match "https://[^\s]+") {
            $deployedUrl = $matches[0]
            Write-Host "🌐 배포된 URL: $deployedUrl" -ForegroundColor Green
            Write-Host "📱 이제 친구들에게 이 URL을 공유할 수 있습니다!" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Vercel 배포 실패" -ForegroundColor Red
        Write-Host "🔍 오류 내용: $deployResult" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 배포 중 오류 발생: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 다음 단계:" -ForegroundColor Magenta
Write-Host "1. 배포된 URL로 접속하여 PWA 테스트" -ForegroundColor White
Write-Host "2. 모바일에서 '홈 화면에 추가' 테스트" -ForegroundColor White
Write-Host "3. 친구들에게 URL 공유" -ForegroundColor White

Write-Host ""
Write-Host "🎉 엔오건강도우미 PWA 온라인 배포 완료!" -ForegroundColor Green
Write-Host "📱 전 세계 어디서나 접속 가능합니다!" -ForegroundColor Cyan 