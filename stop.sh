#!/bin/bash
echo "🛑 停止所有服务..."
pkill -f "python3.*server.py" 2>/dev/null
pkill -f "http.server.*8765" 2>/dev/null
sleep 1
echo "✅ 已停止"
