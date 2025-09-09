# 阿里云OSS到百度云盘迁移工具

这个工具可以将阿里云OSS中指定年份的文件夹下载、打包、上传到百度云盘，然后删除原文件夹。

## 功能特性

- 自动列出指定年份的所有文件夹
- 批量下载文件夹内容
- 创建ZIP压缩包
- 上传到百度云盘
- 删除原OSS文件夹
- 详细的日志记录
- 进度条显示

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制并编辑配置文件：

```bash
cp config.ini config_local.ini
```

2. 编辑 `config_local.ini` 文件，填入您的配置信息：

```ini
[aliyun_oss]
access_key_id = YOUR_ACCESS_KEY_ID
access_key_secret = YOUR_ACCESS_KEY_SECRET
endpoint = https://oss-cn-hangzhou.aliyuncs.com
bucket_name = YOUR_BUCKET_NAME

[baidu_pan]
access_token = YOUR_BAIDU_PAN_ACCESS_TOKEN

[general]
temp_dir = ./temp
output_dir = ./output
target_year = 2023
```

### 配置说明

- **aliyun_oss**: 阿里云OSS的访问凭证和配置
- **baidu_pan**: 百度云盘的访问令牌
- **general**: 通用配置，包括临时目录、输出目录和目标年份

## 使用方法

### 基本用法

```bash
python oss_to_baidupan.py
```

### 使用自定义配置文件

```bash
python oss_to_baidupan.py config_local.ini
```

## 工作流程

1. **扫描文件夹**: 列出OSS中指定年份的所有文件夹
2. **下载文件**: 将每个文件夹的内容下载到本地临时目录
3. **创建压缩包**: 将下载的文件夹打包成ZIP文件
4. **上传到百度云盘**: 将ZIP文件上传到百度云盘
5. **清理本地文件**: 删除本地临时文件
6. **删除OSS文件夹**: 删除OSS中的原始文件夹

## 注意事项

⚠️ **重要提醒**:
- 此操作会永久删除OSS中的原始文件夹，请确保数据已正确备份
- 建议先在测试环境中验证功能
- 确保有足够的本地存储空间用于临时文件
- 百度云盘API需要有效的访问令牌

## 日志

程序运行时会生成详细的日志文件 `migration.log`，包含：
- 操作进度
- 错误信息
- 成功/失败统计

## 错误处理

程序包含完善的错误处理机制：
- 网络连接错误
- 文件操作错误
- API调用错误
- 权限错误

## 扩展功能

### 使用真实的百度云盘客户端

当前版本使用模拟客户端进行测试。要使用真实的百度云盘API，请：

1. 替换 `MockBaiduPanClient` 为 `BaiduPanClient`
2. 配置正确的百度云盘API参数
3. 实现百度云盘的OAuth认证流程

### 自定义配置

可以通过修改配置文件来调整：
- 目标年份
- 临时目录位置
- 输出目录位置
- 压缩格式

## 故障排除

### 常见问题

1. **认证失败**: 检查阿里云OSS和百度云盘的访问凭证
2. **权限不足**: 确保有足够的OSS和百度云盘权限
3. **存储空间不足**: 检查本地临时目录的可用空间
4. **网络超时**: 检查网络连接，考虑使用代理

### 调试模式

启用详细日志：

```python
logging.basicConfig(level=logging.DEBUG)
```

## 许可证

MIT License