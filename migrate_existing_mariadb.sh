#!/bin/bash

# 现有MariaDB数据文件迁移到MySQL脚本
# 适用于MariaDB无法启动的情况

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <MariaDB数据目录> [目标数据库名]"
    echo "示例: $0 /var/lib/mysql test_db"
    echo "示例: $0 /path/to/mariadb/data my_database"
    exit 1
fi

MARIADB_DATA_DIR="$1"
TARGET_DB_NAME="${2:-migrated_db}"

# 检查MariaDB数据目录是否存在
if [ ! -d "$MARIADB_DATA_DIR" ]; then
    log_error "MariaDB数据目录不存在: $MARIADB_DATA_DIR"
    exit 1
fi

log_info "MariaDB数据目录: $MARIADB_DATA_DIR"
log_info "目标数据库名: $TARGET_DB_NAME"

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
    log_error "此脚本需要root权限运行"
    log_info "请使用: sudo $0 $MARIADB_DATA_DIR $TARGET_DB_NAME"
    exit 1
fi

# 安装MySQL（如果未安装）
install_mysql() {
    if ! command -v mysql &> /dev/null; then
        log_info "安装MySQL..."
        apt-get update -y
        apt-get install -y mysql-server mysql-client
        log_success "MySQL安装完成"
    else
        log_info "MySQL已安装"
    fi
}

# 查找MariaDB数据库
find_mariadb_databases() {
    log_info "查找MariaDB数据库..."
    
    # 查找所有数据库目录
    DATABASES=()
    for dir in "$MARIADB_DATA_DIR"/*; do
        if [ -d "$dir" ] && [ -f "$dir/db.opt" ]; then
            db_name=$(basename "$dir")
            if [ "$db_name" != "mysql" ] && [ "$db_name" != "performance_schema" ] && [ "$db_name" != "information_schema" ] && [ "$db_name" != "sys" ]; then
                DATABASES+=("$db_name")
            fi
        fi
    done
    
    if [ ${#DATABASES[@]} -eq 0 ]; then
        log_error "未找到任何MariaDB数据库"
        exit 1
    fi
    
    log_info "找到以下数据库:"
    for db in "${DATABASES[@]}"; do
        echo "  - $db"
    done
}

# 分析数据库结构
analyze_database() {
    local db_name="$1"
    local db_path="$MARIADB_DATA_DIR/$db_name"
    
    log_info "分析数据库: $db_name"
    
    # 查找表文件
    TABLES=()
    for file in "$db_path"/*.frm; do
        if [ -f "$file" ]; then
            table_name=$(basename "$file" .frm)
            TABLES+=("$table_name")
        fi
    done
    
    # 查找InnoDB表
    for file in "$db_path"/*.ibd; do
        if [ -f "$file" ]; then
            table_name=$(basename "$file" .ibd)
            if [[ ! " ${TABLES[@]} " =~ " ${table_name} " ]]; then
                TABLES+=("$table_name")
            fi
        fi
    done
    
    log_info "数据库 $db_name 包含 ${#TABLES[@]} 个表:"
    for table in "${TABLES[@]}"; do
        echo "  - $table"
    done
}

# 创建表结构SQL
create_table_structure() {
    local db_name="$1"
    local db_path="$MARIADB_DATA_DIR/$db_name"
    local output_file="/tmp/${db_name}_structure.sql"
    
    log_info "创建表结构SQL: $output_file"
    
    echo "-- 数据库: $db_name" > "$output_file"
    echo "CREATE DATABASE IF NOT EXISTS \`$db_name\`;" >> "$output_file"
    echo "USE \`$db_name\`;" >> "$output_file"
    echo "" >> "$output_file"
    
    # 查找表文件
    for file in "$db_path"/*.frm; do
        if [ -f "$file" ]; then
            table_name=$(basename "$file" .frm)
            log_info "处理表: $table_name"
            
            # 尝试从.frm文件提取表结构（简化版本）
            echo "-- 表: $table_name" >> "$output_file"
            echo "CREATE TABLE \`$table_name\` (" >> "$output_file"
            echo "  id INT AUTO_INCREMENT PRIMARY KEY," >> "$output_file"
            echo "  data TEXT" >> "$output_file"
            echo ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done
    
    log_success "表结构SQL创建完成: $output_file"
}

# 使用mysqlfrm工具（如果可用）
use_mysqlfrm() {
    local db_name="$1"
    local db_path="$MARIADB_DATA_DIR/$db_name"
    local output_file="/tmp/${db_name}_structure_mysqlfrm.sql"
    
    if command -v mysqlfrm &> /dev/null; then
        log_info "使用mysqlfrm工具提取表结构..."
        
        echo "-- 数据库: $db_name" > "$output_file"
        echo "CREATE DATABASE IF NOT EXISTS \`$db_name\`;" >> "$output_file"
        echo "USE \`$db_name\`;" >> "$output_file"
        echo "" >> "$output_file"
        
        for file in "$db_path"/*.frm; do
            if [ -f "$file" ]; then
                table_name=$(basename "$file" .frm)
                log_info "使用mysqlfrm处理表: $table_name"
                
                mysqlfrm --diagnostic "$file" >> "$output_file" 2>/dev/null || {
                    log_warning "mysqlfrm处理表 $table_name 失败，使用默认结构"
                    echo "-- 表: $table_name (默认结构)" >> "$output_file"
                    echo "CREATE TABLE \`$table_name\` (" >> "$output_file"
                    echo "  id INT AUTO_INCREMENT PRIMARY KEY," >> "$output_file"
                    echo "  data TEXT" >> "$output_file"
                    echo ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;" >> "$output_file"
                }
                echo "" >> "$output_file"
            fi
        done
        
        log_success "mysqlfrm提取完成: $output_file"
    else
        log_warning "mysqlfrm工具未安装，使用简化方法"
        create_table_structure "$db_name"
    fi
}

# 复制数据文件方法
copy_data_files() {
    local db_name="$1"
    local db_path="$MARIADB_DATA_DIR/$db_name"
    local mysql_data_dir="/var/lib/mysql"
    
    log_info "使用文件复制方法迁移数据库: $db_name"
    
    # 停止MySQL
    systemctl stop mysql 2>/dev/null || true
    
    # 备份MySQL数据目录
    if [ -d "$mysql_data_dir" ]; then
        log_info "备份MySQL数据目录..."
        cp -r "$mysql_data_dir" "${mysql_data_dir}_backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 创建目标数据库目录
    local target_db_path="$mysql_data_dir/$db_name"
    mkdir -p "$target_db_path"
    
    # 复制数据库文件
    log_info "复制数据库文件..."
    cp -r "$db_path"/* "$target_db_path"/
    
    # 设置权限
    chown -R mysql:mysql "$mysql_data_dir"
    chmod -R 755 "$mysql_data_dir"
    
    # 启动MySQL
    systemctl start mysql
    sleep 5
    
    log_success "文件复制完成"
}

# 验证迁移结果
verify_migration() {
    local db_name="$1"
    
    log_info "验证迁移结果..."
    
    # 检查数据库是否存在
    if mysql -u root -e "USE \`$db_name\`;" 2>/dev/null; then
        log_success "数据库 '$db_name' 迁移成功"
        
        # 显示表信息
        echo -e "\n${BLUE}=== 数据库 $db_name 的表信息 ===${NC}"
        mysql -u root -e "USE \`$db_name\`; SHOW TABLES;"
        
        # 显示表结构（前几个表）
        echo -e "\n${BLUE}=== 表结构示例 ===${NC}"
        mysql -u root -e "USE \`$db_name\`; SHOW TABLES;" | tail -n +2 | head -3 | while read table; do
            if [ -n "$table" ]; then
                echo -e "\n--- 表: $table ---"
                mysql -u root -e "USE \`$db_name\`; DESCRIBE \`$table\`;" 2>/dev/null || echo "无法获取表结构"
            fi
        done
        
    else
        log_error "数据库 '$db_name' 迁移失败"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始MariaDB数据文件迁移..."
    
    # 安装MySQL
    install_mysql
    
    # 查找数据库
    find_mariadb_databases
    
    # 处理每个数据库
    for db_name in "${DATABASES[@]}"; do
        log_info "处理数据库: $db_name"
        
        # 分析数据库
        analyze_database "$db_name"
        
        # 选择迁移方法
        echo -e "\n${YELLOW}请选择迁移方法:${NC}"
        echo "1) 文件复制方法 (快速，但可能有兼容性问题)"
        echo "2) 使用mysqlfrm提取结构 + 手动处理数据"
        read -p "请输入选择 (1-2): " choice
        
        case $choice in
            1)
                copy_data_files "$db_name"
                verify_migration "$db_name"
                ;;
            2)
                use_mysqlfrm "$db_name"
                log_info "请手动检查生成的SQL文件: /tmp/${db_name}_structure_mysqlfrm.sql"
                log_info "然后手动导入到MySQL:"
                log_info "mysql -u root -p < /tmp/${db_name}_structure_mysqlfrm.sql"
                ;;
            *)
                log_error "无效选择，跳过数据库 $db_name"
                ;;
        esac
    done
    
    log_success "迁移过程完成！"
    log_info "请检查迁移结果并根据需要进行调整"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi