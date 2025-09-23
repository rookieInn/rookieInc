# 微信公众号API代理服务器

这是一个用于海外服务器通过阿里云服务器访问微信公众号接口的代理程序。

## 功能特性

- 🔄 **请求代理**: 将海外服务器的请求转发到微信公众号API
- 🔒 **安全控制**: 支持IP白名单和API密钥验证
- 📊 **日志记录**: 完整的请求和响应日志
- ⚡ **高性能**: 基于aiohttp的异步处理
- 🔄 **重试机制**: 自动重试失败的请求
- 🌐 **CORS支持**: 支持跨域请求

## 部署步骤

### 1. 在阿里云服务器上部署代理

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 配置config.yaml文件
# 编辑config.yaml，设置允许的IP地址和API密钥

# 3. 启动代理服务器
python wechat_proxy.py
```

### 2. 配置微信公众号后台

1. 登录微信公众号后台
2. 进入"基本配置" -> "IP白名单"
3. 添加阿里云服务器的公网IP地址

### 3. 在海外服务器上使用代理

```python
# 使用示例
import asyncio
from client_example import WeChatClient

async def main():
    proxy_url = "http://your-aliyun-server:8080"
    async with WeChatClient(proxy_url) as client:
        # 调用微信公众号API
        result = await client.get_access_token("your-appid", "your-secret")
        print(result)

asyncio.run(main())
```

## 配置文件说明

### config.yaml

```yaml
server:
  host: "0.0.0.0"  # 监听地址
  port: 8080       # 监听端口

security:
  allowed_ips:     # 允许访问的IP列表
    - "1.2.3.4"    # 海外服务器IP
  api_key: ""      # API密钥（可选）

wechat:
  timeout: 30      # 请求超时时间
  retry_times: 3   # 重试次数
```

## API接口

### 代理接口

所有微信公众号API都可以通过代理访问：

```
GET/POST http://your-aliyun-server:8080/{wechat-api-path}
```

例如：
- 获取access_token: `GET /cgi-bin/token?grant_type=client_credential&appid=xxx&secret=xxx`
- 发送模板消息: `POST /cgi-bin/message/template/send?access_token=xxx`

### 管理接口

- 健康检查: `GET /health`
- 统计信息: `GET /stats`

## 安全配置

### IP白名单

在`config.yaml`中配置`allowed_ips`，只允许指定的IP访问代理：

```yaml
security:
  allowed_ips:
    - "1.2.3.4"    # 海外服务器IP1
    - "5.6.7.8"    # 海外服务器IP2
```

### API密钥验证

设置API密钥后，客户端需要在请求头或查询参数中提供：

```python
# 方式1：请求头
headers = {'X-API-Key': 'your-api-key'}

# 方式2：查询参数
url = "http://proxy-server:8080/api?api_key=your-api-key"
```

## 监控和日志

### 日志文件

- 代理服务器日志: `wechat_proxy.log`
- 控制台输出: 实时显示请求和错误信息

### 监控接口

```bash
# 健康检查
curl http://your-aliyun-server:8080/health

# 统计信息
curl http://your-aliyun-server:8080/stats
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查阿里云服务器防火墙设置
   - 确认代理服务器正在运行

2. **IP不在白名单**
   - 检查`config.yaml`中的`allowed_ips`配置
   - 确认海外服务器IP地址正确

3. **API密钥验证失败**
   - 检查客户端是否正确提供API密钥
   - 确认服务端和客户端密钥一致

4. **请求超时**
   - 检查网络连接
   - 调整`config.yaml`中的`timeout`设置

### 调试模式

启用详细日志：

```yaml
logging:
  level: "DEBUG"
  log_requests: true
```

## 性能优化

1. **调整并发数**: 根据服务器性能调整aiohttp的并发设置
2. **缓存access_token**: 客户端应该缓存access_token，避免频繁请求
3. **连接池**: 使用连接池复用HTTP连接

## 许可证

MIT License