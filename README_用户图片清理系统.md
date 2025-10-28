# 用户图片清理系统

## 概述

用户图片清理系统是一个自动化的图片管理解决方案，用于管理用户上传的图片，确保每个用户只保留指定数量的图片（默认10张），并自动清理多余的图片记录和OSS存储文件。

## 主要功能

### 1. 图片数量限制
- 每个用户最多保留10张图片（可配置）
- 当用户上传新图片时，自动删除最旧的图片
- 支持按用户ID管理图片

### 2. 自动清理机制
- 定时检查并清理标记为不活跃的图片
- 同时删除数据库记录和OSS文件
- 支持批量处理和重试机制

### 3. 灵活的配置
- 可配置的清理间隔和延迟时间
- 支持试运行模式（不实际删除）
- 详细的日志记录和报告生成

### 4. 多种运行模式
- 手动执行清理
- 定时自动清理
- 系统服务模式

## 系统架构

```
用户图片清理系统
├── 数据库层 (SQLite)
│   ├── 用户图片记录管理
│   ├── 图片元数据存储
│   └── 清理状态跟踪
├── OSS存储层
│   ├── 图片文件存储
│   ├── 文件删除操作
│   └── 存储统计
├── 业务逻辑层
│   ├── 图片数量限制
│   ├── 清理策略执行
│   └── 批量处理
└── 调度层
    ├── 定时任务管理
    ├── 手动执行接口
    └── 服务管理
```

## 文件结构

```
/workspace/
├── user_image_models.py          # 数据库模型和操作
├── oss_image_cleaner.py          # OSS清理器
├── user_image_cleanup_scheduler.py  # 清理调度器
├── test_user_image_cleanup.py    # 测试脚本
├── install_image_cleanup.sh      # 安装脚本
├── config.ini                    # 配置文件
├── requirements_image_cleanup.txt # Python依赖
└── README_用户图片清理系统.md    # 说明文档
```

## 安装和配置

### 1. 运行安装脚本

```bash
# 给安装脚本执行权限
chmod +x install_image_cleanup.sh

# 运行安装脚本
./install_image_cleanup.sh
```

### 2. 配置OSS信息

编辑 `config.ini` 文件，填入正确的OSS配置：

```ini
[aliyun_oss]
access_key_id = YOUR_ACCESS_KEY_ID
access_key_secret = YOUR_ACCESS_KEY_SECRET
endpoint = https://oss-cn-hangzhou.aliyuncs.com
bucket_name = YOUR_BUCKET_NAME
```

### 3. 调整清理参数

根据需要调整清理参数：

```ini
[user_images]
max_images_per_user = 10  # 每个用户最多保留的图片数量

[image_cleanup]
cleanup_interval_hours = 24  # 清理检查间隔（小时）
cleanup_delay_days = 1       # 图片标记为不活跃后多少天可以删除
batch_size = 100             # 批量处理大小
enable_dry_run = False       # 是否启用试运行模式
```

## 使用方法

### 1. 测试系统功能

```bash
# 运行测试脚本
python3 test_user_image_cleanup.py
```

### 2. 手动执行清理

```bash
# 试运行模式（不实际删除）
python3 user_image_cleanup_scheduler.py --cleanup --dry-run

# 实际执行清理
python3 user_image_cleanup_scheduler.py --cleanup

# 清理指定用户的图片
python3 user_image_cleanup_scheduler.py --cleanup --user-id user_001
```

### 3. 启动定时清理

```bash
# 启动定时清理任务
python3 user_image_cleanup_scheduler.py --schedule
```

### 4. 查看统计信息

```bash
# 查看清理统计信息
python3 user_image_cleanup_scheduler.py --stats
```

### 5. 安装为系统服务

```bash
# 安装systemd服务
sudo cp user-image-cleanup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable user-image-cleanup
sudo systemctl start user-image-cleanup

# 查看服务状态
sudo systemctl status user-image-cleanup

# 查看服务日志
sudo journalctl -u user-image-cleanup -f
```

## API接口

### 数据库操作

```python
from user_image_models import UserImageDatabase, UserImage

# 创建数据库实例
db = UserImageDatabase()

# 添加用户图片
image = UserImage(
    user_id="user_001",
    image_name="photo.jpg",
    oss_key="users/user_001/photo.jpg",
    file_size=1024000,
    mime_type="image/jpeg",
    upload_time=datetime.now()
)
db.add_user_image(image)

# 获取用户图片
images = db.get_user_images("user_001")

# 获取统计信息
stats = db.get_user_image_stats("user_001")
```

### OSS清理操作

```python
from oss_image_cleaner import OSSImageCleaner

# 创建OSS清理器
cleaner = OSSImageCleaner()

# 删除单个文件
success = cleaner.delete_single_image("users/user_001/photo.jpg")

# 批量删除文件
result = cleaner.delete_multiple_images([
    "users/user_001/photo1.jpg",
    "users/user_001/photo2.jpg"
])

# 获取存储统计
stats = cleaner.get_storage_stats()
```

## 配置说明

### 主要配置项

| 配置节 | 配置项 | 说明 | 默认值 |
|--------|--------|------|--------|
| user_images | max_images_per_user | 每个用户最多保留的图片数量 | 10 |
| image_cleanup | cleanup_interval_hours | 清理检查间隔（小时） | 24 |
| image_cleanup | cleanup_delay_days | 图片标记为不活跃后多少天可以删除 | 1 |
| image_cleanup | batch_size | 批量处理大小 | 100 |
| image_cleanup | enable_dry_run | 是否启用试运行模式 | False |
| oss_cleaner | max_retries | 最大重试次数 | 3 |
| oss_cleaner | retry_delay | 重试延迟（秒） | 1 |

### 日志配置

系统会自动生成以下日志文件：
- `user_image_cleanup.log`: 主要操作日志
- `cleanup_report_*.json`: 清理报告文件

## 工作流程

### 1. 图片上传流程

```
用户上传图片
    ↓
检查用户当前图片数量
    ↓
如果超过限制 → 标记最旧图片为不活跃
    ↓
添加新图片记录到数据库
    ↓
上传图片到OSS
```

### 2. 清理流程

```
定时检查任务启动
    ↓
查询标记为不活跃且超过延迟时间的图片
    ↓
批量删除OSS文件
    ↓
删除数据库记录
    ↓
生成清理报告
```

## 监控和维护

### 1. 日志监控

```bash
# 查看实时日志
tail -f user_image_cleanup.log

# 查看服务日志
sudo journalctl -u user-image-cleanup -f
```

### 2. 统计信息

```bash
# 查看清理统计
python3 user_image_cleanup_scheduler.py --stats
```

### 3. 数据库维护

```bash
# 查看数据库文件大小
ls -lh user_images.db

# 备份数据库
cp user_images.db user_images_backup_$(date +%Y%m%d).db
```

## 故障排除

### 常见问题

1. **OSS连接失败**
   - 检查配置文件中的OSS配置是否正确
   - 确认网络连接正常
   - 验证OSS访问权限

2. **数据库操作失败**
   - 检查数据库文件权限
   - 确认磁盘空间充足
   - 查看详细错误日志

3. **清理任务不执行**
   - 检查定时任务配置
   - 确认服务状态正常
   - 查看系统日志

### 调试模式

```bash
# 启用详细日志
# 在config.ini中设置：
[logging]
level = DEBUG

# 使用试运行模式测试
python3 user_image_cleanup_scheduler.py --cleanup --dry-run
```

## 安全考虑

1. **权限控制**
   - 确保OSS访问密钥安全
   - 限制数据库文件访问权限
   - 使用非root用户运行服务

2. **数据备份**
   - 定期备份数据库文件
   - 重要图片建议额外备份
   - 保留清理操作日志

3. **操作审计**
   - 记录所有删除操作
   - 生成详细的清理报告
   - 支持操作回滚（通过备份）

## 性能优化

1. **批量处理**
   - 使用批量删除减少API调用
   - 合理设置批次大小
   - 添加操作间隔避免限流

2. **数据库优化**
   - 创建适当的索引
   - 定期清理旧数据
   - 使用连接池管理连接

3. **存储优化**
   - 定期清理孤立文件
   - 监控存储使用情况
   - 优化文件存储结构

## 扩展功能

### 可能的扩展

1. **多存储支持**
   - 支持其他云存储服务
   - 实现存储抽象层
   - 支持存储迁移

2. **智能清理策略**
   - 基于访问频率的清理
   - 基于文件大小的清理
   - 用户自定义清理规则

3. **Web管理界面**
   - 提供Web管理界面
   - 实时监控和统计
   - 手动操作接口

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 在生产环境使用前，请务必在测试环境中充分测试所有功能，并确保有完整的数据备份策略。