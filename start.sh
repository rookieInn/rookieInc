#!/bin/bash

echo "================================="
echo "MyBatis Plus CRUD 项目启动脚本"
echo "================================="

# 检查Java环境
if ! command -v java &> /dev/null; then
    echo "错误：未找到Java环境，请先安装JDK 11+"
    exit 1
fi

# 检查Maven环境
if ! command -v mvn &> /dev/null; then
    echo "错误：未找到Maven环境，请先安装Maven 3.6+"
    exit 1
fi

echo "Java版本："
java -version

echo ""
echo "Maven版本："
mvn -version

echo ""
echo "开始编译项目..."
mvn clean compile -q

if [ $? -eq 0 ]; then
    echo "编译成功！"
    echo ""
    echo "项目结构："
    echo "├── src/main/java/com/example/mybatisplus/"
    echo "│   ├── entity/User.java          # 用户实体类"
    echo "│   ├── mapper/UserMapper.java    # 数据访问层"
    echo "│   ├── service/                  # 业务逻辑层"
    echo "│   │   ├── UserService.java"
    echo "│   │   └── impl/UserServiceImpl.java"
    echo "│   ├── controller/UserController.java  # 控制器层"
    echo "│   ├── config/MybatisPlusConfig.java   # 配置类"
    echo "│   └── MybatisPlusApplication.java     # 启动类"
    echo "├── src/main/resources/"
    echo "│   ├── application.yml           # 配置文件"
    echo "│   ├── mapper/UserMapper.xml     # MyBatis XML"
    echo "│   ├── schema.sql               # 数据库表结构"
    echo "│   └── data.sql                 # 测试数据"
    echo "└── src/test/java/               # 测试代码"
    echo ""
    echo "功能特性："
    echo "✅ 完整的CRUD操作（增删改查）"
    echo "✅ 分页查询"
    echo "✅ 条件查询"
    echo "✅ 批量操作"
    echo "✅ 逻辑删除"
    echo "✅ 乐观锁"
    echo "✅ 自动填充"
    echo "✅ 数据校验"
    echo "✅ 异常处理"
    echo "✅ RESTful API"
    echo ""
    echo "API接口："
    echo "GET    /api/users/page           # 分页查询用户"
    echo "GET    /api/users/{id}           # 根据ID查询用户"
    echo "POST   /api/users                # 创建用户"
    echo "PUT    /api/users/{id}           # 更新用户"
    echo "DELETE /api/users/{id}           # 删除用户"
    echo "DELETE /api/users/batch          # 批量删除"
    echo "PUT    /api/users/status/batch   # 批量更新状态"
    echo ""
    echo "启动项目："
    echo "mvn spring-boot:run"
    echo ""
    echo "访问地址："
    echo "http://localhost:8080"
    echo "http://localhost:8080/h2-console"
    echo ""
    echo "================================="
else
    echo "编译失败，请检查代码！"
    exit 1
fi