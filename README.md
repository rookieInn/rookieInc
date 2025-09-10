# MariaDB到MySQL迁移工具包

本工具包提供了将MariaDB数据库迁移到MySQL的完整解决方案，特别适用于MariaDB服务无法启动的情况。

## 文件说明

### 主要脚本
- `mariadb_to_mysql_migration.sh` - 自动迁移脚本（包含测试数据）
- `migrate_existing_mariadb.sh` - 迁移现有MariaDB数据文件
- `example_usage.sh` - 使用示例和说明

### 文档
- `manual_migration_guide.md` - 详细的手动迁移指南
- `README.md` - 本说明文档

## 快速开始

### 方法1: 自动迁移（推荐用于测试）
```bash
sudo ./mariadb_to_mysql_migration.sh
```

### 方法2: 迁移现有数据文件
```bash
# 如果您的MariaDB数据目录在 /var/lib/mysql
sudo ./migrate_existing_mariadb.sh /var/lib/mysql my_database

# 如果您的MariaDB数据目录在其他位置
sudo ./migrate_existing_mariadb.sh /path/to/mariadb/data my_database
```

### 方法3: 手动迁移
```bash
# 1. 导出MariaDB数据
mysqldump -u root -p --all-databases > mariadb_export.sql

# 2. 启动MySQL
sudo systemctl start mysql

# 3. 导入数据
mysql -u root -p < mariadb_export.sql
```

## 迁移方法对比

| 方法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| mysqldump | 兼容性好，数据完整 | 需要MariaDB运行 | MariaDB可启动 |
| 文件复制 | 速度快，无需启动MariaDB | 可能有兼容性问题 | MariaDB无法启动 |
| Docker容器 | 隔离环境，易于测试 | 需要Docker | 测试环境 |

## 系统要求

- Ubuntu/Debian系统
- Root权限
- 足够的磁盘空间（至少是原数据库大小的2倍）

## 注意事项

1. **备份数据**: 迁移前务必备份原始数据
2. **版本兼容性**: 确保MariaDB和MySQL版本兼容
3. **字符集**: 检查并统一字符集设置
4. **权限**: 迁移后需要重新设置用户权限
5. **配置**: 根据新环境调整MySQL配置

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   sudo chown -R mysql:mysql /var/lib/mysql
   sudo chmod -R 755 /var/lib/mysql
   ```

2. **字符集问题**
   ```sql
   ALTER DATABASE database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **存储引擎问题**
   ```sql
   ALTER TABLE table_name ENGINE=InnoDB;
   ```

### 验证迁移结果

```bash
# 检查数据库
mysql -u root -p -e "SHOW DATABASES;"

# 检查表
mysql -u root -p -e "USE your_database; SHOW TABLES;"

# 检查数据
mysql -u root -p -e "USE your_database; SELECT COUNT(*) FROM your_table;"
```

## 性能优化

迁移完成后，建议进行以下优化：

1. **重建索引**
   ```sql
   OPTIMIZE TABLE table_name;
   ```

2. **调整MySQL配置**
   ```ini
   # /etc/mysql/mysql.conf.d/mysqld.cnf
   innodb_buffer_pool_size = 1G
   innodb_log_file_size = 256M
   max_connections = 200
   ```

3. **分析查询性能**
   ```sql
   ANALYZE TABLE table_name;
   ```

## 支持

如果遇到问题，请检查：
1. 系统日志: `journalctl -u mysql`
2. MySQL错误日志: `/var/log/mysql/error.log`
3. 数据目录权限
4. 磁盘空间

## 许可证

本工具包遵循MIT许可证。