#!/bin/bash

# 用户图片清理系统安装脚本
# 作者: AI Assistant
# 功能: 安装和配置用户图片清理系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_success "Python版本: $PYTHON_VERSION"
    else
        log_error "Python3未安装，请先安装Python3"
        exit 1
    fi
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖包..."
    
    # 创建requirements.txt文件
    cat > requirements_image_cleanup.txt << EOF
oss2>=2.18.0
schedule>=1.2.0
pandas>=1.5.0
matplotlib>=3.6.0
configparser>=5.3.0
EOF
    
    # 安装依赖
    pip3 install -r requirements_image_cleanup.txt
    
    log_success "Python依赖安装完成"
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    
    if [ ! -f "config.ini" ]; then
        log_warning "config.ini文件不存在，将创建示例配置文件"
        
        cat > config.ini << 'EOF'
[aliyun_oss]
access_key_id = YOUR_ACCESS_KEY_ID
access_key_secret = YOUR_ACCESS_KEY_SECRET
endpoint = https://oss-cn-hangzhou.aliyuncs.com
bucket_name = YOUR_BUCKET_NAME

[user_images]
# 用户图片管理配置
# 每个用户最多保留的图片数量
max_images_per_user = 10
# 数据库文件路径
database_path = user_images.db

[image_cleanup]
# 图片清理配置
# 清理检查间隔（小时）
cleanup_interval_hours = 24
# 图片标记为不活跃后多少天可以删除
cleanup_delay_days = 1
# 批量处理大小
batch_size = 100
# 是否启用试运行模式（不实际删除）
enable_dry_run = False
# 清理报告保存目录
report_dir = ./cleanup_reports

[oss_cleaner]
# OSS清理器配置
# 最大重试次数
max_retries = 3
# 重试延迟（秒）
retry_delay = 1
# 删除操作间隔（秒）
delete_interval = 0.1

[logging]
# 日志级别：DEBUG, INFO, WARNING, ERROR
level = INFO
# 日志文件路径
log_file = user_image_cleanup.log
EOF
        
        log_success "示例配置文件已创建: config.ini"
        log_warning "请编辑config.ini文件，填入正确的OSS配置信息"
    else
        log_info "config.ini文件已存在，跳过创建"
    fi
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    mkdir -p cleanup_reports
    mkdir -p logs
    mkdir -p data
    
    log_success "目录结构创建完成"
}

# 设置文件权限
set_permissions() {
    log_info "设置文件权限..."
    
    chmod +x user_image_cleanup_scheduler.py
    chmod +x user_image_models.py
    chmod +x oss_image_cleaner.py
    
    log_success "文件权限设置完成"
}

# 创建systemd服务文件
create_systemd_service() {
    log_info "创建systemd服务文件..."
    
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    cat > user-image-cleanup.service << EOF
[Unit]
Description=User Image Cleanup Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/user_image_cleanup_scheduler.py --schedule --config $CURRENT_DIR/config.ini
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "systemd服务文件已创建: user-image-cleanup.service"
    log_info "要安装服务，请运行:"
    log_info "  sudo cp user-image-cleanup.service /etc/systemd/system/"
    log_info "  sudo systemctl daemon-reload"
    log_info "  sudo systemctl enable user-image-cleanup"
    log_info "  sudo systemctl start user-image-cleanup"
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > start_image_cleanup.sh << 'EOF'
#!/bin/bash

# 用户图片清理系统启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.ini"

echo "启动用户图片清理系统..."
echo "配置文件: $CONFIG_FILE"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在: $CONFIG_FILE"
    echo "请先运行安装脚本或创建配置文件"
    exit 1
fi

# 启动清理调度器
cd "$SCRIPT_DIR"
python3 user_image_cleanup_scheduler.py --schedule --config "$CONFIG_FILE"
EOF
    
    chmod +x start_image_cleanup.sh
    log_success "启动脚本已创建: start_image_cleanup.sh"
}

# 创建测试脚本
create_test_script() {
    log_info "创建测试脚本..."
    
    cat > test_image_cleanup.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户图片清理系统测试脚本
"""

import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_image_models import UserImageDatabase, UserImage
from oss_image_cleaner import OSSImageCleaner
from user_image_cleanup_scheduler import UserImageCleanupScheduler

def test_database():
    """测试数据库功能"""
    print("测试数据库功能...")
    
    try:
        # 创建数据库实例
        db = UserImageDatabase()
        
        # 创建测试图片记录
        test_image = UserImage(
            id=None,
            user_id="test_user_001",
            image_name="test_image.jpg",
            oss_key="users/test_user_001/test_image.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            upload_time=datetime.now(),
            last_accessed=None
        )
        
        # 添加图片记录
        success = db.add_user_image(test_image)
        print(f"添加图片记录: {'成功' if success else '失败'}")
        
        # 获取用户图片
        images = db.get_user_images("test_user_001")
        print(f"用户图片数量: {len(images)}")
        
        # 获取统计信息
        stats = db.get_user_image_stats("test_user_001")
        print(f"用户统计: {stats}")
        
        db.close()
        print("✅ 数据库测试完成")
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")

def test_oss_cleaner():
    """测试OSS清理器功能"""
    print("测试OSS清理器功能...")
    
    try:
        # 创建OSS清理器实例
        cleaner = OSSImageCleaner()
        
        # 获取存储统计
        stats = cleaner.get_storage_stats()
        print(f"OSS存储统计: {stats}")
        
        print("✅ OSS清理器测试完成")
        
    except Exception as e:
        print(f"❌ OSS清理器测试失败: {e}")

def test_scheduler():
    """测试清理调度器功能"""
    print("测试清理调度器功能...")
    
    try:
        # 创建调度器实例
        scheduler = UserImageCleanupScheduler()
        
        # 获取统计信息
        stats = scheduler.get_cleanup_stats()
        print(f"清理统计: {stats}")
        
        # 执行试运行清理
        result = scheduler.cleanup_user_images(dry_run=True)
        print(f"试运行清理结果: {result}")
        
        scheduler.close()
        print("✅ 清理调度器测试完成")
        
    except Exception as e:
        print(f"❌ 清理调度器测试失败: {e}")

def main():
    """主测试函数"""
    print("="*50)
    print("用户图片清理系统测试")
    print("="*50)
    
    # 测试各个组件
    test_database()
    print()
    
    test_oss_cleaner()
    print()
    
    test_scheduler()
    print()
    
    print("="*50)
    print("测试完成")
    print("="*50)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x test_image_cleanup.py
    log_success "测试脚本已创建: test_image_cleanup.py"
}

# 显示使用说明
show_usage() {
    log_info "显示使用说明..."
    
    cat << EOF

${GREEN}用户图片清理系统安装完成！${NC}

${YELLOW}配置文件:${NC}
  - config.ini: 主配置文件，请编辑填入正确的OSS配置

${YELLOW}主要脚本:${NC}
  - user_image_cleanup_scheduler.py: 清理调度器
  - user_image_models.py: 数据库模型
  - oss_image_cleaner.py: OSS清理器

${YELLOW}使用命令:${NC}
  # 执行一次清理（试运行）
  python3 user_image_cleanup_scheduler.py --cleanup --dry-run

  # 执行一次清理（实际删除）
  python3 user_image_cleanup_scheduler.py --cleanup

  # 启动定时清理任务
  python3 user_image_cleanup_scheduler.py --schedule

  # 查看统计信息
  python3 user_image_cleanup_scheduler.py --stats

  # 运行测试
  python3 test_image_cleanup.py

${YELLOW}服务管理:${NC}
  # 安装为系统服务
  sudo cp user-image-cleanup.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable user-image-cleanup
  sudo systemctl start user-image-cleanup

  # 查看服务状态
  sudo systemctl status user-image-cleanup

  # 查看服务日志
  sudo journalctl -u user-image-cleanup -f

${YELLOW}注意事项:${NC}
  1. 请先编辑config.ini文件，填入正确的OSS配置
  2. 建议先使用--dry-run模式测试
  3. 定期检查清理日志文件
  4. 确保有足够的磁盘空间存储日志和报告

EOF
}

# 主函数
main() {
    log_info "开始安装用户图片清理系统..."
    
    # 检查Python
    check_python
    
    # 安装依赖
    install_dependencies
    
    # 创建配置文件
    create_config
    
    # 创建目录结构
    create_directories
    
    # 设置文件权限
    set_permissions
    
    # 创建systemd服务
    create_systemd_service
    
    # 创建启动脚本
    create_startup_script
    
    # 创建测试脚本
    create_test_script
    
    # 显示使用说明
    show_usage
    
    log_success "用户图片清理系统安装完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi