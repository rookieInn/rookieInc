# Nginx访问日志分析工具

这是一个强大的nginx访问日志分析工具，可以统计各个URL的访问次数，并生成详细的分析报告。

## 功能特性

- 📊 **URL访问统计**: 统计各个URL的访问次数，找出最受欢迎的页面
- 📈 **状态码分析**: 分析HTTP状态码分布，了解请求成功率
- 🌐 **用户代理分析**: 统计访问者使用的浏览器和设备类型
- 🔗 **来源页面分析**: 分析访问者的来源页面
- 🖥️ **IP地址统计**: 统计访问者的IP地址分布
- ⏰ **时间分布分析**: 分析访问时间的小时和日期分布
- 📦 **响应大小统计**: 分析各个URL的响应大小
- 🔍 **HTTP方法统计**: 统计GET、POST等HTTP方法的使用情况

## 安装要求

- Python 3.6+
- 无需额外依赖包（使用标准库）

## 使用方法

### 基本用法

```bash
# 分析nginx访问日志
python3 nginx_log_analyzer.py /var/log/nginx/access.log

# 分析压缩的日志文件
python3 nginx_log_analyzer.py /var/log/nginx/access.log.1.gz

# 生成JSON格式的详细报告
python3 nginx_log_analyzer.py /var/log/nginx/access.log -o report.json

# 只显示前10个访问最多的URL
python3 nginx_log_analyzer.py /var/log/nginx/access.log --top-urls 10

# 静默模式，只输出简要信息
python3 nginx_log_analyzer.py /var/log/nginx/access.log --quiet
```

### 参数说明

- `log_file`: nginx访问日志文件路径（必需）
- `-o, --output`: 输出JSON格式的详细报告文件路径（可选）
- `--top-urls`: 显示前N个访问最多的URL（默认: 20）
- `--quiet`: 静默模式，只输出简要信息

## 支持的日志格式

工具支持标准的nginx访问日志格式：
```
$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
```

示例日志行：
```
192.168.1.100 - - [25/Dec/2023:10:30:45 +0800] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 输出报告

### 控制台输出

工具会在控制台显示简要的分析报告，包括：

- 总体统计信息（总请求数、唯一URL数、唯一IP数等）
- 访问次数最多的URL列表
- 状态码分布
- HTTP方法分布
- 小时访问分布
- 访问最多的IP地址
- 主要来源页面

### JSON报告

使用 `-o` 参数可以生成详细的JSON格式报告，包含所有统计数据：

```json
{
  "analysis_time": "2023-12-25T10:30:45.123456",
  "log_file": "/var/log/nginx/access.log",
  "summary": {
    "total_requests": 1000,
    "unique_urls": 50,
    "unique_ips": 100,
    "date_range": {
      "start": "2023-12-25",
      "end": "2023-12-25"
    }
  },
  "top_urls": [
    ["/index.html", 150],
    ["/products.html", 120],
    ["/about.html", 80]
  ],
  "status_codes": {
    "200": 950,
    "404": 30,
    "500": 20
  },
  "http_methods": {
    "GET": 980,
    "POST": 20
  },
  "top_user_agents": [...],
  "top_referers": [...],
  "top_ips": [...],
  "hourly_distribution": {...},
  "daily_distribution": {...},
  "response_size_stats": {...}
}
```

## 示例

### 分析示例日志

```bash
# 使用提供的示例日志文件
python3 nginx_log_analyzer.py sample_nginx_access.log
```

输出示例：
```
开始分析日志文件: sample_nginx_access.log
日志分析完成: 总行数 50, 成功解析 50 行

============================================================
NGINX访问日志分析报告
============================================================

📊 总体统计:
   总请求数: 50
   唯一URL数: 15
   唯一IP数: 41
   日期范围: 2023-12-25 到 2023-12-25

🔝 访问次数最多的URL (前20个):
    1. /index.html - 8 次
    2. /products.html - 8 次
    3. /about.html - 6 次
    4. /contact.html - 6 次
    5. /css/style.css - 4 次
    6. /js/app.js - 4 次
    7. /images/logo.png - 3 次
    8. /images/banner.jpg - 3 次
    9. /api/users - 3 次
   10. /api/products - 2 次
   11. /api/status - 1 次
   12. /api/health - 1 次
   13. /robots.txt - 1 次
   14. /sitemap.xml - 1 次
   15. /admin/login - 1 次

📈 状态码分布:
   200: 48 次
   404: 1 次
   401: 1 次

🌐 HTTP方法分布:
   GET: 50 次

⏰ 小时访问分布 (前10个):
   10:00 - 25 次
   11:00 - 25 次

🖥️  访问最多的IP (前10个):
    1. 192.168.1.100 - 4 次
    2. 192.168.1.101 - 3 次
    3. 192.168.1.102 - 3 次
    4. 192.168.1.103 - 2 次
    5. 192.168.1.104 - 1 次
    6. 192.168.1.105 - 1 次
    7. 192.168.1.106 - 1 次
    8. 192.168.1.107 - 1 次
    9. 192.168.1.108 - 1 次
   10. 192.168.1.109 - 1 次

🔗 主要来源页面 (前10个):
    1. http://example.com/index.html - 15 次
    2. http://example.com/about.html - 4 次
    3. http://example.com/products.html - 3 次

✅ 分析完成!
```

### 生成详细报告

```bash
# 生成JSON格式的详细报告
python3 nginx_log_analyzer.py sample_nginx_access.log -o detailed_report.json
```

## 常见问题

### Q: 如何处理大型日志文件？
A: 工具已经优化了内存使用，可以处理大型日志文件。对于非常大的文件，建议使用 `--quiet` 参数减少输出。

### Q: 支持哪些日志格式？
A: 目前支持标准的nginx访问日志格式。如果您的日志格式不同，可能需要修改代码中的正则表达式。

### Q: 如何处理压缩的日志文件？
A: 工具自动检测 `.gz` 扩展名并解压缩文件。

### Q: 可以分析多个日志文件吗？
A: 目前工具一次只能分析一个文件。如果需要分析多个文件，可以先将它们合并或分别分析。

## 技术细节

- 使用Python标准库，无需额外依赖
- 支持gzip压缩的日志文件
- 使用正则表达式解析日志格式
- 内存优化的计数器实现
- 支持大文件处理

## 许可证

MIT License