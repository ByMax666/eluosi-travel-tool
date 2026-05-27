#!/bin/bash
# 阿杜俄旅 · 一键启动脚本

cd "$(dirname "$0")"

echo "🇷🇺 阿杜俄旅 · 启动中..."

# Kill old processes
pkill -f "python3.*server.py" 2>/dev/null
pkill -f "http.server.*8765" 2>/dev/null
sleep 1

# Start backend API (port 8766)
echo "📡 启动后端API (端口8766)..."
cd backend
rm -f adu_travel.db
python3 server.py > /tmp/adu_api.log 2>&1 &
cd ..

# Start frontend (port 8765, 0.0.0.0 for LAN access)
echo "🌐 启动前端服务器 (端口8765)..."
python3 -m http.server 8765 --bind 0.0.0.0 > /tmp/adu_web.log 2>&1 &

sleep 2

# Check
if curl -s http://localhost:8766/api/health > /dev/null 2>&1; then
    echo "✅ 后端API: 正常"
else
    echo "❌ 后端API: 启动失败"
fi

# Get IP
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🇷🇺 阿杜俄旅 已启动！"
echo ""
echo "  你的电脑打开:"
echo "  → http://localhost:8765/adu-system.html"
echo ""
echo "  同事打开 (同一WiFi):"
echo "  → http://$IP:8765/adu-system.html"
echo ""
echo "  账号: 3056898  密码: pan3056898"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
