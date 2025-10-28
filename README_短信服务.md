# 短信服务系统

一个支持多渠道动态切换的短信发送系统，支持阿里云、腾讯云、华为云等主流短信服务商。

## 功能特性

- ✅ **多渠道支持**: 支持阿里云、腾讯云、华为云、网易云信等主流短信服务商
- ✅ **动态切换**: 支持运行时动态切换短信服务提供商
- ✅ **自动故障转移**: 主服务失败时自动切换到备用服务
- ✅ **配置管理**: 支持通过配置文件或Web界面管理服务提供商
- ✅ **统计监控**: 实时监控发送统计、成功率、费用等
- ✅ **限制控制**: 支持每日发送限制、优先级控制
- ✅ **Web管理界面**: 提供友好的Web管理界面
- ✅ **API接口**: 提供RESTful API接口

## 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web管理界面    │    │   短信管理器      │    │  服务提供商适配器 │
│                 │    │                  │    │                 │
│  - 状态监控      │◄──►│  - 渠道选择      │◄──►│  - 阿里云SMS    │
│  - 配置管理      │    │  - 故障转移      │    │  - 腾讯云SMS    │
│  - 统计查看      │    │  - 统计收集      │    │  - 华为云SMS    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   配置文件管理    │
                       │                  │
                       │  - JSON配置      │
                       │  - 动态更新      │
                       │  - 持久化存储    │
                       └──────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests flask
```

### 2. 配置短信服务

编辑 `sms_config.json` 文件，配置您的短信服务提供商：

```json
{
  "providers": {
    "aliyun_primary": {
      "provider": "aliyun",
      "access_key": "YOUR_ALIYUN_ACCESS_KEY",
      "secret_key": "YOUR_ALIYUN_SECRET_KEY",
      "sign_name": "您的签名",
      "template_id": "SMS_123456789",
      "endpoint": "https://dysmsapi.aliyuncs.com",
      "region": "cn-hangzhou",
      "enabled": true,
      "priority": 1,
      "daily_limit": 1000,
      "cost_per_sms": 0.045
    }
  }
}
```

### 3. 基础使用

```python
from sms_service import SMSManager

# 创建短信管理器
sms_manager = SMSManager("sms_config.json")

# 发送短信
result = sms_manager.send_sms(
    phone="13800138000",
    content="您的验证码是123456，5分钟内有效。",
    template_params={"code": "123456"}
)

if result.success:
    print(f"短信发送成功，消息ID: {result.message_id}")
else:
    print(f"短信发送失败: {result.error_message}")
```

### 4. 启动Web管理界面

```bash
python sms_web_admin.py
```

访问 http://localhost:5000 查看管理界面。

## 详细使用说明

### 短信管理器 (SMSManager)

短信管理器是系统的核心组件，负责管理所有短信服务提供商。

#### 初始化

```python
from sms_service import SMSManager

# 使用默认配置文件
sms_manager = SMSManager()

# 使用自定义配置文件
sms_manager = SMSManager("custom_config.json")
```

#### 发送短信

```python
# 基础发送
result = sms_manager.send_sms(
    phone="13800138000",
    content="短信内容"
)

# 使用模板参数
result = sms_manager.send_sms(
    phone="13800138000",
    content="您的验证码是{code}，{minutes}分钟内有效。",
    template_params={"code": "123456", "minutes": "5"}
)

# 指定服务提供商
result = sms_manager.send_sms(
    phone="13800138000",
    content="短信内容",
    provider_name="aliyun_primary"
)
```

#### 管理服务提供商

```python
# 查看状态
status = sms_manager.get_provider_status()
print(status)

# 切换服务提供商
sms_manager.switch_provider("aliyun_primary", False)  # 禁用
sms_manager.switch_provider("tencent_backup", True)   # 启用

# 保存配置
sms_manager.save_config()
```

### 服务提供商配置

每个服务提供商需要以下配置：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| provider | string | 是 | 服务提供商类型 (aliyun/tencent/huawei) |
| access_key | string | 是 | API访问密钥 |
| secret_key | string | 是 | API密钥 |
| sign_name | string | 是 | 短信签名 |
| template_id | string | 是 | 短信模板ID |
| endpoint | string | 否 | API端点URL |
| region | string | 否 | 服务区域 |
| enabled | boolean | 否 | 是否启用 (默认true) |
| priority | integer | 否 | 优先级 (数字越小优先级越高) |
| daily_limit | integer | 否 | 每日发送限制 |
| cost_per_sms | float | 否 | 每条短信费用 |

### 支持的服务提供商

#### 阿里云短信

```json
{
  "provider": "aliyun",
  "access_key": "LTAI5txxxxxxxxxxxxxxxxx",
  "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "sign_name": "您的签名",
  "template_id": "SMS_123456789",
  "endpoint": "https://dysmsapi.aliyuncs.com",
  "region": "cn-hangzhou"
}
```

#### 腾讯云短信

```json
{
  "provider": "tencent",
  "access_key": "AKIDxxxxxxxxxxxxxxxxxxxx",
  "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
  "sign_name": "您的签名",
  "template_id": "1234567",
  "endpoint": "https://sms.tencentcloudapi.com",
  "region": "ap-beijing"
}
```

#### 华为云短信

```json
{
  "provider": "huawei",
  "access_key": "YOUR_HUAWEI_ACCESS_KEY",
  "secret_key": "YOUR_HUAWEI_SECRET_KEY",
  "sign_name": "您的签名",
  "template_id": "1234567890123456789",
  "endpoint": "https://rtcsms.cn-north-4.myhuaweicloud.com",
  "region": "cn-north-4"
}
```

## Web管理界面

系统提供了完整的Web管理界面，包括：

### 功能特性

- **实时监控**: 实时显示各服务提供商状态
- **动态切换**: 一键启用/禁用服务提供商
- **统计查看**: 查看发送统计、成功率等
- **配置管理**: 在线修改配置参数
- **批量操作**: 支持批量发送短信

### 访问地址

```
http://localhost:5000
```

### 主要页面

- `/` - 状态监控页面
- `/api/status` - 获取服务提供商状态
- `/api/send` - 发送短信API
- `/api/switch` - 切换服务提供商API
- `/api/stats` - 获取统计信息API
- `/api/config` - 配置管理API

## API接口

### 发送短信

```http
POST /api/send
Content-Type: application/json

{
  "phone": "13800138000",
  "content": "短信内容",
  "template_params": {"code": "123456"},
  "provider_name": "aliyun_primary"
}
```

### 切换服务提供商

```http
POST /api/switch
Content-Type: application/json

{
  "provider_name": "aliyun_primary",
  "enabled": false
}
```

### 获取状态

```http
GET /api/status
```

### 获取统计信息

```http
GET /api/stats
```

## 高级功能

### 故障转移

系统支持自动故障转移，当主服务提供商失败时，会自动尝试备用服务提供商。

```python
# 配置多个服务提供商
config = {
  "providers": {
    "aliyun_primary": {
      "provider": "aliyun",
      "priority": 1,
      "enabled": true
    },
    "tencent_backup": {
      "provider": "tencent", 
      "priority": 2,
      "enabled": true
    }
  },
  "fallback_enabled": true
}
```

### 每日限制

支持为每个服务提供商设置每日发送限制。

```python
# 设置每日限制
config = SMSConfig(
    provider=SMSProvider.ALIYUN,
    daily_limit=1000,  # 每日最多发送1000条
    # ... 其他配置
)
```

### 成本统计

系统会自动统计各服务提供商的发送成本和总成本。

```python
# 查看成本统计
status = sms_manager.get_provider_status()
for name, info in status.items():
    print(f"{name}: 余额 {info['balance']:.2f}元")
```

### 优先级控制

通过设置优先级来控制服务提供商的使用顺序。

```python
# 设置优先级（数字越小优先级越高）
config = SMSConfig(
    provider=SMSProvider.ALIYUN,
    priority=1,  # 最高优先级
    # ... 其他配置
)
```

## 测试和调试

### 运行测试

```bash
# 运行基础测试
python sms_test.py

# 运行使用示例
python sms_example.py
```

### 调试模式

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 创建短信管理器
sms_manager = SMSManager("sms_config.json")
```

### 常见问题

1. **短信发送失败**
   - 检查API密钥是否正确
   - 确认短信签名和模板ID是否有效
   - 检查网络连接是否正常

2. **服务提供商无法切换**
   - 确认配置文件格式正确
   - 检查服务提供商配置是否完整
   - 查看日志中的错误信息

3. **Web界面无法访问**
   - 确认Flask应用已启动
   - 检查端口5000是否被占用
   - 确认防火墙设置

## 部署建议

### 生产环境

1. **安全性**
   - 使用HTTPS协议
   - 设置强密码和API密钥
   - 定期更新依赖包

2. **性能优化**
   - 使用连接池
   - 启用缓存
   - 监控系统资源

3. **监控告警**
   - 设置发送失败告警
   - 监控服务提供商状态
   - 记录详细日志

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "sms_web_admin.py"]
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持阿里云、腾讯云、华为云短信服务
- 实现动态切换和故障转移
- 提供Web管理界面
- 支持统计监控和配置管理