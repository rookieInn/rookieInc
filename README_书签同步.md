# Chrome书签同步到Edge浏览器工具

这个工具可以定期将Chrome浏览器的书签同步到Microsoft Edge浏览器中。

## 功能特性

- ✅ 自动检测Chrome和Edge书签文件位置
- ✅ 支持多种操作系统（Linux、macOS、Windows）
- ✅ 定期自动同步（可配置间隔时间）
- ✅ 自动备份Edge书签（防止数据丢失）
- ✅ 支持排除特定文件夹
- ✅ 详细的日志记录
- ✅ 支持systemd服务管理
- ✅ 增量同步和错误处理

## 文件说明

- `chrome_to_edge_sync.py` - 主同步脚本（支持定期同步）
- `bookmark_sync_manual.py` - 简化版本（手动运行）
- `bookmark_sync_config.json` - 配置文件
- `bookmark_sync_requirements.txt` - Python依赖
- `install_bookmark_sync.sh` - 自动安装脚本

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip3 install -r bookmark_sync_requirements.txt

# 或者运行自动安装脚本
./install_bookmark_sync.sh
```

### 2. 手动运行一次同步

```bash
# 使用简化版本（推荐首次使用）
python3 bookmark_sync_manual.py

# 或使用完整版本
python3 chrome_to_edge_sync.py --once
```

### 3. 设置定期同步

#### 方法一：使用systemd服务（推荐）

```bash
# 安装服务
sudo ./install_bookmark_sync.sh

# 启动服务
sudo systemctl start bookmark-sync.service

# 启用开机自启
sudo systemctl enable bookmark-sync.service

# 启用定时器（每30分钟同步一次）
sudo systemctl enable bookmark-sync.timer
sudo systemctl start bookmark-sync.timer

# 查看服务状态
sudo systemctl status bookmark-sync.service
sudo systemctl status bookmark-sync.timer

# 查看日志
journalctl -u bookmark-sync.service -f
```

#### 方法二：使用cron定时任务

```bash
# 编辑crontab
crontab -e

# 添加以下行（每30分钟同步一次）
*/30 * * * * /usr/bin/python3 /workspace/chrome_to_edge_sync.py --once
```

#### 方法三：后台运行脚本

```bash
# 后台运行定期同步
nohup python3 chrome_to_edge_sync.py > /workspace/sync.log 2>&1 &
```

## 配置说明

编辑 `bookmark_sync_config.json` 文件：

```json
{
    "sync_interval_minutes": 30,        // 同步间隔（分钟）
    "backup_enabled": true,             // 是否启用备份
    "backup_retention_days": 7,         // 备份保留天数
    "chrome_profile": "Default",        // Chrome配置文件
    "edge_profile": "Default",          // Edge配置文件
    "exclude_folders": ["书签栏", "其他书签"], // 排除的文件夹
    "log_level": "INFO"                 // 日志级别
}
```

## 使用说明

### 首次使用

1. 确保Chrome和Edge浏览器都已安装
2. 至少运行一次Chrome和Edge浏览器（生成书签文件）
3. 运行 `python3 bookmark_sync_manual.py` 测试同步
4. 如果测试成功，设置定期同步

### 日常使用

- 工具会自动定期同步书签
- 每次同步前会自动备份Edge书签
- 可以通过日志文件查看同步状态
- 支持手动触发同步

### 故障排除

1. **找不到书签文件**
   - 确保浏览器已安装并运行过
   - 检查配置文件中的路径设置

2. **同步失败**
   - 检查文件权限
   - 确保浏览器未在运行（避免文件锁定）
   - 查看日志文件获取详细错误信息

3. **权限问题**
   - 确保脚本有读取Chrome书签的权限
   - 确保脚本有写入Edge书签的权限

## 日志文件

- 主日志：`/workspace/bookmark_sync.log`
- 备份文件：`/workspace/edge_bookmark_backups/`
- systemd日志：`journalctl -u bookmark-sync.service`

## 安全说明

- 工具只读取和写入书签文件，不会访问其他浏览器数据
- 自动备份功能确保数据安全
- 支持排除敏感文件夹
- 所有操作都有详细日志记录

## 注意事项

1. 同步前建议关闭Edge浏览器
2. 首次同步会完全替换Edge书签
3. 定期清理备份文件以节省空间
4. 建议在测试环境先验证功能

## 卸载

```bash
# 停止服务
sudo systemctl stop bookmark-sync.timer
sudo systemctl stop bookmark-sync.service

# 禁用服务
sudo systemctl disable bookmark-sync.timer
sudo systemctl disable bookmark-sync.service

# 删除服务文件
sudo rm /etc/systemd/system/bookmark-sync.service
sudo rm /etc/systemd/system/bookmark-sync.timer

# 重新加载systemd
sudo systemctl daemon-reload
```