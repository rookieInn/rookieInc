# SQL查询结果推送到腾讯文档

这是一个Python脚本，用于执行多条SQL查询并将结果汇总推送到腾讯文档。

## 功能特性

- 🔗 支持多种数据库连接（MySQL、PostgreSQL、Oracle等）
- 📊 执行多条SQL查询并自动汇总
- 📋 将查询结果格式化为表格
- 📤 自动推送到腾讯文档
- ⚙️ 灵活的配置管理
- 📝 详细的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 数据库配置

编辑 `config.ini` 文件中的数据库配置：

```ini
[database]
host = localhost
port = 3306
user = your_username
password = your_password
database = your_database
```

### 2. 腾讯文档配置

#### 获取Access Token

1. 访问 [腾讯文档开放平台](https://docs.qq.com/openapi/getAccessToken)
2. 按照指引获取你的Access Token
3. 将Token配置到 `config.ini`：

```ini
[tencent_docs]
access_token = your_access_token
file_id = your_file_id
```

#### 获取文件ID

从腾讯文档的URL中获取文件ID：
```
https://docs.qq.com/sheet/DTWJxQ0FUVVJqS0lD?tab=000001
```
文件ID就是 `DTWJxQ0FUVVJqS0lD`

## 使用方法

### 基本使用

```python
from sql_to_tencent_docs import SQLToTencentDocs

# 定义SQL查询
sql_queries = [
    {
        "name": "用户统计",
        "sql": "SELECT COUNT(*) as 用户总数 FROM users"
    },
    {
        "name": "订单统计", 
        "sql": "SELECT status, COUNT(*) as 数量 FROM orders GROUP BY status"
    }
]

# 创建处理器并运行
processor = SQLToTencentDocs('config.ini')
processor.run(sql_queries, "每日数据汇总")
```

### 高级使用

```python
# 自定义查询示例
custom_queries = [
    {
        "name": "销售分析",
        "sql": """
            SELECT 
                DATE(created_at) as 日期,
                COUNT(*) as 订单数,
                SUM(amount) as 总收入
            FROM orders 
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY 日期 DESC
        """
    }
]

processor = SQLToTencentDocs('config.ini')
success = processor.run(custom_queries, "销售数据分析")

if success:
    print("数据推送成功！")
else:
    print("推送失败，请检查日志")
```

## 文件结构

```
.
├── sql_to_tencent_docs.py    # 主脚本文件
├── config.ini                # 配置文件
├── requirements.txt          # 依赖文件
├── example_usage.py          # 使用示例
├── README_sql_to_docs.md     # 说明文档
└── sql_to_docs.log          # 日志文件（运行后生成）
```

## 支持的数据库

- ✅ MySQL (使用 pymysql)
- ✅ PostgreSQL (使用 psycopg2-binary)
- ✅ Oracle (使用 cx_Oracle)
- ✅ SQLite (使用 sqlite3，Python内置)

## 配置示例

### MySQL配置
```ini
[database]
host = localhost
port = 3306
user = root
password = your_password
database = your_database
```

### PostgreSQL配置
```ini
[database]
host = localhost
port = 5432
user = postgres
password = your_password
database = your_database
```

## 注意事项

1. **权限要求**：确保数据库用户有执行查询的权限
2. **腾讯文档API**：需要有效的Access Token和文件ID
3. **数据量限制**：腾讯文档对单次写入的数据量有限制
4. **网络连接**：确保服务器能访问腾讯文档API

## 错误排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置信息
   - 确认数据库服务是否运行
   - 验证用户权限

2. **腾讯文档推送失败**
   - 检查Access Token是否有效
   - 确认文件ID是否正确
   - 检查网络连接

3. **SQL查询错误**
   - 检查SQL语法
   - 确认表名和字段名正确
   - 查看日志文件获取详细错误信息

### 日志查看

```bash
tail -f sql_to_docs.log
```

## 扩展功能

### 添加新的数据库支持

```python
# 在 connect_database 方法中添加新的数据库类型
if db_type == 'postgresql':
    import psycopg2
    self.db_connection = psycopg2.connect(...)
```

### 自定义数据格式化

```python
def custom_format_data(self, df):
    # 自定义数据格式化逻辑
    return formatted_data
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！