# 微信群ChatGPT-4机器人使用说明

## 🤖 项目简介

这是一个功能强大的微信群机器人，可以对接ChatGPT-4 API，支持智能对话、图片识别、语音处理等多种功能。

## ✨ 功能特点

### 基础版本 (`wechat_chatgpt_bot.py`)
- 🤖 智能文字对话
- 💬 群聊和私聊支持
- 📝 对话历史记录
- ⚙️ 简单配置管理

### 高级版本 (`wechat_bot_advanced.py`)
- 🎯 所有基础功能
- 🖼️ 图片内容识别
- 🎤 语音转文字（开发中）
- 📊 用户使用统计
- 🔧 群组管理功能
- ⏰ 定时任务支持
- 🎛️ 丰富的命令系统

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑配置文件 `bot_config.ini` 或 `bot_config_advanced.ini`：

```ini
[OPENAI]
api_key = your_openai_api_key_here  # 替换为您的OpenAI API密钥
model = gpt-4
max_tokens = 1000
temperature = 0.7
```

### 3. 获取OpenAI API密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录您的账户
3. 创建新的API密钥
4. 将密钥复制到配置文件中

### 4. 运行机器人

#### 基础版本
```bash
python wechat_chatgpt_bot.py
```

#### 高级版本
```bash
python wechat_bot_advanced.py
```

### 5. 微信登录

运行程序后，会弹出二维码，使用微信扫描登录。

## 📋 配置说明

### 基础配置 (`bot_config.ini`)

```ini
[OPENAI]
api_key = your_openai_api_key_here  # OpenAI API密钥
model = gpt-4                       # 使用的模型
max_tokens = 1000                   # 最大回复长度
temperature = 0.7                   # 回复随机性

[WECHAT]
auto_reply = true                   # 是否启用自动回复
reply_groups = true                 # 是否回复群聊
reply_private = true                # 是否回复私聊
admin_users = your_wechat_id        # 管理员用户ID

[BOT]
name = ChatGPT助手                  # 机器人名称
welcome_message = 你好！...         # 欢迎消息
error_message = 抱歉，我现在...     # 错误消息
```

### 高级配置 (`bot_config_advanced.ini`)

包含所有基础配置，额外增加：

```ini
[OPENAI]
enable_vision = true                # 启用图片识别
enable_voice = true                 # 启用语音处理

[WECHAT]
enable_image_recognition = true     # 启用图片识别
enable_voice_recognition = true     # 启用语音识别
enable_group_management = true      # 启用群组管理

[FEATURES]
enable_weather = false              # 天气功能
weather_api_key = your_key          # 天气API密钥
enable_news = false                 # 新闻功能
news_api_key = your_key             # 新闻API密钥
enable_translation = true           # 翻译功能
enable_sentiment = true             # 情感分析
```

## 🎮 使用方法

### 基础对话
- 直接发送文字消息给机器人
- 在群聊中@机器人 + 消息内容

### 图片识别（高级版本）
- 发送图片给机器人
- 机器人会自动识别图片内容并回复

### 命令系统（高级版本）

| 命令 | 功能 | 示例 |
|------|------|------|
| `/help` | 查看帮助信息 | `/help` |
| `/stats` | 查看使用统计 | `/stats` |
| `/clear` | 清除对话历史 | `/clear` |
| `/weather` | 查询天气 | `/weather 北京` |
| `/translate` | 翻译文本 | `/translate hello` |
| `/sentiment` | 情感分析 | `/sentiment 今天心情很好` |
| `/admin` | 管理员面板 | `/admin` |

## 🔧 高级功能

### 1. 图片识别
- 支持多种图片格式
- 自动分析图片内容
- 提供详细描述

### 2. 用户统计
- 记录用户使用次数
- 统计活跃时间
- 生成使用报告

### 3. 群组管理
- 支持多群组管理
- 独立的群组设置
- 管理员权限控制

### 4. 定时任务
- 自动清理过期数据
- 定期保存统计信息
- 可扩展的定时功能

## 🛠️ 开发说明

### 项目结构
```
/workspace/
├── wechat_chatgpt_bot.py          # 基础版本机器人
├── wechat_bot_advanced.py         # 高级版本机器人
├── bot_config.ini                 # 基础配置文件
├── bot_config_advanced.ini        # 高级配置文件
├── requirements.txt               # 依赖包列表
├── 微信群ChatGPT机器人使用说明.md  # 使用说明
└── *.log                         # 日志文件
```

### 扩展开发

1. **添加新命令**：
   ```python
   def _handle_new_command(self, user_id: str) -> str:
       return "新命令的回复"
   
   # 在 _setup_commands 中注册
   self.commands['/new'] = self._handle_new_command
   ```

2. **添加新功能**：
   ```python
   async def _new_feature(self, message: str) -> str:
       # 实现新功能
       return "功能结果"
   ```

3. **自定义配置**：
   在配置文件中添加新的配置项，并在代码中读取使用。

## ⚠️ 注意事项

1. **API限制**：
   - OpenAI API有使用限制和费用
   - 建议设置合理的max_tokens值
   - 监控API使用量

2. **微信限制**：
   - 避免频繁发送消息
   - 遵守微信使用规范
   - 注意群聊管理规则

3. **隐私安全**：
   - 妥善保管API密钥
   - 定期清理聊天记录
   - 注意用户隐私保护

4. **服务器要求**：
   - 稳定的网络连接
   - 足够的存储空间
   - 定期备份数据

## 🐛 常见问题

### Q: 机器人不回复消息？
A: 检查以下几点：
- 配置文件中的API密钥是否正确
- 是否启用了自动回复功能
- 网络连接是否正常
- 查看日志文件中的错误信息

### Q: 图片识别不工作？
A: 确保：
- 配置文件中启用了图片识别功能
- OpenAI API支持Vision功能
- 图片格式正确且大小合适

### Q: 如何查看机器人状态？
A: 使用 `/admin` 命令（需要管理员权限）或查看日志文件。

### Q: 如何停止机器人？
A: 在终端中按 `Ctrl+C` 停止程序。

## 📞 技术支持

如果遇到问题，请：
1. 查看日志文件
2. 检查配置文件
3. 确认网络连接
4. 验证API密钥

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台规则。

---

**祝您使用愉快！** 🎉