# GitHub Container Registry (GHCR) 푸시 스크립트
# PowerShell용

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,
    
    [string]$Tag = "latest"
)

Write-Host "🚀 GitHub Container Registry 푸시 시작..." -ForegroundColor Green
Write-Host "사용자: $GitHubUsername" -ForegroundColor Yellow
Write-Host "태그: $Tag" -ForegroundColor Yellow

# 작업 디렉토리 확인
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "📁 작업 디렉토리: $projectRoot" -ForegroundColor Blue

# Docker 상태 확인
Write-Host "🔍 Docker 상태 확인 중..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker 버전: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker가 실행되지 않았습니다." -ForegroundColor Red
    exit 1
}

# GitHub Container Registry 로그인
Write-Host "🔐 GitHub Container Registry 로그인 중..." -ForegroundColor Blue
try {
    echo $GitHubToken | docker login ghcr.io -u $GitHubUsername --password-stdin
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GHCR 로그인 성공" -ForegroundColor Green
    } else {
        Write-Host "❌ GHCR 로그인 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ GHCR 로그인 중 오류 발생: $_" -ForegroundColor Red
    exit 1
}

# 이미지 태깅
Write-Host "🏷️ 이미지 태깅 중..." -ForegroundColor Blue

# 백엔드 이미지 태깅
Write-Host "  - 백엔드 이미지 태깅..." -ForegroundColor White
docker tag eno-backend:$Tag ghcr.io/$GitHubUsername/eno-health-helper/backend:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ 백엔드 태깅 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ 백엔드 태깅 실패" -ForegroundColor Red
}

# 프론트엔드 이미지 태깅
Write-Host "  - 프론트엔드 이미지 태깅..." -ForegroundColor White
docker tag eno-frontend:$Tag ghcr.io/$GitHubUsername/eno-health-helper/frontend:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ 프론트엔드 태깅 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ 프론트엔드 태깅 실패" -ForegroundColor Red
}

# Functions 이미지 태깅
Write-Host "  - Functions 이미지 태깅..." -ForegroundColor White
docker tag eno-functions:$Tag ghcr.io/$GitHubUsername/eno-health-helper/functions:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ Functions 태깅 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ Functions 태깅 실패" -ForegroundColor Red
}

# 이미지 푸시
Write-Host "📤 이미지 푸시 중..." -ForegroundColor Blue

# 백엔드 이미지 푸시
Write-Host "  - 백엔드 이미지 푸시..." -ForegroundColor White
docker push ghcr.io/$GitHubUsername/eno-health-helper/backend:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ 백엔드 푸시 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ 백엔드 푸시 실패" -ForegroundColor Red
}

# 프론트엔드 이미지 푸시
Write-Host "  - 프론트엔드 이미지 푸시..." -ForegroundColor White
docker push ghcr.io/$GitHubUsername/eno-health-helper/frontend:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ 프론트엔드 푸시 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ 프론트엔드 푸시 실패" -ForegroundColor Red
}

# Functions 이미지 푸시
Write-Host "  - Functions 이미지 푸시..." -ForegroundColor White
docker push ghcr.io/$GitHubUsername/eno-health-helper/functions:$Tag
if ($LASTEXITCODE -eq 0) {
    Write-Host "    ✅ Functions 푸시 완료" -ForegroundColor Green
} else {
    Write-Host "    ❌ Functions 푸시 실패" -ForegroundColor Red
}

# 푸시된 이미지 확인
Write-Host "📋 푸시된 이미지 목록:" -ForegroundColor Blue
docker images | Select-String "ghcr.io/$GitHubUsername/eno-health-helper"

Write-Host "🎉 GitHub Container Registry 푸시 완료!" -ForegroundColor Green
Write-Host "🌐 이미지 URL:" -ForegroundColor Yellow
Write-Host "  - 백엔드: ghcr.io/$GitHubUsername/eno-health-helper/backend:$Tag" -ForegroundColor Cyan
Write-Host "  - 프론트엔드: ghcr.io/$GitHubUsername/eno-health-helper/frontend:$Tag" -ForegroundColor Cyan
Write-Host "  - Functions: ghcr.io/$GitHubUsername/eno-health-helper/functions:$Tag" -ForegroundColor Cyan

Write-Host "📚 다음 단계: 프로덕션 배포를 진행하세요." -ForegroundColor Yellow
