#!/bin/bash
# FFmpeg安装脚本

echo "🎬 正在安装FFmpeg..."

# 检查系统类型
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian系统
    echo "检测到Ubuntu/Debian系统，使用apt安装..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
elif command -v yum &> /dev/null; then
    # CentOS/RHEL系统
    echo "检测到CentOS/RHEL系统，使用yum安装..."
    sudo yum install -y epel-release
    sudo yum install -y ffmpeg
elif command -v dnf &> /dev/null; then
    # Fedora系统
    echo "检测到Fedora系统，使用dnf安装..."
    sudo dnf install -y ffmpeg
elif command -v pacman &> /dev/null; then
    # Arch Linux系统
    echo "检测到Arch Linux系统，使用pacman安装..."
    sudo pacman -S ffmpeg
elif command -v brew &> /dev/null; then
    # macOS系统
    echo "检测到macOS系统，使用Homebrew安装..."
    brew install ffmpeg
else
    echo "❌ 不支持的系统，请手动安装FFmpeg"
    echo "请访问: https://ffmpeg.org/download.html"
    exit 1
fi

# 验证安装
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg安装成功!"
    ffmpeg -version | head -1
else
    echo "❌ FFmpeg安装失败"
    exit 1
fi

echo "🎉 FFmpeg安装完成，现在可以使用视频水印工具了!"