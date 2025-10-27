#!/bin/bash

# 带宽监控脚本
# 使用方法: ./bandwidth_monitor.sh [监控时间(秒)]

MONITOR_TIME=${1:-60}  # 默认监控60秒
INTERFACE="eth0"

echo "开始监控网络接口 $INTERFACE，持续 $MONITOR_TIME 秒..."
echo "时间戳,接收速率(KB/s),发送速率(KB/s),总速率(KB/s)"
echo "----------------------------------------"

# 获取初始数据
RX_BYTES_OLD=$(cat /proc/net/dev | grep $INTERFACE | awk '{print $2}')
TX_BYTES_OLD=$(cat /proc/net/dev | grep $INTERFACE | awk '{print $10}')

for i in $(seq 1 $MONITOR_TIME); do
    sleep 1
    
    # 获取当前数据
    RX_BYTES_NEW=$(cat /proc/net/dev | grep $INTERFACE | awk '{print $2}')
    TX_BYTES_NEW=$(cat /proc/net/dev | grep $INTERFACE | awk '{print $10}')
    
    # 计算速率 (字节/秒 转换为 KB/秒)
    RX_RATE=$(( (RX_BYTES_NEW - RX_BYTES_OLD) / 1024 ))
    TX_RATE=$(( (TX_BYTES_NEW - TX_BYTES_OLD) / 1024 ))
    TOTAL_RATE=$(( RX_RATE + TX_RATE ))
    
    # 输出结果
    echo "$(date '+%H:%M:%S'),$RX_RATE,$TX_RATE,$TOTAL_RATE"
    
    # 更新旧值
    RX_BYTES_OLD=$RX_BYTES_NEW
    TX_BYTES_OLD=$TX_BYTES_NEW
done

echo "监控完成！"