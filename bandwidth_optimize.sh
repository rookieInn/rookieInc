#!/bin/bash

# 服务器带宽优化脚本
echo "开始优化服务器带宽配置..."

# 1. 备份当前配置
echo "备份当前网络配置..."
cp /etc/sysctl.conf /etc/sysctl.conf.backup.$(date +%Y%m%d_%H%M%S)

# 2. 应用TCP优化参数
echo "应用TCP优化参数..."
cat >> /etc/sysctl.conf << EOF

# 带宽优化配置 - $(date)
# TCP缓冲区优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# TCP拥塞控制
net.ipv4.tcp_congestion_control = bbr

# 连接优化
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_syn_backlog = 8192
net.core.netdev_max_backlog = 5000

# 网络性能优化
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_moderate_rcvbuf = 1

# 减少TIME_WAIT连接
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
EOF

# 3. 应用配置
echo "应用网络配置..."
sysctl -p

# 4. 检查BBR是否启用
echo "检查TCP拥塞控制算法..."
sysctl net.ipv4.tcp_congestion_control

# 5. 优化文件描述符限制
echo "优化文件描述符限制..."
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 6. 创建网络监控别名
echo "创建网络监控别名..."
cat >> ~/.bashrc << EOF

# 网络监控别名
alias netmon='watch -n 1 "cat /proc/net/dev | grep -E \"(eth0|wlan0)\" | awk \"{print \\\"接收: \" \\\$2/1024/1024 \"MB, 发送: \" \\\$10/1024/1024 \"MB\\\"}\""'
alias netstat='ss -tuln'
alias bandwidth='./bandwidth_monitor.sh'
EOF

echo "优化完成！"
echo "请重新登录或运行 'source ~/.bashrc' 使别名生效"
echo "使用 './bandwidth_monitor.sh' 监控带宽使用情况"