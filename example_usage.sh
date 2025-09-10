#!/bin/bash

# MariaDB到MySQL迁移使用示例

echo "=== MariaDB到MySQL迁移工具使用示例 ==="
echo ""

echo "1. 自动迁移脚本（推荐用于测试环境）:"
echo "   sudo chmod +x mariadb_to_mysql_migration.sh"
echo "   sudo ./mariadb_to_mysql_migration.sh"
echo ""

echo "2. 迁移现有MariaDB数据文件:"
echo "   sudo chmod +x migrate_existing_mariadb.sh"
echo "   sudo ./migrate_existing_mariadb.sh /var/lib/mysql my_database"
echo ""

echo "3. 手动迁移步骤:"
echo "   # 步骤1: 导出MariaDB数据"
echo "   mysqldump -u root -p --all-databases > mariadb_export.sql"
echo ""
echo "   # 步骤2: 启动MySQL"
echo "   sudo systemctl start mysql"
echo ""
echo "   # 步骤3: 导入数据"
echo "   mysql -u root -p < mariadb_export.sql"
echo ""

echo "4. 验证迁移结果:"
echo "   mysql -u root -p -e \"SHOW DATABASES;\""
echo "   mysql -u root -p -e \"USE your_database; SHOW TABLES;\""
echo ""

echo "5. 查看详细迁移指南:"
echo "   cat manual_migration_guide.md"
echo ""

echo "=== 注意事项 ==="
echo "- 确保在迁移前备份原始数据"
echo "- 检查字符集和存储引擎兼容性"
echo "- 验证数据完整性"
echo "- 调整MySQL配置以适应新的工作负载"