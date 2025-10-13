# Spring Boot 图形验证码实现

这是一个完整的Spring Boot图形验证码解决方案，提供了生成、验证和管理图形验证码的完整功能。

## 功能特性

- ✅ **自动生成随机验证码** - 支持自定义字符集和长度
- ✅ **图形干扰效果** - 包含干扰线和干扰点，提高安全性
- ✅ **Redis缓存存储** - 使用Redis存储验证码，支持分布式部署
- ✅ **自动过期机制** - 验证码自动过期，防止重放攻击
- ✅ **RESTful API接口** - 提供完整的REST API
- ✅ **响应式前端界面** - 美观的Web界面，支持移动端
- ✅ **可配置参数** - 支持自定义验证码样式和参数

## 技术栈

- **后端**: Spring Boot 2.7.14
- **缓存**: Redis
- **模板引擎**: Thymeleaf
- **前端**: HTML5 + CSS3 + JavaScript
- **构建工具**: Maven

## 快速开始

### 1. 环境要求

- Java 11+
- Maven 3.6+
- Redis 5.0+

### 2. 安装Redis

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### CentOS/RHEL
```bash
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### Docker
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

### 3. 运行项目

```bash
# 克隆项目
git clone <repository-url>
cd captcha-demo

# 编译项目
mvn clean compile

# 运行项目
mvn spring-boot:run
```

### 4. 访问应用

- 首页: http://localhost:8080
- 演示页面: http://localhost:8080/demo
- API文档: http://localhost:8080/api/captcha/generate

## API接口

### 1. 生成验证码

```http
GET /api/captcha/generate
```

**响应示例:**
```json
{
  "success": true,
  "message": "验证码生成成功",
  "data": {
    "imageBase64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "answer": "A3B7",
    "captchaId": "abc123def456",
    "expireTime": 1703123456789
  }
}
```

### 2. 验证验证码

```http
POST /api/captcha/verify
Content-Type: application/x-www-form-urlencoded

captchaId=abc123def456&captchaCode=A3B7
```

**响应示例:**
```json
{
  "success": true,
  "message": "验证码验证成功",
  "valid": true
}
```

### 3. 刷新验证码

```http
GET /api/captcha/refresh
```

## 配置说明

在 `application.yml` 中可以配置以下参数:

```yaml
captcha:
  # 验证码长度
  length: 4
  # 验证码过期时间（秒）
  expire-time: 300
  # 图片宽度
  width: 120
  # 图片高度
  height: 40
  # 干扰线数量
  line-count: 20
  # 干扰点数量
  point-count: 50
  # 字体大小
  font-size: 24
  # 字符集
  chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
```

## 项目结构

```
src/
├── main/
│   ├── java/com/example/
│   │   ├── CaptchaDemoApplication.java          # 启动类
│   │   ├── config/
│   │   │   ├── CaptchaProperties.java          # 验证码配置属性
│   │   │   ├── RedisConfig.java                # Redis配置
│   │   │   └── WebConfig.java                  # Web配置
│   │   ├── controller/
│   │   │   ├── CaptchaController.java          # 验证码API控制器
│   │   │   └── PageController.java             # 页面控制器
│   │   ├── model/
│   │   │   └── CaptchaResult.java              # 验证码结果模型
│   │   └── service/
│   │       └── CaptchaService.java             # 验证码服务类
│   └── resources/
│       ├── application.yml                     # 应用配置
│       ├── static/css/
│       │   └── style.css                       # 样式文件
│       └── templates/
│           ├── index.html                      # 首页
│           └── demo.html                       # 演示页面
└── test/                                       # 测试代码
```

## 使用示例

### 前端JavaScript调用

```javascript
// 生成验证码
async function generateCaptcha() {
    const response = await fetch('/api/captcha/generate');
    const result = await response.json();
    
    if (result.success) {
        const data = result.data;
        document.getElementById('captchaImage').src = data.imageBase64;
        // 保存captchaId用于验证
        window.captchaId = data.captchaId;
    }
}

// 验证验证码
async function verifyCaptcha(captchaCode) {
    const formData = new FormData();
    formData.append('captchaId', window.captchaId);
    formData.append('captchaCode', captchaCode);
    
    const response = await fetch('/api/captcha/verify', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    return result.valid;
}
```

### Java代码集成

```java
@Autowired
private CaptchaService captchaService;

// 生成验证码
CaptchaResult captcha = captchaService.generateCaptcha();

// 验证验证码
boolean isValid = captchaService.verifyCaptcha(captchaId, userInput);
```

## 安全建议

1. **HTTPS部署** - 生产环境建议使用HTTPS
2. **IP限制** - 可以添加IP访问频率限制
3. **验证码复杂度** - 根据安全需求调整验证码复杂度
4. **日志监控** - 监控验证码生成和验证的日志
5. **Redis安全** - 确保Redis访问安全

## 故障排除

### 1. Redis连接失败
```
检查Redis服务是否启动
检查application.yml中的Redis配置
检查网络连接
```

### 2. 验证码图片不显示
```
检查Base64编码是否正确
检查浏览器控制台是否有错误
检查图片格式支持
```

### 3. 验证码验证失败
```
检查验证码是否过期
检查输入是否正确（大小写敏感）
检查Redis中是否存储了验证码
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题，请通过以下方式联系：

- 邮箱: example@example.com
- GitHub: https://github.com/example/captcha-demo