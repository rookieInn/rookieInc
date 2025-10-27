# Java接入Fluentd采集日志

本项目演示如何在Java应用中集成Fluentd进行日志采集，支持多种日志输出方式和实时日志传输。

## 功能特性

- ✅ 自定义Fluentd Appender for Log4j2
- ✅ 支持结构化日志输出
- ✅ 异步日志传输，提高性能
- ✅ 支持MDC（Mapped Diagnostic Context）
- ✅ 支持异常堆栈跟踪
- ✅ 支持Marker分类日志
- ✅ Docker容器化部署
- ✅ 集成Elasticsearch和Kibana（可选）

## 项目结构

```
├── src/main/java/com/example/fluentd/
│   ├── FluentdAppender.java          # 自定义Fluentd Appender
│   └── FluentdLoggingExample.java    # 示例应用程序
├── src/main/resources/
│   └── log4j2.xml                    # Log4j2配置文件
├── fluentd.conf                      # Fluentd配置文件
├── docker-compose-fluentd.yml        # Docker Compose配置
├── Dockerfile.fluentd               # Java应用Dockerfile
├── start-fluentd-demo.sh            # 演示启动脚本
└── pom.xml                          # Maven依赖配置
```

## 快速开始

### 1. 环境要求

- Java 11+
- Maven 3.6+
- Docker & Docker Compose

### 2. 运行演示

```bash
# 运行完整演示
./start-fluentd-demo.sh
```

### 3. 手动运行步骤

```bash
# 1. 构建项目
mvn clean package

# 2. 启动Fluentd
docker-compose -f docker-compose-fluentd.yml up -d fluentd

# 3. 运行Java应用
java -cp target/classes:target/dependency/* com.example.fluentd.FluentdLoggingExample
```

## 配置说明

### Log4j2配置

`src/main/resources/log4j2.xml` 文件配置了三种日志输出方式：

1. **控制台输出** - 用于开发调试
2. **文件输出** - 本地日志文件存储
3. **Fluentd输出** - 发送到Fluentd服务器

```xml
<FluentdAppender name="FluentdAppender" 
                tag="java.logs" 
                host="localhost" 
                port="24224"
                timeout="3000"
                bufferCapacity="8192">
    <PatternLayout pattern="%d{yyyy-MM-dd HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
</FluentdAppender>
```

### Fluentd配置

`fluentd.conf` 文件配置了日志接收和处理规则：

- **输入源**: 监听24224端口接收日志
- **过滤器**: 解析JSON格式的日志数据
- **输出**: 同时输出到控制台和文件

## 使用方式

### 基本日志记录

```java
private static final Logger logger = LogManager.getLogger(YourClass.class);

// 基本日志
logger.info("这是一条信息日志");
logger.warn("这是一条警告日志");
logger.error("这是一条错误日志");

// 带参数的日志
logger.info("用户 {} 执行了操作 {}", userId, operation);
```

### 使用Marker分类日志

```java
private static final Marker BUSINESS_MARKER = MarkerManager.getMarker("BUSINESS");
private static final Marker SECURITY_MARKER = MarkerManager.getMarker("SECURITY");

logger.info(BUSINESS_MARKER, "业务操作日志");
logger.warn(SECURITY_MARKER, "安全警告日志");
```

### 使用MDC添加上下文信息

```java
// 设置MDC数据
ThreadContext.put("userId", "12345");
ThreadContext.put("sessionId", "abc123");

// 记录日志（会自动包含MDC数据）
logger.info("用户操作日志");

// 清理MDC数据
ThreadContext.clearAll();
```

### 记录异常信息

```java
try {
    // 业务逻辑
} catch (Exception e) {
    logger.error("操作失败", e); // 会自动记录异常堆栈
}
```

## 日志数据结构

发送到Fluentd的日志数据包含以下字段：

```json
{
  "timestamp": 1640995200000,
  "level": "INFO",
  "logger": "com.example.fluentd.FluentdLoggingExample",
  "thread": "main",
  "message": "这是一条信息日志",
  "exception": "异常信息（如果有）",
  "stackTrace": "堆栈跟踪（如果有）",
  "mdc": {
    "userId": "12345",
    "sessionId": "abc123"
  }
}
```

## Docker部署

### 启动所有服务

```bash
# 启动Fluentd、Elasticsearch和Kibana
docker-compose -f docker-compose-fluentd.yml up -d

# 查看服务状态
docker-compose -f docker-compose-fluentd.yml ps
```

### 访问服务

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Fluentd日志**: `docker logs fluentd-server`

## 性能优化

### 1. 异步日志传输

使用AsyncAppender可以避免阻塞主线程：

```xml
<AsyncAppender name="AsyncFluentd" bufferSize="1024">
    <FluentdAppender name="FluentdAppender" ... />
</AsyncAppender>
```

### 2. 批量发送

Fluentd Appender支持批量发送日志，减少网络开销：

```java
// 在FluentdAppender中设置
bufferCapacity="8192"  // 缓冲区大小
timeout="3000"         // 超时时间
```

### 3. 日志级别控制

生产环境建议使用INFO级别，避免过多DEBUG日志：

```xml
<Root level="INFO">
    <AppenderRef ref="FluentdAppender"/>
</Root>
```

## 故障排除

### 1. Fluentd连接失败

检查Fluentd服务是否运行：
```bash
docker logs fluentd-server
```

检查网络连接：
```bash
telnet localhost 24224
```

### 2. 日志未发送到Fluentd

- 检查Log4j2配置中的host和port设置
- 查看应用日志中的错误信息
- 确认Fluentd配置文件正确

### 3. 性能问题

- 调整AsyncAppender的bufferSize
- 增加Fluentd的buffer配置
- 考虑使用日志采样

## 扩展功能

### 1. 集成Elasticsearch

修改Fluentd配置添加Elasticsearch输出：

```conf
<match java.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name java-logs
  type_name _doc
</match>
```

### 2. 添加更多输出

可以添加Kafka、MongoDB等输出：

```conf
<match java.logs>
  @type kafka2
  brokers kafka:9092
  topic java-logs
</match>
```

### 3. 日志过滤和转换

使用Fluentd过滤器处理日志：

```conf
<filter java.logs>
  @type grep
  <regexp>
    key level
    pattern /ERROR|WARN/
  </regexp>
</filter>
```

## 最佳实践

1. **结构化日志**: 使用JSON格式输出结构化日志
2. **上下文信息**: 充分利用MDC添加上下文信息
3. **日志分类**: 使用Marker对日志进行分类
4. **异常处理**: 记录完整的异常堆栈信息
5. **性能监控**: 监控日志传输性能，避免影响业务
6. **日志轮转**: 配置日志文件轮转策略
7. **安全考虑**: 避免在日志中记录敏感信息

## 许可证

MIT License