# 多阶段构建Dockerfile
FROM maven:3.9.4-openjdk-17-slim AS build

# 设置工作目录
WORKDIR /app

# 复制pom.xml并下载依赖
COPY pom.xml .
RUN mvn dependency:go-offline -B

# 复制源代码并构建
COPY src ./src
RUN mvn clean package -DskipTests

# 运行阶段
FROM openjdk:17-jre-slim

# 安装必要的工具
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建应用用户
RUN groupadd -r shorturl && useradd -r -g shorturl shorturl

# 设置工作目录
WORKDIR /app

# 复制jar文件
COPY --from=build /app/target/shorturl-service-*.jar app.jar

# 创建日志目录
RUN mkdir -p /app/logs && chown -R shorturl:shorturl /app

# 切换到应用用户
USER shorturl

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# 启动应用
ENTRYPOINT ["java", "-jar", "app.jar"]