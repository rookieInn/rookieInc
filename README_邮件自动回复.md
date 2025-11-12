# 邮件关键字自动回复助手

该工具可以在收到指定关键字的邮件时自动回复预设内容，适用于售后支持、常见问题解答等场景。

## 功能概述

- **关键字匹配**：支持任意/全部关键字匹配，区分大小写可配置。
- **模板回复**：回复主题与内容可带占位符，例如`{original_subject}`、`{matched_keyword}`。
- **多语言支持**：正文匹配基于Unicode，适配中英文关键字。
- **自动避免重复**：使用本地存储记录已处理的邮件 UID。
- **定时轮询**：可持续运行，按照设定间隔轮询新邮件。

## 快速开始

1. 安装依赖（仅使用标准库，无需额外安装）。
2. 复制配置模板：

   ```bash
   cp email_auto_responder_config.example.json email_auto_responder_config.json
   ```

3. 填写邮箱服务器信息和关键字规则：

   - `imap.host` / `imap.port`：IMAP 服务地址与端口（通常为 993）。
   - `smtp.host` / `smtp.port`：SMTP 服务地址与端口（SSL 常用 465）。
   - `credentials.username`：邮箱账号。
   - `credentials.password`：建议填写 `$ENV{变量名}`，在运行前通过环境变量提供。
   - `keyword_rules`：关键字与回复模板配置。
   - `default_response`：未匹配到关键字时的默认回复（可选）。

4. 运行：

   ```bash
   export EMAIL_APP_PASSWORD=你的邮箱授权码
   python email_auto_responder.py --config email_auto_responder_config.json --loop --log-level INFO
   ```

   - `--loop` 开启持续轮询；如需仅执行一次，可使用 `--once`。
   - `--max-replies` 限制单次运行的最大回复数量。

## 配置说明

- **关键字规则 (`keyword_rules`)**
  - `name`：规则名称，便于日志追踪。
  - `keywords`：关键字列表，默认为任意匹配。
  - `match_all`：为 `true` 时，邮件需同时包含列表中的所有关键字。
  - `case_sensitive`：是否区分大小写。
  - `response.subject`：回复主题，支持占位符。
  - `response.body`：回复正文，支持占位符和多行文本。
  - `response.reply_to_all`：是否将原邮件里的抄送人加入回复。
  - `response.include_original_message`：是否附上原邮件正文。

- **默认回复 (`default_response`)**
  - 若未匹配到关键字且配置了默认回复，将发送该回复。

- **占位符**
  - `{original_subject}`：原邮件主题。
  - `{original_sender}`：发件人邮箱。
  - `{original_sender_name}`：发件人名称（可能为空）。
  - `{matched_keyword}`：触发的关键字。
  - `{rule_name}`：触发的规则名称。

- **已处理邮件存储 (`processed_store`)**
  - 默认文件为 `.auto_responder_processed.json`。
  - 可自定义路径，支持相对/绝对路径。

## 日志与监控

- 日志级别可通过 `--log-level` 调整（`DEBUG/INFO/WARNING/ERROR`）。
- 每次运行会记录匹配的规则和回复状态，便于排查问题。

## 测试

```bash
python -m unittest test_email_auto_responder.py
```

## 常见问题

1. **邮箱授权失败**  
   请确认使用的是邮箱的「客户端授权码」或「应用密码」，部分邮箱需在后台开启 IMAP/SMTP 服务。

2. **重复回复**  
   确认配置文件中的 `processed_store` 路径可写，脚本会将已回复的 UID 存储在该文件中。

3. **关键字未匹配**  
   建议在 `DEBUG` 日志级别下查看原始主题和正文，确认关键字是否正确、是否受大小写影响。

