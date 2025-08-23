# DNS 설정 확인 스크립트
# PowerShell 실행 정책: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "🔍 mkmlab.space DNS 설정 확인 중..." -ForegroundColor Green

# 현재 DNS 설정 확인
Write-Host "`n📡 A 레코드 확인:" -ForegroundColor Yellow
nslookup -type=A mkmlab.space

Write-Host "`n📡 TXT 레코드 확인:" -ForegroundColor Yellow
nslookup -type=TXT mkmlab.space

Write-Host "`n📡 AAAA 레코드 확인:" -ForegroundColor Yellow
nslookup -type=AAAA mkmlab.space

Write-Host "`n✅ 올바른 설정:" -ForegroundColor Green
Write-Host "   A 레코드: mkmlab.space → 199.36.158.100" -ForegroundColor White
Write-Host "   TXT 레코드: mkmlab.space → hosting-site=eno-health-helper" -ForegroundColor White

Write-Host "`n❌ 삭제해야 할 레코드:" -ForegroundColor Red
Write-Host "   A: 145.223.124.221" -ForegroundColor White
Write-Host "   A: 88.223.87.239" -ForegroundColor White
Write-Host "   AAAA: 2a02:4780:4a:9be:496:2bec:f456:e93" -ForegroundColor White
Write-Host "   AAAA: 2a02:4780:4d:d888:4ede:6e66:26b6:5e8c" -ForegroundColor White

Write-Host "`n💡 DNS 설정 완료 후 다시 실행하여 확인하세요!" -ForegroundColor Cyan
