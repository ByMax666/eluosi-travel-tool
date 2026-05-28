@echo off
chcp 65001 >nul
echo ================================================
echo   阿杜俄旅 · 服务器部署
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 请先安装 Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 安装依赖...
cd /d "%~dp0backend"
pip install -r requirements.txt

echo.
echo [2/3] 初始化数据库...
python -c "from database import init_db; init_db()"

echo.
echo [3/3] 启动后端服务...
echo.
echo ================================================
echo   后端API: http://117.72.218.38:8766
echo   前端页面: http://117.72.218.38:8765
echo   账号: 3056898  密码: pan3056898
echo ================================================
echo.

start "阿杜俄旅API" python server.py

:: Start frontend server
cd /d "%~dp0"
start "阿杜俄旅前端" python -m http.server 8765

echo 服务已启动！请确保防火墙开放 8765 和 8766 端口。
echo.
pause
