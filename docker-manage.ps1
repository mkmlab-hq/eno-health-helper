# Eno Health Helper Docker 환경 관리 스크립트
# PowerShell에서 실행

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "full", "test", "stop", "clean", "logs", "build")]
    [string]$Action = "dev"
)

Write-Host "🐳 Eno Health Helper Docker 환경 관리" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

function Show-Status {
    Write-Host "`n📊 현재 Docker 상태:" -ForegroundColor Yellow
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

function Start-DevEnvironment {
    Write-Host "`n🚀 개발 환경 시작 중..." -ForegroundColor Green
    docker-compose -f docker-compose.dev.yml up -d
    Write-Host "✅ 개발 환경이 시작되었습니다!" -ForegroundColor Green
    Write-Host "🌐 프론트엔드: http://localhost:3000" -ForegroundColor Blue
    Write-Host "🔧 백엔드: http://localhost:8000" -ForegroundColor Blue
    Write-Host "⚡ Functions: http://localhost:5001" -ForegroundColor Blue
}

function Start-FullEnvironment {
    Write-Host "`n🚀 전체 환경 시작 중..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✅ 전체 환경이 시작되었습니다!" -ForegroundColor Green
    Write-Host "🌐 프론트엔드: http://localhost:3000" -ForegroundColor Blue
    Write-Host "🔧 백엔드: http://localhost:8000" -ForegroundColor Blue
    Write-Host "⚡ Functions: http://localhost:5001" -ForegroundColor Blue
    Write-Host "🗄️ PostgreSQL: localhost:5432" -ForegroundColor Blue
    Write-Host "🔴 Redis: localhost:6379" -ForegroundColor Blue
}

function Start-TestEnvironment {
    Write-Host "`n🧪 테스트 환경 시작 중..." -ForegroundColor Green
    docker-compose -f docker-compose.test.yml up -d
    Write-Host "✅ 테스트 환경이 시작되었습니다!" -ForegroundColor Green
}

function Stop-AllServices {
    Write-Host "`n🛑 모든 서비스 중지 중..." -ForegroundColor Yellow
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    docker-compose -f docker-compose.test.yml down
    Write-Host "✅ 모든 서비스가 중지되었습니다!" -ForegroundColor Green
}

function Clean-Environment {
    Write-Host "`n🧹 환경 정리 중..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    docker-compose -f docker-compose.dev.yml down -v --remove-orphans
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
    docker system prune -f
    Write-Host "✅ 환경이 정리되었습니다!" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "`n📋 서비스 로그:" -ForegroundColor Yellow
    docker-compose logs --tail=50
}

function Build-Images {
    Write-Host "`n🔨 Docker 이미지 빌드 중..." -ForegroundColor Green
    docker-compose build --no-cache
    Write-Host "✅ 이미지 빌드가 완료되었습니다!" -ForegroundColor Green
}

# 메인 실행 로직
switch ($Action) {
    "dev" {
        Start-DevEnvironment
    }
    "full" {
        Start-FullEnvironment
    }
    "test" {
        Start-TestEnvironment
    }
    "stop" {
        Stop-AllServices
    }
    "clean" {
        Clean-Environment
    }
    "logs" {
        Show-Logs
    }
    "build" {
        Build-Images
    }
}

# 상태 표시
Show-Status

Write-Host "`n💡 사용법:" -ForegroundColor Cyan
Write-Host "  .\docker-manage.ps1 dev     # 개발 환경 시작" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 full    # 전체 환경 시작" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 test    # 테스트 환경 시작" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 stop    # 모든 서비스 중지" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 clean   # 환경 정리" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 logs    # 로그 확인" -ForegroundColor White
Write-Host "  .\docker-manage.ps1 build   # 이미지 재빌드" -ForegroundColor White
