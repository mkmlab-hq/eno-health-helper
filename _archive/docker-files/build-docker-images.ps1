# Eno Health Helper - Docker 이미지 빌드 스크립트
# PowerShell 스크립트

Write-Host "🐳 Eno Health Helper Docker 이미지 빌드 시작..." -ForegroundColor Green

# 작업 디렉토리 확인
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "📁 작업 디렉토리: $projectRoot" -ForegroundColor Yellow

# Docker 상태 확인
Write-Host "🔍 Docker 상태 확인 중..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker 버전: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker가 실행되지 않았습니다. Docker Desktop을 시작해주세요." -ForegroundColor Red
    exit 1
}

# 백엔드 이미지 빌드
Write-Host "🔨 백엔드 이미지 빌드 중..." -ForegroundColor Blue
try {
    docker build -t eno-backend:latest ./backend
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 백엔드 이미지 빌드 성공" -ForegroundColor Green
    } else {
        Write-Host "❌ 백엔드 이미지 빌드 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 백엔드 이미지 빌드 중 오류 발생: $_" -ForegroundColor Red
    exit 1
}

# 프론트엔드 이미지 빌드
Write-Host "🔨 프론트엔드 이미지 빌드 중..." -ForegroundColor Blue
try {
    docker build -t eno-frontend:latest ./frontend
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 프론트엔드 이미지 빌드 성공" -ForegroundColor Green
    } else {
        Write-Host "❌ 프론트엔드 이미지 빌드 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 프론트엔드 이미지 빌드 중 오류 발생: $_" -ForegroundColor Red
    exit 1
}

# Functions 이미지 빌드
Write-Host "🔨 Functions 이미지 빌드 중..." -ForegroundColor Blue
try {
    docker build -t eno-functions:latest ./functions
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Functions 이미지 빌드 성공" -ForegroundColor Green
    } else {
        Write-Host "❌ Functions 이미지 빌드 실패" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Functions 이미지 빌드 중 오류 발생: $_" -ForegroundColor Red
    exit 1
}

# 빌드된 이미지 확인
Write-Host "📋 빌드된 이미지 목록:" -ForegroundColor Blue
try {
    docker images | Select-String "eno"
} catch {
    Write-Host "⚠️ 이미지 목록 확인 실패" -ForegroundColor Yellow
}

# Docker Compose 테스트 실행 (선택사항)
$runTest = Read-Host "🧪 Docker Compose로 테스트를 실행하시겠습니까? (y/n)"
if ($runTest -eq "y" -or $runTest -eq "Y") {
    Write-Host "🚀 Docker Compose 테스트 시작..." -ForegroundColor Blue
    try {
        docker-compose -f docker-compose.test.yml up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 테스트 환경 시작 성공" -ForegroundColor Green
            Write-Host "🌐 백엔드: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "🌐 프론트엔드: http://localhost:3000" -ForegroundColor Cyan
            Write-Host "🌐 Functions: http://localhost:5001" -ForegroundColor Cyan
            
            $stopTest = Read-Host "🛑 테스트 환경을 중지하시겠습니까? (y/n)"
            if ($stopTest -eq "y" -or $stopTest -eq "Y") {
                docker-compose -f docker-compose.test.yml down
                Write-Host "✅ 테스트 환경 중지 완료" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ 테스트 환경 시작 실패" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 테스트 환경 시작 중 오류 발생: $_" -ForegroundColor Red
    }
}

Write-Host "🎉 모든 Docker 이미지 빌드가 완료되었습니다!" -ForegroundColor Green
Write-Host "📚 다음 단계: DOCKER_DEPLOYMENT_GUIDE.md 파일을 참조하여 배포를 진행하세요." -ForegroundColor Yellow
