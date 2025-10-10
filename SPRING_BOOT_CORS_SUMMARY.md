# Spring Boot 跨域处理完整解决方案

## 📁 项目结构

```
/workspace/
├── pom.xml                                    # Maven配置文件
├── start-cors-demo.sh                        # 启动脚本
├── test-cors.sh                              # 测试脚本
├── README_CORS.md                            # 详细文档
├── SPRING_BOOT_CORS_SUMMARY.md              # 本文件
└── src/
    └── main/
        ├── java/com/example/corsdemo/
        │   ├── CorsDemoApplication.java      # 主应用类
        │   ├── config/
        │   │   ├── CorsConfig.java          # CORS配置类
        │   │   └── SecurityConfig.java      # 安全配置类
        │   └── controller/
        │       ├── ApiController.java       # 基础API控制器
        │       └── CorsTestController.java  # CORS测试控制器
        └── resources/
            ├── application.yml              # 主配置文件
            ├── application-dev.yml          # 开发环境配置
            └── static/
                └── test.html               # 测试页面
```

## 🚀 快速启动

### 1. 启动应用
```bash
./start-cors-demo.sh
```

### 2. 运行测试
```bash
./test-cors.sh
```

### 3. 访问测试页面
打开浏览器访问：http://localhost:8080/test.html

## 🔧 六种跨域配置方法

### 1. WebMvcConfigurer接口配置（推荐）
- **文件**: `CorsConfig.java`
- **特点**: 全局生效，配置简单
- **适用**: 大多数场景

### 2. CorsConfigurationSource Bean配置
- **文件**: `CorsConfig.java`
- **特点**: 更细粒度控制，支持复杂规则
- **适用**: 需要复杂CORS规则的场景

### 3. Controller级别@CrossOrigin注解
- **文件**: `ApiController.java`
- **特点**: 只对特定Controller生效
- **适用**: 不同Controller需要不同CORS规则

### 4. 方法级别@CrossOrigin注解
- **文件**: `CorsTestController.java`
- **特点**: 最细粒度控制
- **适用**: 特殊方法需要特殊CORS规则

### 5. Spring Security配置
- **文件**: `SecurityConfig.java`
- **特点**: 与Spring Security集成
- **适用**: 需要认证的应用

### 6. 手动处理OPTIONS请求
- **文件**: `CorsTestController.java`
- **特点**: 完全自定义控制
- **适用**: 特殊场景

## 🌐 API端点

### 基础API
- `GET /api/test` - 基础GET请求
- `POST /api/test` - 基础POST请求
- `PUT /api/test/{id}` - 基础PUT请求
- `DELETE /api/test/{id}` - 基础DELETE请求
- `POST /api/test/headers` - 带自定义请求头
- `GET /api/data` - 返回JSON数据

### CORS测试API
- `GET /cors/method-level` - 方法级别CORS
- `POST /cors/specific-path` - 特定路径CORS
- `GET /cors/manual-options` - 手动OPTIONS处理
- `POST /cors/complex-request` - 复杂请求测试

## 📋 配置参数

| 参数 | 说明 | 默认值 | 生产环境建议 |
|------|------|--------|-------------|
| `allowedOrigins` | 允许的源 | `"*"` | 指定具体域名 |
| `allowedMethods` | 允许的HTTP方法 | `"GET,POST,PUT,DELETE,OPTIONS"` | 根据需求限制 |
| `allowedHeaders` | 允许的请求头 | `"*"` | 指定具体请求头 |
| `exposedHeaders` | 暴露的响应头 | 无 | 根据需要设置 |
| `allowCredentials` | 是否允许携带凭证 | `true` | 根据需求设置 |
| `maxAge` | 预检请求缓存时间 | `3600` | 根据需求调整 |

## 🛠️ 生产环境配置建议

### 1. 安全配置
```java
// 不要使用 "*" 作为允许的源
.allowedOrigins("https://yourdomain.com", "https://www.yourdomain.com")

// 限制允许的方法
.allowedMethods("GET", "POST", "PUT", "DELETE")

// 限制允许的请求头
.allowedHeaders("Content-Type", "Authorization", "X-Requested-With")
```

### 2. 性能优化
```java
// 设置合理的缓存时间
.maxAge(3600)  // 1小时

// 只暴露必要的响应头
.exposedHeaders("Authorization", "Content-Type")
```

### 3. 环境配置
```yaml
# application-prod.yml
spring:
  cors:
    allowed-origins:
      - "https://yourdomain.com"
      - "https://www.yourdomain.com"
    allowed-methods: "GET,POST,PUT,DELETE"
    allowed-headers: "Content-Type,Authorization,X-Requested-With"
    allow-credentials: true
    max-age: 3600
```

## 🐛 常见问题解决

### 1. 预检请求失败
- 确保配置了OPTIONS方法
- 检查路径映射
- 使用`@RequestMapping`而不是`@GetMapping`

### 2. 简单请求被阻止
- 检查`allowedOrigins`配置
- 避免不必要的请求头

### 3. 带凭证请求失败
- 设置`allowCredentials(true)`
- 不能同时使用`allowedOrigins("*")`和`allowCredentials(true)`
- 使用`allowedOriginPatterns`替代

### 4. 自定义请求头被阻止
- 在`allowedHeaders`中添加自定义请求头
- 或使用`allowedHeaders("*")`

## 📚 学习资源

- [Spring Boot CORS官方文档](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-cors)
- [MDN CORS文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [Spring Security CORS配置](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html)

## 🎯 使用建议

1. **开发环境**: 使用方法1（WebMvcConfigurer）快速配置
2. **测试环境**: 结合方法3和方法4进行细粒度控制
3. **生产环境**: 使用严格的CORS配置，限制允许的源、方法和请求头
4. **特殊需求**: 使用方法6手动处理OPTIONS请求

## 📝 更新日志

- **v1.0.0** - 初始版本
  - 提供6种CORS配置方法
  - 包含完整的测试页面和脚本
  - 支持生产环境配置建议
  - 提供详细的文档和示例