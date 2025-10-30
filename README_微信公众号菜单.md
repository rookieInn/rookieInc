# 微信公众号自定义菜单管理系统

## 📖 简介

这是一个完整的微信公众号自定义菜单管理系统，支持创建多级菜单，并能在用户点击菜单时返回图片、视频、音频等多媒体内容。

## ✨ 功能特点

- ✅ **多级菜单支持**：支持最多3个一级菜单，每个一级菜单最多5个子菜单
- 📸 **图片响应**：点击菜单返回图片
- 🎬 **视频响应**：点击菜单返回视频
- 🎵 **音频响应**：点击菜单返回音频
- 📰 **图文消息**：支持图文混排的消息推送
- 🔄 **自动Token管理**：自动获取和刷新access_token
- 🛠️ **完整示例**：提供多个实用示例
- 📝 **详细日志**：完整的操作日志记录

## 📁 文件说明

```
微信公众号菜单系统/
├── wechat_official_menu.py              # 菜单管理核心模块
├── wechat_official_server.py            # 消息响应服务器
├── wechat_official_example.py           # 使用示例
├── wechat_official_account_config.ini   # 配置文件
├── wechat_official_requirements.txt     # 依赖包列表
├── start_wechat_official.sh             # 快速启动脚本
└── media/                                # 媒体文件目录
    ├── images/                           # 图片文件
    ├── videos/                           # 视频文件
    └── audios/                           # 音频文件
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- 微信公众号（已认证或测试号）
- 公网可访问的服务器（用于接收微信消息）

### 2. 安装依赖

```bash
pip install -r wechat_official_requirements.txt
```

或使用国内镜像加速：

```bash
pip install -r wechat_official_requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置公众号信息

编辑 `wechat_official_account_config.ini` 文件：

```ini
[WECHAT_OFFICIAL]
# 在微信公众平台获取: https://mp.weixin.qq.com/
appid = your_appid_here
appsecret = your_appsecret_here
token = your_token_here
encoding_aes_key = your_encoding_aes_key_here

[SERVER]
host = 0.0.0.0
port = 8080
debug = false

[MEDIA]
image_path = ./media/images
video_path = ./media/videos
audio_path = ./media/audios
```

### 4. 获取公众号信息

#### 方式一：正式公众号

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" -> "基本配置"
3. 获取 AppID 和 AppSecret
4. 设置服务器配置中的 Token

#### 方式二：测试公众号（推荐开发使用）

1. 访问 [微信公众平台测试账号](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 扫码登录获取测试号
3. 获取 appID 和 appsecret
4. 配置接口信息中的 Token

### 5. 创建菜单

#### 使用快速启动脚本（推荐）

```bash
./start_wechat_official.sh
```

然后选择对应的功能选项。

#### 使用Python直接运行

```bash
# 创建示例菜单
python3 wechat_official_menu.py

# 运行完整示例
python3 wechat_official_example.py

# 启动消息响应服务器
python3 wechat_official_server.py
```

### 6. 配置服务器地址

在微信公众平台配置服务器地址：

1. 进入"开发" -> "基本配置"
2. 服务器配置：
   - URL: `http://your-domain:8080/wechat`
   - Token: 与配置文件中的token一致
   - EncodingAESKey: 与配置文件中的encoding_aes_key一致
   - 消息加解密方式: 明文模式（或安全模式）

## 📚 使用教程

### 创建简单菜单

```python
from wechat_official_menu import WeChatOfficialMenuManager

# 初始化管理器
manager = WeChatOfficialMenuManager()

# 定义菜单
menu_data = {
    "button": [
        {
            "type": "click",
            "name": "点击按钮",
            "key": "BUTTON_CLICK"
        },
        {
            "type": "view",
            "name": "访问网页",
            "url": "https://www.example.com"
        }
    ]
}

# 创建菜单
if manager.create_menu(menu_data):
    print("菜单创建成功！")
```

### 创建多级菜单

```python
menu_data = {
    "button": [
        {
            "name": "多媒体",
            "sub_button": [
                {
                    "type": "click",
                    "name": "查看图片",
                    "key": "VIEW_IMAGE"
                },
                {
                    "type": "click",
                    "name": "观看视频",
                    "key": "VIEW_VIDEO"
                },
                {
                    "type": "click",
                    "name": "听音频",
                    "key": "VIEW_AUDIO"
                }
            ]
        },
        {
            "type": "click",
            "name": "关于我们",
            "key": "ABOUT_US"
        }
    ]
}

manager.create_menu(menu_data)
```

### 上传媒体文件

```python
# 上传图片
image_path = "./media/images/sample.jpg"
media_id = manager.upload_media(image_path, 'image')
print(f"图片Media ID: {media_id}")

# 上传视频
video_path = "./media/videos/sample.mp4"
media_id = manager.upload_media(video_path, 'video')
print(f"视频Media ID: {media_id}")

# 上传音频
audio_path = "./media/audios/sample.mp3"
media_id = manager.upload_media(audio_path, 'voice')
print(f"音频Media ID: {media_id}")
```

### 查询和删除菜单

```python
# 查询当前菜单
menu = manager.get_menu()
if menu:
    print("当前菜单:", menu)

# 删除菜单
if manager.delete_menu():
    print("菜单已删除")
```

## 🎯 菜单类型说明

### 一级菜单类型

1. **click** - 点击推事件
   - 用户点击后，微信服务器推送事件到您的服务器
   - 需要配置 `key` 参数

2. **view** - 跳转URL
   - 用户点击后直接跳转到指定网页
   - 需要配置 `url` 参数

3. **sub_button** - 子菜单
   - 包含多个子菜单项
   - 最多5个子菜单

### 菜单限制

- 一级菜单：最多 **3个**
- 二级菜单：每个一级菜单最多 **5个** 子菜单
- 菜单名称：最多 **16个字节**（中文约5个字）

## 🎨 响应消息类型

系统支持以下消息响应类型：

### 1. 文本消息

```python
def handle_menu_click(event_key, to_user, from_user):
    if event_key == "ABOUT":
        return build_text_response(
            to_user,
            from_user,
            "欢迎关注我们！这是关于我们的信息..."
        )
```

### 2. 图片消息

```python
# 需要先上传图片获取media_id
media_id = manager.upload_media("image.jpg", "image")
return build_image_response(to_user, from_user, media_id)
```

### 3. 视频消息

```python
media_id = manager.upload_media("video.mp4", "video")
return build_video_response(
    to_user,
    from_user,
    media_id,
    title="精彩视频",
    description="视频描述"
)
```

### 4. 音频消息

```python
media_id = manager.upload_media("audio.mp3", "voice")
return build_voice_response(to_user, from_user, media_id)
```

### 5. 图文消息

```python
articles = [
    {
        "title": "文章标题",
        "description": "文章描述",
        "pic_url": "https://example.com/pic.jpg",
        "url": "https://example.com/article"
    }
]
return build_news_response(to_user, from_user, articles)
```

## 🔧 自定义响应处理

在 `wechat_official_server.py` 中的 `handle_menu_click` 函数中添加您的自定义处理：

```python
def handle_menu_click(event_key, to_user, from_user):
    # 添加您的自定义菜单KEY处理
    if event_key == "YOUR_CUSTOM_KEY":
        # 返回图片
        media_id = "your_media_id"
        return build_image_response(to_user, from_user, media_id)
    
    elif event_key == "ANOTHER_KEY":
        # 返回文本
        return build_text_response(
            to_user,
            from_user,
            "这是自定义的响应内容"
        )
```

## 📝 媒体文件格式要求

### 图片
- 格式：jpg/png
- 大小：不超过2MB
- 分辨率：建议800x600或更高

### 视频
- 格式：mp4
- 大小：不超过10MB
- 时长：建议不超过3分钟

### 音频
- 格式：mp3/amr
- 大小：不超过2MB
- 时长：建议不超过60秒

## 🌐 生产环境部署

### 使用Gunicorn部署

```bash
# 安装gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:8080 wechat_official_server:app
```

### 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /wechat {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用Supervisor进程管理

```ini
[program:wechat_official]
command=/usr/bin/python3 /path/to/wechat_official_server.py
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/wechat_official.log
```

## ❓ 常见问题

### Q1: 菜单不显示怎么办？

A: 
1. 检查菜单是否创建成功（查看日志）
2. 取消关注后重新关注公众号
3. 菜单生效可能需要24小时
4. 确认是否在正确的公众号下创建

### Q2: 点击菜单没有响应？

A:
1. 检查服务器是否正常运行
2. 确认服务器地址配置正确
3. 查看服务器日志是否收到请求
4. 确认Token配置一致

### Q3: 媒体文件上传失败？

A:
1. 检查文件格式和大小是否符合要求
2. 确认access_token是否有效
3. 查看详细错误日志
4. 确认公众号权限（测试号可能有限制）

### Q4: access_token获取失败？

A:
1. 检查AppID和AppSecret是否正确
2. 确认网络连接正常
3. 检查IP白名单设置
4. 查看微信公众平台是否有异常提示

## 📊 日志说明

系统会生成以下日志文件：

- `wechat_official_menu.log` - 菜单管理操作日志
- `wechat_official_server.log` - 服务器运行日志

日志级别：INFO, WARNING, ERROR

## 🔐 安全建议

1. ✅ 不要将AppID和AppSecret提交到公开仓库
2. ✅ 使用环境变量或配置文件管理敏感信息
3. ✅ 定期更换Token和AppSecret
4. ✅ 使用HTTPS加密通信
5. ✅ 验证请求来源（签名校验）
6. ✅ 限制API调用频率

## 📖 API参考

### 微信公众平台API文档

- [自定义菜单](https://developers.weixin.qq.com/doc/offiaccount/Custom_Menus/Creating_Custom-Defined_Menu.html)
- [素材管理](https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/New_temporary_materials.html)
- [消息管理](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Receiving_standard_messages.html)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 💡 提示

1. 开发阶段建议使用**测试公众号**，避免影响正式公众号
2. 媒体文件建议使用CDN托管，提高加载速度
3. 定期备份菜单配置
4. 监控服务器日志，及时发现问题
5. 关注微信公众平台的API更新

## 📞 支持

如有问题，请查看：
- 微信公众平台开发文档
- GitHub Issues
- 项目日志文件

---

**祝您使用愉快！** 🎉
