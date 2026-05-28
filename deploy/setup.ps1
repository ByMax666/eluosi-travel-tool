Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  阿杜俄旅 · 服务器部署" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

# Check Python
try { python --version } catch { 
    Write-Host "[ERROR] 请先安装Python!" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] 安装依赖..." -ForegroundColor Green
Set-Location (Join-Path $PSScriptRoot "backend")
pip install -r requirements.txt

Write-Host "[2/3] 初始化数据库..." -ForegroundColor Green
python -c "from database import init_db; init_db()"

Write-Host "[3/3] 配置防火墙..." -ForegroundColor Green
New-NetFirewallRule -DisplayName "阿杜俄旅API" -Direction Inbound -Port 8766 -Protocol TCP -Action Allow 2>$null
New-NetFirewallRule -DisplayName "阿杜俄旅前端" -Direction Inbound -Port 8765 -Protocol TCP -Action Allow 2>$null

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  后端API: http://117.72.218.38:8766" -ForegroundColor White
Write-Host "  前端页面: http://117.72.218.38:8765/adu-system.html" -ForegroundColor White
Write-Host "  账号: 3056898 / pan3056898" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Start-Process python -ArgumentList "server.py" -WorkingDirectory (Join-Path $PSScriptRoot "backend")

Set-Location $PSScriptRoot
Start-Process python -ArgumentList "-m http.server 8765"

Write-Host "服务已启动！" -ForegroundColor Green
