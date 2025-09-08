# 微信群ChatGPT-4机器人

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能强大的微信群机器人，集成ChatGPT-4 API，支持智能对话、图片识别、语音处理等多种功能。

## 🌟 功能特点

### 基础功能
- 🤖 **智能对话**: 基于ChatGPT-4的自然语言处理
- 💬 **多场景支持**: 群聊和私聊自动回复
- 📝 **对话历史**: 智能记忆用户对话上下文
- ⚙️ **灵活配置**: 简单易用的配置文件管理

### 高级功能
- 🖼️ **图片识别**: 自动分析图片内容并生成描述
- 🎤 **语音处理**: 语音转文字功能（开发中）
- 📊 **用户统计**: 详细的使用数据和分析
- 🔧 **群组管理**: 多群组独立管理
- ⏰ **定时任务**: 自动数据清理和统计
- 🎛️ **命令系统**: 丰富的交互命令

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd wechat-chatgpt-bot

# 运行启动脚本
./start_bot.sh
```

### 方法二：手动安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API密钥
# 编辑 bot_config.ini 或 bot_config_advanced.ini
# 将 your_openai_api_key_here 替换为您的OpenAI API密钥

# 3. 运行机器人
python wechat_chatgpt_bot.py          # 基础版本
# 或
python wechat_bot_advanced.py         # 高级版本
```

### 方法三：Docker部署

```bash
# 1. 设置环境变量
export OPENAI_API_KEY="your_openai_api_key_here"

# 2. 启动容器
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

## 📋 配置说明

### 获取OpenAI API密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录您的账户
3. 创建新的API密钥
4. 复制密钥到配置文件中

### 配置文件

#### 基础配置 (`bot_config.ini`)
```ini
[OPENAI]
api_key = your_openai_api_key_here
model = gpt-4
max_tokens = 1000
temperature = 0.7

[WECHAT]
auto_reply = true
reply_groups = true
reply_private = true
admin_users = your_wechat_id

[BOT]
name = ChatGPT助手
welcome_message = 你好！我是ChatGPT助手
error_message = 抱歉，我现在无法回复
```

#### 高级配置 (`bot_config_advanced.ini`)
包含所有基础配置，额外支持：
- 图片识别功能
- 语音处理功能
- 群组管理功能
- 扩展功能配置

## 🎮 使用方法

### 基础对话
- 直接发送文字消息
- 群聊中@机器人 + 消息内容

### 图片识别（高级版本）
- 发送图片给机器人
- 自动识别并描述图片内容

### 命令系统（高级版本）

| 命令 | 功能 | 示例 |
|------|------|------|
| `/help` | 查看帮助 | `/help` |
| `/stats` | 使用统计 | `/stats` |
| `/clear` | 清除历史 | `/clear` |
| `/weather` | 查询天气 | `/weather 北京` |
| `/translate` | 翻译文本 | `/translate hello` |
| `/sentiment` | 情感分析 | `/sentiment 今天心情很好` |
| `/admin` | 管理员面板 | `/admin` |

## 🛠️ 开发指南

### 项目结构
```
├── wechat_chatgpt_bot.py          # 基础版本机器人
├── wechat_bot_advanced.py         # 高级版本机器人
├── bot_config.ini                 # 基础配置文件
├── bot_config_advanced.ini        # 高级配置文件
├── requirements.txt               # 依赖包列表
├── start_bot.sh                   # 启动脚本
├── docker-compose.yml             # Docker配置
├── Dockerfile                     # Docker镜像
├── 微信群ChatGPT机器人使用说明.md  # 详细使用说明
└── README_微信群机器人.md          # 项目说明
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

## 📊 功能对比

| 功能 | 基础版本 | 高级版本 |
|------|----------|----------|
| 文字对话 | ✅ | ✅ |
| 群聊支持 | ✅ | ✅ |
| 私聊支持 | ✅ | ✅ |
| 对话历史 | ✅ | ✅ |
| 图片识别 | ❌ | ✅ |
| 语音处理 | ❌ | ✅ |
| 用户统计 | ❌ | ✅ |
| 群组管理 | ❌ | ✅ |
| 定时任务 | ❌ | ✅ |
| 命令系统 | ❌ | ✅ |

## ⚠️ 注意事项

1. **API限制**: OpenAI API有使用限制和费用，请合理使用
2. **微信规范**: 遵守微信使用规范，避免频繁发送消息
3. **隐私保护**: 妥善保管API密钥，注意用户隐私
4. **服务器要求**: 需要稳定的网络连接和足够的存储空间

## 🐛 故障排除

### 常见问题

**Q: 机器人不回复消息？**
A: 检查API密钥配置、网络连接和日志文件

**Q: 图片识别不工作？**
A: 确保启用了图片识别功能且API支持Vision

**Q: 如何查看机器人状态？**
A: 使用 `/admin` 命令或查看日志文件

## 📈 更新日志

### v1.0.0
- 基础版本机器人发布
- 支持文字对话和群聊功能

### v2.0.0
- 高级版本机器人发布
- 新增图片识别、用户统计等功能
- 完善命令系统和群组管理

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 邮箱: [your-email@example.com]

---

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**