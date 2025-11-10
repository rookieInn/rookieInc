# 图片文字提取与翻译应用

该应用提供一个简洁的 Web 页面，支持上传图片、调用 Baidu OCR API 识别文字，并自动调用 Baidu 翻译 API 将文字翻译为指定语言。识别结果可以复制、下载为 TXT 文件，并生成原文与译文对照的 DOCX 文档。

## 功能概览

- 上传图片（支持 png/jpg/jpeg/bmp/gif/tiff 等常见格式）
- 调用 Baidu OCR 接口提取图片文字
- 将识别结果翻译为指定语言（默认英语）
- 页面上一键复制原文与译文
- 导出原文 TXT、译文 TXT、原文/译文对照 TXT
- 生成原文与译文对照的 DOCX 文档

## 环境准备

1. 建议使用 Python 3.10 以上版本，并创建虚拟环境：

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 配置凭证

应用会从以下来源读取 Baidu OCR 与翻译接口所需的凭证（优先级从高到低）：

1. 环境变量：
   - `BAIDU_OCR_API_KEY`
   - `BAIDU_OCR_SECRET_KEY`
   - `BAIDU_TRANSLATE_APP_ID`
   - `BAIDU_TRANSLATE_SECRET_KEY`

2. 配置文件 `image_text_app/config.json`

可复制示例配置并填写个人凭证：

```bash
cp image_text_app/config.example.json image_text_app/config.json
```

将文件中的占位符替换为真实的 Key 和 Secret。

> **注意**：Baidu OCR 与 Baidu 翻译凭证需要分别在百度智能云控制台开通并获取。

## 运行应用

```bash
python image_text_app/app.py
```

默认监听 `http://127.0.0.1:5000`。若需要在局域网访问，可设置环境变量 `FLASK_DEBUG=1` 并根据需要调整 `host`、`port`。

## 导出文件说明

- `原文 TXT`：仅包含 OCR 识别出的文本
- `译文 TXT`：仅包含翻译后的文本
- `原文/译文 对照 TXT`：按行展示原文与译文，中间以制表符分隔
- `原文/译文 对照 DOCX`：以双列表格形式排版，可直接用于分享或归档

## 常见问题

- **页面提示缺少凭证？**  
  请确认已设置环境变量或在 `config.json` 中填写了正确的 Key。

- **OCR 返回空结果？**  
  可能是图片中文字较少或清晰度不够，可尝试上传更清晰的图片或使用其他 OCR 模型。

- **翻译失败？**  
  检查翻译接口的 App ID 和密钥是否正确，或确认 Baidu 翻译服务已开通。

如需扩展功能（例如支持多语种对照导出、识别区域选择等），可以在现有基础上继续拓展。
