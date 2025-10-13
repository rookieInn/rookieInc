# Spring Boot 图形验证码 - 快速开始

## 🚀 快速启动

### 方法一：使用Docker Compose（推荐）

```bash
# 1. 启动所有服务（包括Redis和应用）
docker-compose up -d

# 2. 查看日志
docker-compose logs -f app

# 3. 访问应用
# 首页: http://localhost:8080
# 演示: http://localhost:8080/demo
```

### 方法二：本地运行

#### 1. 安装依赖

**安装Java 11+**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# CentOS/RHEL
sudo yum install java-11-openjdk-devel

# 验证安装
java -version
```

**安装Maven**
```bash
# Ubuntu/Debian
sudo apt install maven

# CentOS/RHEL
sudo yum install maven

# 验证安装
mvn -version
```

**安装Redis**
```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# CentOS/RHEL
sudo yum install redis
sudo systemctl start redis

# 或使用Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

#### 2. 运行应用

```bash
# 编译项目
mvn clean compile

# 启动应用
mvn spring-boot:run

# 或使用启动脚本
./start.sh
```

## 📱 访问应用

- **首页**: http://localhost:8080
- **演示页面**: http://localhost:8080/demo
- **API接口**: http://localhost:8080/api/captcha/generate

## 🔧 API使用示例

### 生成验证码
```bash
curl http://localhost:8080/api/captcha/generate
```

### 验证验证码
```bash
curl -X POST http://localhost:8080/api/captcha/verify \
  -d "captchaId=your_captcha_id&captchaCode=your_input"
```

## 🛠️ 故障排除

### 1. 端口被占用
```bash
# 查看端口占用
netstat -tulpn | grep :8080
# 或
lsof -i :8080

# 杀死进程
kill -9 <PID>
```

### 2. Redis连接失败
```bash
# 检查Redis状态
redis-cli ping

# 启动Redis
sudo systemctl start redis-server
# 或
docker start redis
```

### 3. 编译失败
```bash
# 清理并重新编译
mvn clean
mvn compile
```

## 📋 功能特性

- ✅ 自动生成随机验证码
- ✅ 图形干扰效果（干扰线、干扰点）
- ✅ Redis缓存存储
- ✅ 自动过期机制
- ✅ RESTful API接口
- ✅ 响应式Web界面
- ✅ 可配置参数

## 🔒 安全建议

1. 生产环境使用HTTPS
2. 配置Redis访问密码
3. 添加IP访问限制
4. 监控验证码使用情况

## 📞 技术支持

如有问题，请检查：
1. Java版本是否为11+
2. Redis服务是否运行
3. 端口8080是否被占用
4. 防火墙设置是否正确