# Spring Boot API 处理时间计算

这是一个Spring Boot应用程序，演示如何计算后端接口的处理时间。

## 功能特性

1. **拦截器方式** - 使用HandlerInterceptor计算API请求处理时间
2. **AOP方式** - 使用@Timing注解和AOP切面计算方法执行时间
3. **多种测试接口** - 提供各种模拟业务场景的测试接口
4. **详细日志记录** - 记录处理时间到日志和响应头

## 项目结构

```
src/main/java/com/example/springbootapitiming/
├── SpringBootApiTimingApplication.java    # 主应用程序类
├── annotation/
│   └── Timing.java                       # 处理时间注解
├── aspect/
│   └── TimingAspect.java                 # AOP切面
├── config/
│   └── WebConfig.java                    # Web配置
├── controller/
│   ├── ApiController.java                # API控制器
│   └── ServiceController.java            # 服务控制器
├── interceptor/
│   └── ApiTimingInterceptor.java         # 处理时间拦截器
└── service/
    └── BusinessService.java              # 业务服务类
```

## 快速开始

### 1. 编译和运行

```bash
# 编译项目
mvn clean compile

# 运行应用程序
mvn spring-boot:run
```

### 2. 测试接口

应用程序启动后，可以通过以下接口测试处理时间计算：

#### 基础API接口（使用拦截器）

- `GET /api/quick` - 快速响应接口
- `GET /api/process?delay=1000` - 模拟处理时间接口
- `GET /api/database?records=10` - 数据库查询模拟接口
- `POST /api/file?filename=test.txt&size=1024` - 文件处理模拟接口
- `GET /api/complex?steps=5` - 复杂业务逻辑模拟接口
- `GET /api/health` - 健康检查接口（不计算处理时间）

#### 服务接口（使用AOP注解）

- `GET /api/service/quick` - 快速业务接口
- `GET /api/service/slow` - 慢速业务接口
- `GET /api/service/database?records=20` - 数据库操作接口
- `POST /api/service/file?filename=test.txt&fileSize=2048` - 文件处理接口
- `GET /api/service/calculation?iterations=100000` - 复杂计算接口

### 3. 查看处理时间

#### 方式1：查看日志
应用程序会在控制台输出详细的处理时间日志：

```
2024-01-01 12:00:00.000 [http-nio-8080-exec-1] INFO  c.e.s.i.ApiTimingInterceptor - API请求开始: GET /api/quick
2024-01-01 12:00:00.100 [http-nio-8080-exec-1] INFO  c.e.s.i.ApiTimingInterceptor - API请求完成: GET /api/quick - 处理时间: 100ms, 状态码: 200
```

#### 方式2：查看响应头
每个API响应都会包含处理时间信息：

```
X-Processing-Time: 100
X-Processing-Time-Unit: ms
```

#### 方式3：查看AOP日志
使用@Timing注解的方法会输出执行时间：

```
2024-01-01 12:00:00.000 [http-nio-8080-exec-1] INFO  c.e.s.a.TimingAspect - 方法执行完成: 快速业务处理 - 执行时间: 50ms
```

## 配置说明

### 拦截器配置
在`WebConfig.java`中配置拦截器：

```java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    registry.addInterceptor(apiTimingInterceptor)
            .addPathPatterns("/api/**")  // 只拦截 /api/** 路径的请求
            .excludePathPatterns("/api/health"); // 排除健康检查接口
}
```

### 日志配置
在`application.yml`中配置日志级别：

```yaml
logging:
  level:
    com.example.springbootapitiming: INFO
    org.springframework.web: DEBUG
```

## 使用场景

1. **性能监控** - 监控API接口的响应时间
2. **性能优化** - 识别慢接口并进行优化
3. **系统监控** - 集成到监控系统中
4. **调试分析** - 分析业务方法的执行时间

## 扩展功能

### 1. 集成监控系统
可以将处理时间数据发送到监控系统（如Prometheus、InfluxDB等）。

### 2. 数据库存储
可以将处理时间数据存储到数据库中，用于历史分析和报表。

### 3. 告警机制
可以设置处理时间阈值，超过阈值时发送告警。

### 4. 统计报表
可以生成处理时间的统计报表和趋势分析。

## 注意事项

1. 拦截器会为每个请求增加少量性能开销
2. AOP切面只对使用@Timing注解的方法生效
3. 生产环境中建议调整日志级别以减少日志输出
4. 可以根据需要调整拦截器的路径匹配规则