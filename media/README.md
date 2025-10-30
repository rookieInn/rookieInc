# 媒体文件目录

## 📁 目录说明

本目录用于存放微信公众号菜单响应的媒体文件。

### 目录结构

```
media/
├── images/          # 图片文件
│   └── sample_image_1.jpg
├── videos/          # 视频文件
│   └── sample_video_1.mp4
└── audios/          # 音频文件
    └── sample_audio_1.mp3
```

## 📝 文件命名规范

为了方便管理，建议使用以下命名规范：

### 图片文件
- 格式：`sample_image_N.jpg` 或 `category_name_N.jpg`
- 示例：
  - `sample_image_1.jpg`
  - `product_banner_1.jpg`
  - `promotion_poster_1.jpg`

### 视频文件
- 格式：`sample_video_N.mp4` 或 `category_name_N.mp4`
- 示例：
  - `sample_video_1.mp4`
  - `product_intro_1.mp4`
  - `tutorial_guide_1.mp4`

### 音频文件
- 格式：`sample_audio_N.mp3` 或 `category_name_N.mp3`
- 示例：
  - `sample_audio_1.mp3`
  - `welcome_voice_1.mp3`
  - `bgm_music_1.mp3`

## 📋 文件要求

### 图片
- **格式**：JPG, PNG
- **大小**：不超过 2MB
- **尺寸**：建议 800x600 或更高
- **用途**：菜单点击响应、图文消息封面

### 视频
- **格式**：MP4
- **大小**：不超过 10MB
- **时长**：建议不超过 3 分钟
- **编码**：H.264
- **用途**：产品介绍、教程视频

### 音频
- **格式**：MP3, AMR
- **大小**：不超过 2MB
- **时长**：建议不超过 60 秒
- **比特率**：建议 128kbps
- **用途**：语音消息、背景音乐

## 🎯 使用方法

### 1. 准备媒体文件

将您的媒体文件放置到对应的目录中：

```bash
# 复制图片
cp your_image.jpg media/images/sample_image_1.jpg

# 复制视频
cp your_video.mp4 media/videos/sample_video_1.mp4

# 复制音频
cp your_audio.mp3 media/audios/sample_audio_1.mp3
```

### 2. 上传到微信服务器

使用菜单管理器上传：

```python
from wechat_official_menu import WeChatOfficialMenuManager

manager = WeChatOfficialMenuManager()

# 上传图片
image_media_id = manager.upload_media('./media/images/sample_image_1.jpg', 'image')

# 上传视频
video_media_id = manager.upload_media('./media/videos/sample_video_1.mp4', 'video')

# 上传音频
audio_media_id = manager.upload_media('./media/audios/sample_audio_1.mp3', 'voice')
```

### 3. 在服务器中使用

在 `wechat_official_server.py` 的 `handle_menu_click` 函数中使用 media_id：

```python
def handle_menu_click(event_key, to_user, from_user):
    if event_key == "YOUR_MENU_KEY":
        # 使用上传后获得的media_id
        return build_image_response(to_user, from_user, image_media_id)
```

## 💡 提示

1. **素材有效期**：临时素材3天有效，永久素材无时间限制
2. **数量限制**：永久素材有数量限制（免费账号图文消息5000条，其他类型100000个）
3. **建议做法**：
   - 将 media_id 缓存起来，避免重复上传
   - 定期检查素材是否过期
   - 使用 CDN 托管大文件，公众号只推送链接

## 🔄 素材管理

### 查看已上传的素材

```python
# 可以通过微信公众平台查看
# 或使用API查询素材列表
```

### 删除素材

```python
# 使用微信公众平台的素材管理功能
# 或调用删除素材API
```

## 📞 注意事项

1. 确保文件格式和大小符合微信要求
2. 图片清晰度要高，避免模糊
3. 视频要进行压缩，控制文件大小
4. 音频清晰，无杂音
5. 定期清理不用的素材文件

---

**开始使用吧！** 🚀
