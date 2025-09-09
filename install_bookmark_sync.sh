#!/bin/bash

# Chrome书签同步到Edge浏览器安装脚本

echo "正在安装Chrome到Edge书签同步工具..."

# 检查Python版本
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 需要Python 3.6或更高版本"
    exit 1
fi

# 安装依赖
echo "安装Python依赖..."
pip3 install -r bookmark_sync_requirements.txt

# 设置脚本权限
chmod +x chrome_to_edge_sync.py

# 创建systemd服务文件
echo "创建systemd服务..."
sudo tee /etc/systemd/system/bookmark-sync.service > /dev/null <<EOF
[Unit]
Description=Chrome to Edge Bookmark Sync Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/workspace
ExecStart=/usr/bin/python3 /workspace/chrome_to_edge_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建定时器文件
sudo tee /etc/systemd/system/bookmark-sync.timer > /dev/null <<EOF
[Unit]
Description=Run Chrome to Edge Bookmark Sync every 30 minutes
Requires=bookmark-sync.service

[Timer]
OnCalendar=*:0/30
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 重新加载systemd
sudo systemctl daemon-reload

echo "安装完成！"
echo ""
echo "使用方法："
echo "1. 运行一次同步: python3 chrome_to_edge_sync.py --once"
echo "2. 启动定期同步服务: sudo systemctl start bookmark-sync.service"
echo "3. 启用开机自启: sudo systemctl enable bookmark-sync.service"
echo "4. 启用定时器: sudo systemctl enable bookmark-sync.timer"
echo "5. 启动定时器: sudo systemctl start bookmark-sync.timer"
echo ""
echo "查看日志: journalctl -u bookmark-sync.service -f"
echo "查看定时器状态: systemctl status bookmark-sync.timer"