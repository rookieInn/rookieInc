# Let's Encrypt SSL证书自动管理脚本

这是一个自动化的Let's Encrypt SSL证书管理脚本，可以自动申请、续期SSL证书并更新Nginx配置。

## 功能特性

- 🔐 自动申请Let's Encrypt SSL证书
- 🔄 自动检查证书有效期并续期
- 🌐 自动更新Nginx配置
- 📝 详细的日志记录
- ⚙️ 灵活的配置选项
- 🛡️ 安全的SSL配置
- 🔧 支持试运行模式
- ⏰ 支持定时任务执行

## 系统要求

- Linux系统（Ubuntu/Debian/CentOS/RHEL）
- Nginx
- Certbot
- OpenSSL
- systemd（用于定时任务）

## 安装步骤

### 1. 安装依赖

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx nginx openssl
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx nginx openssl
```

### 2. 下载脚本

```bash
# 下载脚本文件
wget https://raw.githubusercontent.com/your-repo/ssl-cert-manager/main/ssl_cert_manager.sh
chmod +x ssl_cert_manager.sh

# 下载配置文件模板
wget https://raw.githubusercontent.com/your-repo/ssl-cert-manager/main/ssl_config.conf.example
```

### 3. 配置脚本

```bash
# 复制配置文件模板
cp ssl_config.conf.example ssl_config.conf

# 编辑配置文件
nano ssl_config.conf
```

配置文件示例：
```bash
# 必需配置
DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"

# Nginx配置
NGINX_SITE_CONFIG="/etc/nginx/sites-available/yourdomain.com"
WEBROOT="/var/www/html"

# 证书管理
CERT_RENEWAL_DAYS=30
```

### 4. 设置定时任务

```bash
# 复制systemd服务文件
sudo cp ssl-cert-manager.service /etc/systemd/system/
sudo cp ssl-cert-manager.timer /etc/systemd/system/

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用并启动定时器
sudo systemctl enable ssl-cert-manager.timer
sudo systemctl start ssl-cert-manager.timer

# 检查定时器状态
sudo systemctl status ssl-cert-manager.timer
```

## 使用方法

### 基本使用

```bash
# 使用配置文件运行
./ssl_cert_manager.sh

# 指定域名和邮箱运行
./ssl_cert_manager.sh --domain example.com --email admin@example.com

# 试运行模式（不实际申请证书）
./ssl_cert_manager.sh --dry-run

# 强制续期证书
./ssl_cert_manager.sh --renew

# 仅更新Nginx配置
./ssl_cert_manager.sh --update-nginx
```

### 命令行参数

- `-h, --help`: 显示帮助信息
- `-d, --domain DOMAIN`: 指定域名
- `-e, --email EMAIL`: 指定邮箱地址
- `-c, --config FILE`: 指定配置文件路径
- `--dry-run`: 试运行模式
- `--renew`: 强制续期证书
- `--update-nginx`: 仅更新Nginx配置

## 配置说明

### 必需配置

- `DOMAIN`: 要申请证书的域名
- `EMAIL`: 联系邮箱，用于Let's Encrypt通知

### 可选配置

- `NGINX_SITE_CONFIG`: Nginx站点配置文件路径
- `WEBROOT`: Web根目录，用于域名验证
- `CERT_RENEWAL_DAYS`: 证书提前多少天开始续期（默认30天）
- `LOG_FILE`: 日志文件路径

## 日志和监控

### 查看日志

```bash
# 查看脚本日志
tail -f /var/log/ssl_cert_manager.log

# 查看systemd服务日志
sudo journalctl -u ssl-cert-manager.service -f

# 查看定时器状态
sudo systemctl status ssl-cert-manager.timer
```

### 监控证书状态

```bash
# 检查证书有效期
openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem

# 检查定时器下次执行时间
sudo systemctl list-timers ssl-cert-manager.timer
```

## 故障排除

### 常见问题

1. **证书申请失败**
   - 检查域名是否正确解析到服务器
   - 确保80端口可访问
   - 检查防火墙设置

2. **Nginx配置更新失败**
   - 检查Nginx配置语法：`sudo nginx -t`
   - 确保有足够的权限修改配置文件
   - 检查配置文件路径是否正确

3. **定时任务不执行**
   - 检查systemd服务状态：`sudo systemctl status ssl-cert-manager.timer`
   - 查看服务日志：`sudo journalctl -u ssl-cert-manager.service`
   - 确保脚本有执行权限

### 调试模式

```bash
# 启用详细日志
export DEBUG=1
./ssl_cert_manager.sh

# 试运行模式
./ssl_cert_manager.sh --dry-run
```

## 安全注意事项

1. **权限管理**: 脚本需要root权限来修改系统配置
2. **证书安全**: 证书文件存储在`/etc/letsencrypt/`目录，确保目录权限正确
3. **日志安全**: 日志文件可能包含敏感信息，注意文件权限
4. **网络安全**: 确保防火墙配置正确，只开放必要端口

## 高级配置

### 多域名支持

为多个域名创建不同的配置文件：

```bash
# 为每个域名创建单独的配置
cp ssl_config.conf.example ssl_config_domain1.conf
cp ssl_config.conf.example ssl_config_domain2.conf

# 修改配置后分别运行
./ssl_cert_manager.sh --config ssl_config_domain1.conf
./ssl_cert_manager.sh --config ssl_config_domain2.conf
```

### 自定义Nginx配置

脚本会自动生成基本的Nginx SSL配置，你也可以在现有配置基础上添加更多功能。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个脚本。

## 更新日志

- v1.0.0: 初始版本，支持基本的证书申请和续期功能