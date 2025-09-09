# OSS文件归档脚本

这个脚本用于将阿里云OSS中24个月前的按日创建的文件夹打包上传到百度云盘，然后删除OSS中的原始文件。

## 功能特性

- 自动识别OSS中按日创建的文件夹
- 筛选24个月前的文件夹进行归档
- 将文件夹内容打包成ZIP文件
- 上传ZIP文件到百度云盘
- 删除OSS中的原始文件
- 完整的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 运行脚本会自动创建 `config.json` 配置文件
2. 编辑配置文件，填入正确的OSS和百度云盘信息：

```json
{
    "oss": {
        "endpoint": "your-oss-endpoint",
        "bucket_name": "your-bucket-name",
        "access_key_id": "your-access-key-id",
        "access_key_secret": "your-access-key-secret"
    },
    "baidu": {
        "app_id": "your-baidu-app-id",
        "app_key": "your-baidu-app-key",
        "secret_key": "your-baidu-secret-key"
    },
    "archive": {
        "months_threshold": 24,
        "temp_dir": "./temp_archive",
        "baidu_upload_path": "/OSS_Archive"
    }
}
```

## 百度云盘配置

使用bypy库需要先进行授权：

```bash
bypy info
```

按照提示完成百度云盘的授权配置。

## 使用方法

```bash
python oss_archive_script.py
```

## 注意事项

1. 确保有足够的磁盘空间用于临时文件
2. 确保OSS和百度云盘的访问权限正确
3. 建议先在测试环境验证脚本功能
4. 脚本会生成详细的日志文件 `oss_archive.log`

## 文件夹结构假设

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