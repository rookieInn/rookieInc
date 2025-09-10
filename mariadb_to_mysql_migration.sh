#!/bin/bash

# MariaDB到MySQL迁移脚本
# 作者: AI Assistant
# 功能: 将MariaDB数据库迁移到MySQL

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 安装必要的软件包
install_packages() {
    log_info "更新包列表..."
    apt-get update -y
    
    log_info "安装MariaDB和MySQL..."
    apt-get install -y mariadb-server mariadb-client mysql-server mysql-client
    
    log_success "数据库软件安装完成"
}

# 启动MariaDB并创建测试数据库
setup_mariadb() {
    log_info "启动MariaDB服务..."
    systemctl start mariadb
    systemctl enable mariadb
    
    # 等待MariaDB启动
    sleep 5
    
    log_info "创建测试数据库和表..."
    mysql -u root -e "
        CREATE DATABASE IF NOT EXISTS test_db;
        USE test_db;
        
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        INSERT INTO users (username, email) VALUES 
            ('john_doe', 'john@example.com'),
            ('jane_smith', 'jane@example.com'),
            ('bob_wilson', 'bob@example.com');
            
        INSERT INTO products (name, price, description) VALUES 
            ('Laptop', 999.99, 'High-performance laptop'),
            ('Mouse', 29.99, 'Wireless mouse'),
            ('Keyboard', 79.99, 'Mechanical keyboard');
    "
    
    log_success "MariaDB测试数据创建完成"
}

# 停止MariaDB服务
stop_mariadb() {
    log_info "停止MariaDB服务..."
    systemctl stop mariadb
    log_success "MariaDB已停止"
}

# 启动MySQL并配置
setup_mysql() {
    log_info "启动MySQL服务..."
    systemctl start mysql
    systemctl enable mysql
    
    # 等待MySQL启动
    sleep 5
    
    # 设置MySQL root密码（如果需要）
    log_info "配置MySQL..."
    mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'rootpassword';"
    
    log_success "MySQL配置完成"
}

# 方法1: 使用mysqldump导出MariaDB数据
migrate_with_mysqldump() {
    log_info "使用mysqldump方法迁移数据..."
    
    # 启动MariaDB进行导出
    systemctl start mariadb
    sleep 3
    
    # 导出数据库结构和数据
    mysqldump -u root test_db > /tmp/mariadb_export.sql
    
    # 停止MariaDB
    systemctl stop mariadb
    
    # 导入到MySQL
    mysql -u root -prootpassword -e "CREATE DATABASE IF NOT EXISTS test_db;"
    mysql -u root -prootpassword test_db < /tmp/mariadb_export.sql
    
    log_success "mysqldump迁移完成"
}

# 方法2: 直接复制数据文件（高级方法）
migrate_with_file_copy() {
    log_info "使用文件复制方法迁移数据..."
    
    # 获取MariaDB和MySQL数据目录
    MARIADB_DATA_DIR="/var/lib/mysql"
    MYSQL_DATA_DIR="/var/lib/mysql"
    
    # 确保MySQL已停止
    systemctl stop mysql
    
    # 备份MySQL数据目录
    if [ -d "$MYSQL_DATA_DIR" ]; then
        log_info "备份MySQL数据目录..."
        cp -r "$MYSQL_DATA_DIR" "${MYSQL_DATA_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 复制MariaDB数据文件到MySQL目录
    log_info "复制MariaDB数据文件..."
    cp -r "$MARIADB_DATA_DIR"/* "$MYSQL_DATA_DIR"/
    
    # 设置正确的权限
    chown -R mysql:mysql "$MYSQL_DATA_DIR"
    chmod -R 755 "$MYSQL_DATA_DIR"
    
    # 启动MySQL
    systemctl start mysql
    
    log_success "文件复制迁移完成"
}

# 验证迁移结果
verify_migration() {
    log_info "验证迁移结果..."
    
    # 检查数据库是否存在
    DATABASES=$(mysql -u root -prootpassword -e "SHOW DATABASES;" | grep test_db)
    if [ -n "$DATABASES" ]; then
        log_success "数据库 'test_db' 迁移成功"
    else
        log_error "数据库迁移失败"
        return 1
    fi
    
    # 检查表是否存在
    TABLES=$(mysql -u root -prootpassword -e "USE test_db; SHOW TABLES;" | grep -E "(users|products)")
    if [ -n "$TABLES" ]; then
        log_success "表迁移成功"
    else
        log_error "表迁移失败"
        return 1
    fi
    
    # 检查数据
    USER_COUNT=$(mysql -u root -prootpassword -e "USE test_db; SELECT COUNT(*) FROM users;" | tail -1)
    PRODUCT_COUNT=$(mysql -u root -prootpassword -e "USE test_db; SELECT COUNT(*) FROM products;" | tail -1)
    
    log_info "用户表记录数: $USER_COUNT"
    log_info "产品表记录数: $PRODUCT_COUNT"
    
    if [ "$USER_COUNT" -gt 0 ] && [ "$PRODUCT_COUNT" -gt 0 ]; then
        log_success "数据迁移验证成功"
    else
        log_error "数据迁移验证失败"
        return 1
    fi
}

# 显示迁移后的数据
show_migrated_data() {
    log_info "显示迁移后的数据..."
    
    echo -e "\n${BLUE}=== 用户数据 ===${NC}"
    mysql -u root -prootpassword -e "USE test_db; SELECT * FROM users;"
    
    echo -e "\n${BLUE}=== 产品数据 ===${NC}"
    mysql -u root -prootpassword -e "USE test_db; SELECT * FROM products;"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    rm -f /tmp/mariadb_export.sql
    log_success "清理完成"
}

# 主函数
main() {
    log_info "开始MariaDB到MySQL迁移过程..."
    
    # 检查root权限
    check_root
    
    # 安装软件包
    install_packages
    
    # 设置MariaDB
    setup_mariadb
    
    # 停止MariaDB
    stop_mariadb
    
    # 设置MySQL
    setup_mysql
    
    # 选择迁移方法
    echo -e "\n${YELLOW}请选择迁移方法:${NC}"
    echo "1) mysqldump方法 (推荐)"
    echo "2) 文件复制方法 (高级)"
    read -p "请输入选择 (1-2): " choice
    
    case $choice in
        1)
            migrate_with_mysqldump
            ;;
        2)
            migrate_with_file_copy
            ;;
        *)
            log_error "无效选择，使用默认方法mysqldump"
            migrate_with_mysqldump
            ;;
    esac
    
    # 验证迁移
    if verify_migration; then
        show_migrated_data
        log_success "迁移完成！"
    else
        log_error "迁移失败，请检查错误信息"
        exit 1
    fi
    
    # 清理
    cleanup
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi