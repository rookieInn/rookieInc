# 邮件附件收集脚本使用说明

`collect_email_attachments.py` 脚本用于从指定邮箱的收件箱中，按照设定的时间范围批量下载邮件附件到本地文件夹。脚本基于标准库 `imaplib`，无需额外依赖，可直接运行。

## 1. 环境准备

- Python 3.8 及以上版本
- 可访问目标邮箱的 IMAP 服务
- 已开启邮箱的 IMAP 权限（如 Gmail 需在后台开启 IMAP，并使用应用专用密码）

## 2. 常用命令示例

### 下载最近 7 天的附件（默认行为）
```bash
python3 collect_email_attachments.py \
  --imap-server imap.example.com \
  --username user@example.com \
  --ask-password \
  --output-dir ./attachments
```

### 指定起止日期（包含边界）
```bash
export MAIL_PASSWORD='your-app-password'

python3 collect_email_attachments.py \
  --imap-server imap.example.com \
  --username user@example.com \
  --password-env-var MAIL_PASSWORD \
  --since 2025-01-01 \
  --until 2025-01-31 \
  --output-dir ./attachments/january
```

### 仅预览将执行的操作
```bash
python3 collect_email_attachments.py \
  --imap-server imap.example.com \
  --username user@example.com \
  --ask-password \
  --output-dir ./attachments \
  --days 3 \
  --dry-run
```

## 3. 常用参数说明

| 参数 | 说明 |
| --- | --- |
| `--imap-server` | IMAP 服务器地址（必填） |
| `--imap-port` | IMAP 端口，默认 993 |
| `--username` | 邮箱账号（必填） |
| `--password` | 邮箱密码（不推荐直接使用） |
| `--password-env-var` | 保存密码的环境变量名 |
| `--ask-password` | 运行时交互输入密码 |
| `--output-dir` | 附件保存目录（必填，自动创建） |
| `--mailbox` | 邮箱文件夹，默认 `INBOX` |
| `--since` | 起始日期，格式 `YYYY-MM-DD` |
| `--until` | 结束日期，格式 `YYYY-MM-DD`，默认今天 |
| `--days` | 向前追溯天数。未指定起止日期时默认 7 天 |
| `--max-emails` | 限制处理的邮件数量，按时间倒序 |
| `--skip-existing` | 同名文件已存在时跳过保存 |
| `--dry-run` | 不写入文件，仅输出计划操作 |
| `--log-level` | 日志级别，默认 `INFO` |

> ⚠️ **安全建议**：优先使用 `--password-env-var` 或 `--ask-password`，避免在命令历史中暴露明文密码。

## 4. 输出文件策略

- 附件保存到 `--output-dir` 指定的文件夹。
- 文件名会自动清理非法字符。
- 若存在同名文件：
  - 加上 `--skip-existing` 将跳过保存；
  - 否则自动在文件名后追加序号，例如 `report.pdf`, `report_1.pdf`。

## 5. 故障排查

- **IMAP 登录失败**：确认服务器地址、端口、账号密码是否正确；确保已启用 IMAP。
- **未找到邮件**：调整日期范围或邮箱文件夹名称。
- **附件保存失败**：检查输出目录权限和磁盘空间；确认附件内容是否为空。
- **编码异常**：脚本会自动解码常见的 MIME 编码，如遇特殊编码可开启 `--log-level DEBUG` 以获取详细信息。

## 6. 建议的运行流程

1. 使用 `--dry-run` 预览即将下载的附件。
2. 去掉 `--dry-run`，确认输出目录空间充足后正式执行。
3. 如需定期执行，可将命令写入定时任务（crontab/systemd timer 等），并使用环境变量传递密码。

如需扩展功能（例如仅下载特定主题或发件人的邮件），可在脚本中添加额外的 IMAP 搜索条件。欢迎根据业务需求集成到现有自动化流程中。
