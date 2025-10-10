# Spring Boot 跨域处理解决方案

本项目提供了完整的Spring Boot跨域（CORS）处理解决方案，包含多种配置方法和测试页面。

## 🚀 快速开始

### 1. 启动应用

```bash
# 使用Maven启动
mvn spring-boot:run

# 或者先编译再运行
mvn clean package
java -jar target/spring-boot-cors-demo-1.0.0.jar
```

### 2. 访问测试页面

打开浏览器访问：http://localhost:8080/test.html

## 📋 跨域配置方法

### 方法1: WebMvcConfigurer接口配置（推荐）

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
```

**优点：**
- 全局生效
- 配置简单
- 支持所有Controller

### 方法2: CorsConfigurationSource Bean配置

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration configuration = new CorsConfiguration();
    configuration.setAllowedOriginPatterns(Collections.singletonList("*"));
    configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    configuration.setAllowedHeaders(Collections.singletonList("*"));
    configuration.setAllowCredentials(true);
    configuration.setMaxAge(3600L);
    
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", configuration);
    return source;
}
```

**优点：**
- 更细粒度的控制
- 可以配置暴露的响应头
- 支持复杂的CORS规则

### 方法3: Controller级别@CrossOrigin注解

```java
@RestController
@CrossOrigin(origins = "*", maxAge = 3600)
public class ApiController {
    // Controller方法
}
```

**优点：**
- 只对特定Controller生效
- 配置灵活
- 可以覆盖全局配置

### 方法4: 方法级别@CrossOrigin注解

```java
@GetMapping("/test")
@CrossOrigin(
    origins = {"http://localhost:3000", "http://127.0.0.1:3000"},
    methods = {RequestMethod.GET, RequestMethod.POST},
    allowedHeaders = "*",
    allowCredentials = "true"
)
public ResponseEntity<Map<String, Object>> test() {
    // 方法实现
}
```

**优点：**
- 最细粒度的控制
- 可以为不同方法配置不同的CORS规则
- 适合特殊需求

### 方法5: Spring Security配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.csrf().disable()
            .cors().configurationSource(corsConfigurationSource())
            .and()
            .authorizeHttpRequests(authz -> authz.anyRequest().permitAll());
        return http.build();
    }
}
```

**优点：**
- 与Spring Security集成
- 支持更复杂的安全策略
- 适合需要认证的应用

### 方法6: 手动处理OPTIONS请求

```java
@RequestMapping(value = "/api/test", method = RequestMethod.OPTIONS)
public ResponseEntity<Void> handleOptions() {
    return ResponseEntity.ok()
            .header("Access-Control-Allow-Origin", "*")
            .header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            .header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            .header("Access-Control-Max-Age", "3600")
            .build();
}
```

**优点：**
- 完全自定义控制
- 适合特殊场景
- 可以动态处理

## 🔧 配置参数说明

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `allowedOrigins` | 允许的源 | `"*"`, `"http://localhost:3000"` |
| `allowedMethods` | 允许的HTTP方法 | `"GET,POST,PUT,DELETE,OPTIONS"` |
| `allowedHeaders` | 允许的请求头 | `"*"`, `"Content-Type,Authorization"` |
| `exposedHeaders` | 暴露的响应头 | `"Authorization,Content-Type"` |
| `allowCredentials` | 是否允许携带凭证 | `true`, `false` |
| `maxAge` | 预检请求缓存时间（秒） | `3600` |

## 🌐 测试API端点

### 基础API测试
- `GET /api/test` - 基础GET请求
- `POST /api/test` - 基础POST请求
- `PUT /api/test/{id}` - 基础PUT请求
- `DELETE /api/test/{id}` - 基础DELETE请求
- `POST /api/test/headers` - 带自定义请求头
- `GET /api/data` - 返回JSON数据

### CORS配置测试
- `GET /cors/method-level` - 方法级别CORS
- `POST /cors/specific-path` - 特定路径CORS
- `GET /cors/manual-options` - 手动OPTIONS处理
- `POST /cors/complex-request` - 复杂请求测试

## 🛠️ 生产环境配置建议

### 1. 限制允许的源

```java
// 生产环境不要使用 "*"
.allowedOrigins("https://yourdomain.com", "https://www.yourdomain.com")
```

### 2. 限制允许的方法

```java
.allowedMethods("GET", "POST", "PUT", "DELETE")
```

### 3. 限制允许的请求头

```java
.allowedHeaders("Content-Type", "Authorization", "X-Requested-With")
```

### 4. 配置凭据

```java
.allowCredentials(true)  // 如果需要携带cookies或认证信息
```

### 5. 设置合理的缓存时间

```java
.maxAge(3600)  // 1小时，根据实际需求调整
```

## 🐛 常见问题

### 1. 预检请求失败

**问题：** OPTIONS请求返回404或405错误

**解决方案：**
- 确保配置了OPTIONS方法
- 检查路径映射是否正确
- 使用`@RequestMapping`而不是`@GetMapping`等

### 2. 简单请求被阻止

**问题：** GET请求被CORS阻止

**解决方案：**
- 检查`allowedOrigins`配置
- 确保没有额外的请求头导致变成复杂请求

### 3. 带凭证的请求失败

**问题：** 携带cookies的请求失败

**解决方案：**
- 设置`allowCredentials(true)`
- 不能同时使用`allowedOrigins("*")`和`allowCredentials(true)`
- 使用`allowedOriginPatterns`替代

### 4. 自定义请求头被阻止

**问题：** 自定义请求头导致CORS失败

**解决方案：**
- 在`allowedHeaders`中添加自定义请求头
- 或者使用`allowedHeaders("*")`

## 📚 相关资源

- [Spring Boot CORS官方文档](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html#mvc-cors)
- [MDN CORS文档](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)
- [Spring Security CORS配置](https://docs.spring.io/spring-security/reference/servlet/integrations/cors.html)

## 📝 更新日志

- v1.0.0 - 初始版本，包含6种CORS配置方法
- 支持全局和局部CORS配置
- 提供完整的测试页面
- 包含生产环境配置建议