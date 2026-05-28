#!/bin/bash
# 阿杜俄旅 · 服务器一键部署
# 在服务器上复制粘贴运行即可

set -e
echo "🇷🇺 阿杜俄旅 · 服务器部署开始..."

# 1. Install Python dependencies
echo "[1/5] 安装依赖..."
pip3 install fastapi uvicorn python-jose python-multipart 2>&1 | tail -3

# 2. Create app directory
echo "[2/5] 创建目录..."
mkdir -p /opt/adutravel/backend
cd /opt/adutravel

# 3. Download code from GitHub
echo "[3/5] 下载代码..."
curl -sL https://github.com/ByMax666/eluosi-travel-tool/archive/refs/heads/main.tar.gz | tar xz --strip=1

# 4. Init database
echo "[4/5] 初始化数据库..."
cd backend
rm -f adu_travel.db
python3 -c "from database import init_db; init_db()"

# 5. Setup systemd service
echo "[5/5] 配置服务..."
cat > /etc/systemd/system/adutravel-api.service << 'SVC'
[Unit]
Description=阿杜俄旅API
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/adutravel/backend
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVC

systemctl daemon-reload
systemctl enable adutravel-api
systemctl start adutravel-api

# 6. Firewall
echo "配置防火墙..."
firewall-cmd --add-port=8766/tcp --permanent 2>/dev/null || true
firewall-cmd --add-port=8765/tcp --permanent 2>/dev/null || true
firewall-cmd --reload 2>/dev/null || true
iptables -I INPUT -p tcp --dport 8766 -j ACCEPT 2>/dev/null || true
iptables -I INPUT -p tcp --dport 8765 -j ACCEPT 2>/dev/null || true

# 7. Frontend server via python
cat > /etc/systemd/system/adutravel-web.service << 'SVC2'
[Unit]
Description=阿杜俄旅前端
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/adutravel
ExecStart=/usr/bin/python3 -m http.server 8765 --bind 0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVC2

systemctl daemon-reload
systemctl enable adutravel-web
systemctl start adutravel-web

sleep 2

echo ""
echo "================================================"
echo "  🇷🇺 阿杜俄旅 部署完成！"
echo ""
echo "  前端: http://117.72.218.38:8765/adu-system.html"
echo "  API:  http://117.72.218.38:8766"
echo "  账号: 3056898 / pan3056898"
echo ""
echo "  查看状态: systemctl status adutravel-api"
echo "================================================"
