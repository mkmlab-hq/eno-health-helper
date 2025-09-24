# 엔오건강도우미 백엔드 서버 시작 스크립트
# Docker Desktop 문제 시 로컬 환경에서 안정적으로 실행

Write-Host "🚀 엔오건강도우미 백엔드 서버 시작 중..." -ForegroundColor Green

# 포트 사용 중인 프로세스 확인 및 종료
$port = 8002
$processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue

if ($processes) {
    Write-Host "⚠️ 포트 $port 사용 중인 프로세스 발견, 종료 중..." -ForegroundColor Yellow
    foreach ($process in $processes) {
        $pid = $process.OwningProcess
        $processName = (Get-Process -Id $pid).ProcessName
        Write-Host "종료: $processName (PID: $pid)" -ForegroundColor Red
        Stop-Process -Id $pid -Force
    }
    Start-Sleep -Seconds 2
}

# Python 환경 확인
try {
    $pythonVersion = py --version
    Write-Host "✅ Python 버전: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python이 설치되지 않았습니다." -ForegroundColor Red
    exit 1
}

# 의존성 설치 확인
Write-Host "📦 Python 의존성 확인 중..." -ForegroundColor Blue
py -m pip install -r requirements.txt

# 서버 시작
Write-Host "🌐 서버를 포트 $port에서 시작합니다..." -ForegroundColor Green
Write-Host "📍 서버 URL: http://127.0.0.1:$port" -ForegroundColor Cyan
Write-Host "⏹️  서버 중지: Ctrl+C" -ForegroundColor Yellow

# 백그라운드에서 서버 실행
Start-Process -FilePath "py" -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", $port, "--log-level", "info" -WindowStyle Hidden

# 서버 상태 확인
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 서버가 성공적으로 시작되었습니다!" -ForegroundColor Green
        Write-Host "🌐 API 엔드포인트: http://127.0.0.1:$port" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ 서버 응답 확인 실패, 잠시 후 다시 시도해주세요." -ForegroundColor Yellow
}

Write-Host "`n📋 서버 관리 명령어:" -ForegroundColor White
Write-Host "  서버 상태 확인: Get-Process -Name 'python'" -ForegroundColor Gray
Write-Host "  서버 종료: Get-Process -Name 'python' | Stop-Process -Force" -ForegroundColor Gray
