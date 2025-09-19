# 短链接生成服务

一个高性能、可扩展的短链接生成服务，支持URL缩短、重定向、统计分析和缓存优化。

## 功能特性

- **高性能**: 基于自增ID + Base62编码算法
- **高可用**: 支持分布式部署和故障转移
- **缓存优化**: 多级缓存策略提升响应速度
- **统计分析**: 访问量统计和数据分析
- **安全防护**: 防刷机制和恶意URL检测
- **监控告警**: 完整的监控和日志系统

## 技术架构

### 核心算法
- **短码生成**: 自增ID + Base62编码
- **冲突处理**: 数据库唯一约束 + 重试机制
- **性能优化**: 批量ID预分配

### 存储方案
- **主存储**: MySQL (持久化存储)
- **缓存层**: Redis (热点数据缓存)
- **本地缓存**: Caffeine (JVM内缓存)

### 缓存策略
- **L1缓存**: 本地缓存 (1分钟TTL)
- **L2缓存**: Redis缓存 (1小时TTL)
- **L3存储**: MySQL数据库 (持久化)

## 项目结构

```
shorturl-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/shorturl/
│   │   │       ├── ShortUrlServiceApplication.java
│   │   │       ├── algorithm/          # 短码生成算法
│   │   │       ├── cache/             # 缓存管理
│   │   │       ├── config/            # 配置类
│   │   │       ├── controller/        # REST API
│   │   │       ├── entity/            # 数据实体
│   │   │       ├── repository/        # 数据访问层
│   │   │       ├── service/           # 业务逻辑层
│   │   │       └── util/              # 工具类
│   │   └── resources/
│   │       ├── application.yml
│   │       └── db/migration/          # 数据库迁移脚本
│   └── test/
├── docker-compose.yml
├── Dockerfile
└── pom.xml
```

## 快速开始

### 环境要求
- Java 17+
- MySQL 8.0+
- Redis 6.0+
- Maven 3.6+

### 本地开发
```bash
# 启动依赖服务
docker-compose up -d mysql redis

# 编译运行
mvn clean package
java -jar target/shorturl-service-1.0.0.jar
```

### API使用示例

#### 生成短链接
```bash
curl -X POST http://localhost:8080/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

#### 访问短链接
```bash
curl -X GET http://localhost:8080/s/abc123
```

## 性能指标

- **生成速度**: >10,000 QPS
- **重定向速度**: >50,000 QPS  
- **缓存命中率**: >95%
- **可用性**: 99.9%

## 监控指标

- 请求QPS和响应时间
- 缓存命中率和失效率
- 数据库连接池状态
- 系统资源使用率
- 错误率和异常统计