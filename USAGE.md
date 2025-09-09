# OSS文件归档脚本使用说明

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置百度云盘
```bash
bypy info
```
按照提示完成百度云盘授权。

### 3. 生成配置文件
```bash
python3 oss_archive_script.py
```
首次运行会自动生成 `config.json` 配置文件。

### 4. 编辑配置文件
编辑 `config.json`，填入正确的OSS和百度云盘信息。

### 5. 测试配置
```bash
python3 test_config.py
```

### 6. 干运行测试（推荐）
```bash
python3 safe_archive.py --dry-run
```

### 7. 执行实际归档
```bash
python3 oss_archive_script.py
```

## 脚本说明

### 主要脚本

1. **`oss_archive_script.py`** - 主脚本，执行实际归档操作
2. **`safe_archive.py`** - 安全版本，支持干运行模式
3. **`test_config.py`** - 配置测试脚本

### 配置文件

- **`config.json`** - 主配置文件
- **`config_template.json`** - 配置模板文件

### 运行脚本

- **`run_archive.sh`** - 一键运行脚本

## 使用流程

### 1. 干运行模式（强烈推荐）
```bash
# 预览将要执行的操作
python3 safe_archive.py --dry-run
```

### 2. 配置测试
```bash
# 测试OSS和百度云盘连接
python3 test_config.py
```

### 3. 执行归档
```bash
# 执行实际归档操作
python3 oss_archive_script.py
```

## 配置说明

### OSS配置
```json
{
    "oss": {
        "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
        "bucket_name": "your-bucket-name",
        "access_key_id": "your-access-key-id",
        "access_key_secret": "your-access-key-secret"
    }
}
```

### 百度云盘配置
```json
{
    "baidu": {
        "app_id": "your-baidu-app-id",
        "app_key": "your-baidu-app-key",
        "secret_key": "your-baidu-secret-key"
    }
}
```

### 归档配置
```json
{
    "archive": {
        "months_threshold": 24,           // 归档阈值（月）
        "temp_dir": "./temp_archive",     // 临时目录
        "baidu_upload_path": "/OSS_Archive" // 百度云盘上传路径
    }
}
```

### 安全配置
```json
{
    "safety": {
        "dry_run": false,                 // 是否干运行
        "backup_before_delete": true,     // 删除前备份
        "max_file_size_mb": 1000         // 最大文件大小限制
    }
}
```

## 注意事项

1. **首次使用建议先干运行**，确认操作无误后再执行实际归档
2. **确保有足够的磁盘空间**用于临时文件存储
3. **确保OSS和百度云盘权限正确**
4. **建议在测试环境先验证**脚本功能
5. **定期检查日志文件** `oss_archive.log`

## 故障排除

### 常见问题

1. **OSS连接失败**
   - 检查endpoint、bucket_name、access_key是否正确
   - 确认网络连接正常

2. **百度云盘连接失败**
   - 运行 `bypy info` 重新授权
   - 检查app_id、app_key、secret_key是否正确

3. **权限不足**
   - 确认OSS访问密钥有删除权限
   - 确认百度云盘有上传权限

4. **磁盘空间不足**
   - 清理临时目录 `./temp_archive`
   - 增加磁盘空间

### 日志查看
```bash
tail -f oss_archive.log
```

## 文件夹结构要求

脚本假设OSS中的文件夹结构为：
```
bucket_name/
├── folder_name1/
│   ├── 2022-01-01/
│   │   ├── file1.txt
│   │   └── file2.txt
│   └── 2022-01-02/
│       └── file3.txt
└── folder_name2/
    └── 2022-02-01/
        └── file4.txt
```

如果您的文件夹结构不同，请修改 `get_old_folders` 方法中的解析逻辑。