# MariaDB到MySQL迁移指南

## 概述
本指南提供了将MariaDB数据库迁移到MySQL的多种方法，特别适用于MariaDB服务无法启动的情况。

## 方法一：使用mysqldump（推荐）

### 1. 准备工作
```bash
# 安装必要的软件
sudo apt-get update
sudo apt-get install -y mariadb-client mysql-server

# 启动MariaDB（如果可能）
sudo systemctl start mariadb
```

### 2. 导出MariaDB数据
```bash
# 导出特定数据库
mysqldump -u root -p --single-transaction --routines --triggers database_name > mariadb_export.sql

# 导出所有数据库
mysqldump -u root -p --all-databases > mariadb_all_export.sql

# 只导出表结构
mysqldump -u root -p --no-data database_name > mariadb_structure.sql

# 只导出数据
mysqldump -u root -p --no-create-info database_name > mariadb_data.sql
```

### 3. 导入到MySQL
```bash
# 启动MySQL
sudo systemctl start mysql

# 创建数据库
mysql -u root -p -e "CREATE DATABASE database_name;"

# 导入数据
mysql -u root -p database_name < mariadb_export.sql
```

## 方法二：直接复制数据文件（高级）

### 1. 定位数据目录
```bash
# 查找MariaDB数据目录
find /var -name "mysql" -type d 2>/dev/null
# 通常位于: /var/lib/mysql

# 查找MySQL数据目录
mysql -u root -p -e "SHOW VARIABLES LIKE 'datadir';"
```

### 2. 停止服务
```bash
sudo systemctl stop mariadb
sudo systemctl stop mysql
```

### 3. 复制数据文件
```bash
# 备份MySQL数据目录
sudo cp -r /var/lib/mysql /var/lib/mysql_backup_$(date +%Y%m%d)

# 复制MariaDB数据文件
sudo cp -r /var/lib/mysql_mariadb/database_name /var/lib/mysql/

# 设置权限
sudo chown -R mysql:mysql /var/lib/mysql
sudo chmod -R 755 /var/lib/mysql
```

### 4. 启动MySQL
```bash
sudo systemctl start mysql
```

## 方法三：使用物理备份工具

### 1. 使用Percona XtraBackup
```bash
# 安装XtraBackup
wget https://repo.percona.com/apt/percona-release_latest.$(lsb_release -sc)_all.deb
sudo dpkg -i percona-release_latest.$(lsb_release -sc)_all.deb
sudo apt-get update
sudo apt-get install percona-xtrabackup-80

# 备份MariaDB
sudo innobackupex --user=root --password=your_password /backup/path/

# 恢复到MySQL
sudo innobackupex --copy-back /backup/path/backup_folder/
```

## 方法四：使用Docker容器

### 1. 创建MariaDB容器并挂载数据
```bash
# 启动MariaDB容器
docker run -d --name mariadb_temp \
  -v /path/to/mariadb/data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  mariadb:latest

# 导出数据
docker exec mariadb_temp mysqldump -u root -ppassword --all-databases > export.sql

# 停止容器
docker stop mariadb_temp
docker rm mariadb_temp
```

### 2. 导入到MySQL容器
```bash
# 启动MySQL容器
docker run -d --name mysql_target \
  -e MYSQL_ROOT_PASSWORD=password \
  mysql:latest

# 导入数据
docker exec -i mysql_target mysql -u root -ppassword < export.sql
```

## 验证迁移结果

### 1. 检查数据库和表
```sql
-- 连接到MySQL
mysql -u root -p

-- 查看所有数据库
SHOW DATABASES;

-- 选择迁移的数据库
USE database_name;

-- 查看表
SHOW TABLES;

-- 检查表结构
DESCRIBE table_name;

-- 检查数据
SELECT COUNT(*) FROM table_name;
```

### 2. 比较数据完整性
```bash
# 比较表结构
mysqldump -u root -p --no-data database_name > mysql_structure.sql
diff mariadb_structure.sql mysql_structure.sql

# 比较数据
mysqldump -u root -p --no-create-info database_name > mysql_data.sql
diff mariadb_data.sql mysql_data.sql
```

## 常见问题和解决方案

### 1. 字符集问题
```sql
-- 检查字符集
SHOW VARIABLES LIKE 'character_set%';

-- 修改字符集
ALTER DATABASE database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 存储引擎问题
```sql
-- 检查存储引擎
SHOW TABLE STATUS;

-- 转换存储引擎
ALTER TABLE table_name ENGINE=InnoDB;
```

### 3. 权限问题
```sql
-- 重新创建用户和权限
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
FLUSH PRIVILEGES;
```

## 性能优化建议

### 1. 调整MySQL配置
```ini
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
```

### 2. 重建索引
```sql
-- 重建所有表的索引
OPTIMIZE TABLE table_name;
```

## 备份策略

### 1. 迁移前备份
```bash
# 备份原始MariaDB数据
sudo tar -czf mariadb_backup_$(date +%Y%m%d).tar.gz /var/lib/mysql
```

### 2. 迁移后备份
```bash
# 备份迁移后的MySQL数据
sudo mysqldump -u root -p --all-databases > mysql_backup_$(date +%Y%m%d).sql
```

## 注意事项

1. **版本兼容性**: 确保MariaDB和MySQL版本兼容
2. **字符集**: 检查并统一字符集设置
3. **存储引擎**: 注意不同存储引擎的差异
4. **权限**: 重新设置用户权限
5. **配置**: 调整MySQL配置以适应新的工作负载
6. **测试**: 在生产环境迁移前进行充分测试