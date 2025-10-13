# 使用OpenJDK 11作为基础镜像
FROM openjdk:11-jdk-slim

# 设置工作目录
WORKDIR /app

# 复制Maven配置文件
COPY pom.xml .

# 复制源代码
COPY src ./src

# 安装Maven
RUN apt-get update && \
    apt-get install -y maven && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 编译项目
RUN mvn clean compile

# 暴露端口
EXPOSE 8080

# 启动应用
CMD ["mvn", "spring-boot:run"]