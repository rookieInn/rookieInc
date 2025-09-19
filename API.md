# 短链接服务 API 文档

## 概述

短链接服务提供RESTful API来创建、管理和访问短链接。所有API都返回JSON格式的响应。

**Base URL**: `https://your-domain.com/api`

## 认证

目前API不需要认证，但建议在生产环境中添加API密钥认证。

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": { ... }
}
```

### 错误响应
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "Error description"
}
```

## API 端点

### 1. 创建短链接

**POST** `/shorten`

创建新的短链接。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| url | string | 是 | 原始URL |
| title | string | 否 | 链接标题 |
| description | string | 否 | 链接描述 |
| expiresAt | string | 否 | 过期时间 (ISO 8601格式) |
| password | string | 否 | 访问密码 |

#### 请求示例

```bash
curl -X POST https://your-domain.com/api/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com/very/long/url",
    "title": "示例网站",
    "description": "这是一个示例网站链接",
    "expiresAt": "2024-12-31T23:59:59",
    "password": "mypassword"
  }'
```

#### 响应示例

```json
{
  "success": true,
  "shortCode": "abc123",
  "shortUrl": "https://your-domain.com/api/s/abc123",
  "originalUrl": "https://www.example.com/very/long/url",
  "title": "示例网站",
  "description": "这是一个示例网站链接",
  "expiresAt": "2024-12-31T23:59:59",
  "hasPassword": true,
  "createdAt": "2024-01-01T12:00:00"
}
```

### 2. 获取短链接信息

**GET** `/info/{shortCode}`

获取短链接的详细信息。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| shortCode | string | 是 | 短码 |

#### 请求示例

```bash
curl -X GET https://your-domain.com/api/info/abc123
```

#### 响应示例

```json
{
  "success": true,
  "shortCode": "abc123",
  "originalUrl": "https://www.example.com/very/long/url",
  "title": "示例网站",
  "description": "这是一个示例网站链接",
  "accessCount": 150,
  "uniqueAccessCount": 120,
  "isActive": true,
  "expiresAt": "2024-12-31T23:59:59",
  "hasPassword": true,
  "createdAt": "2024-01-01T12:00:00",
  "updatedAt": "2024-01-01T12:30:00"
}
```

### 3. 验证密码

**POST** `/validate/{shortCode}`

验证受密码保护的短链接的密码。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| shortCode | string | 是 | 短码 |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| password | string | 是 | 密码 |

#### 请求示例

```bash
curl -X POST https://your-domain.com/api/validate/abc123 \
  -H "Content-Type: application/json" \
  -d '{"password": "mypassword"}'
```

#### 响应示例

```json
{
  "success": true,
  "valid": true
}
```

### 4. 删除短链接

**DELETE** `/{shortCode}`

删除指定的短链接。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| shortCode | string | 是 | 短码 |

#### 请求示例

```bash
curl -X DELETE https://your-domain.com/api/abc123
```

#### 响应示例

```json
{
  "success": true,
  "deleted": true
}
```

### 5. 短链接重定向

**GET** `/s/{shortCode}`

访问短链接并重定向到原始URL。

#### 路径参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| shortCode | string | 是 | 短码 |

#### 请求示例

```bash
curl -I https://your-domain.com/api/s/abc123
```

#### 响应示例

```
HTTP/1.1 302 Found
Location: https://www.example.com/very/long/url
```

### 6. 健康检查

**GET** `/health`

检查服务健康状态。

#### 请求示例

```bash
curl -X GET https://your-domain.com/api/health
```

#### 响应示例

```json
{
  "status": "UP",
  "timestamp": "2024-01-01T12:00:00",
  "service": "short-url-service",
  "version": "1.0.0"
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|----------|------------|------|
| INVALID_URL | 400 | URL格式无效 |
| SHORT_URL_NOT_FOUND | 404 | 短链接不存在 |
| SHORT_URL_EXPIRED | 410 | 短链接已过期 |
| INVALID_PASSWORD | 401 | 密码错误 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率过高 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |

## 限制

### 请求限制

- **API接口**: 10 请求/秒
- **重定向接口**: 100 请求/秒
- **URL长度**: 最大 2048 字符
- **短码长度**: 4-8 字符

### 数据限制

- **标题长度**: 最大 255 字符
- **描述长度**: 最大 500 字符
- **密码长度**: 最大 64 字符

## 使用示例

### JavaScript 示例

```javascript
// 创建短链接
async function createShortUrl(originalUrl) {
  const response = await fetch('/api/shorten', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      url: originalUrl,
      title: '我的链接',
      description: '这是一个测试链接'
    })
  });
  
  const data = await response.json();
  return data.shortUrl;
}

// 使用示例
createShortUrl('https://www.example.com/very/long/url')
  .then(shortUrl => console.log('短链接:', shortUrl))
  .catch(error => console.error('错误:', error));
```

### Python 示例

```python
import requests

# 创建短链接
def create_short_url(original_url):
    response = requests.post('https://your-domain.com/api/shorten', json={
        'url': original_url,
        'title': '我的链接',
        'description': '这是一个测试链接'
    })
    
    if response.status_code == 200:
        data = response.json()
        return data['shortUrl']
    else:
        raise Exception(f'创建失败: {response.text}')

# 使用示例
try:
    short_url = create_short_url('https://www.example.com/very/long/url')
    print(f'短链接: {short_url}')
except Exception as e:
    print(f'错误: {e}')
```

## 监控和指标

服务提供Prometheus指标端点：`/actuator/prometheus`

主要指标包括：
- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: 请求处理时间
- `cache_hits_total`: 缓存命中次数
- `cache_misses_total`: 缓存未命中次数
- `short_url_created_total`: 创建的短链接总数
- `short_url_redirected_total`: 重定向次数

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基本的短链接创建和重定向
- 支持密码保护
- 支持过期时间设置
- 支持访问统计
- 支持多级缓存