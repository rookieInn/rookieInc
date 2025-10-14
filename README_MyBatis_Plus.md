# MyBatis Plus CRUD 示例项目

这是一个基于Spring Boot和MyBatis Plus的完整CRUD操作示例项目，包含了Controller、Service、Mapper层的完整代码模板。

## 项目结构

```
src/
├── main/
│   ├── java/
│   │   └── com/example/mybatisplus/
│   │       ├── entity/          # 实体类
│   │       │   └── User.java
│   │       ├── mapper/          # Mapper接口
│   │       │   └── UserMapper.java
│   │       ├── service/         # Service层
│   │       │   ├── UserService.java
│   │       │   └── impl/
│   │       │       └── UserServiceImpl.java
│   │       ├── controller/      # Controller层
│   │       │   └── UserController.java
│   │       ├── config/          # 配置类
│   │       │   └── MybatisPlusConfig.java
│   │       └── MybatisPlusApplication.java
│   └── resources/
│       ├── mapper/              # MyBatis XML文件
│       │   └── UserMapper.xml
│       ├── application.yml      # 配置文件
│       ├── schema.sql          # 数据库表结构
│       └── data.sql            # 测试数据
└── test/
    └── java/
        └── com/example/mybatisplus/
            └── UserControllerTest.java
```

## 功能特性

### 1. 实体类 (Entity)
- 使用Lombok简化代码
- 支持MyBatis Plus注解
- 包含逻辑删除、乐观锁、自动填充等特性

### 2. Mapper层
- 继承BaseMapper获得基础CRUD操作
- 自定义查询方法
- 支持分页查询
- 批量操作

### 3. Service层
- 业务逻辑封装
- 事务管理
- 数据校验
- 异常处理

### 4. Controller层
- RESTful API设计
- 统一返回格式
- 参数校验
- 异常处理

## API接口

### 用户管理接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/users/page` | 分页查询用户列表 |
| GET | `/api/users/{id}` | 根据ID查询用户详情 |
| GET | `/api/users/username/{username}` | 根据用户名查询用户 |
| GET | `/api/users/status/{status}` | 根据状态查询用户列表 |
| POST | `/api/users` | 创建用户 |
| PUT | `/api/users/{id}` | 更新用户信息 |
| DELETE | `/api/users/{id}` | 删除用户 |
| DELETE | `/api/users/batch` | 批量删除用户 |
| PUT | `/api/users/status/batch` | 批量更新用户状态 |
| GET | `/api/users/check/username` | 检查用户名是否存在 |
| GET | `/api/users/check/email` | 检查邮箱是否存在 |
| GET | `/api/users/check/phone` | 检查手机号是否存在 |
| GET | `/api/users/statistics` | 统计用户数量 |

### 请求示例

#### 1. 分页查询用户
```bash
GET /api/users/page?current=1&size=10&username=admin&status=1
```

#### 2. 创建用户
```bash
POST /api/users
Content-Type: application/json

{
    "username": "newuser",
    "password": "password123",
    "email": "newuser@example.com",
    "phone": "13800138000",
    "realName": "新用户",
    "age": 25,
    "gender": 1,
    "status": 1
}
```

#### 3. 更新用户
```bash
PUT /api/users/1
Content-Type: application/json

{
    "realName": "更新后的姓名",
    "age": 26
}
```

#### 4. 批量更新状态
```bash
PUT /api/users/status/batch
Content-Type: application/json

{
    "ids": [1, 2, 3],
    "status": 0
}
```

## 运行项目

### 1. 环境要求
- JDK 11+
- Maven 3.6+

### 2. 启动项目
```bash
# 编译项目
mvn clean compile

# 运行项目
mvn spring-boot:run
```

### 3. 访问地址
- 应用首页：http://localhost:8080
- H2控制台：http://localhost:8080/h2-console
- 数据库连接信息：
  - JDBC URL: `jdbc:h2:mem:testdb`
  - 用户名: `sa`
  - 密码: (空)

## 配置说明

### 数据库配置
项目默认使用H2内存数据库，如需使用MySQL，请修改`application.yml`中的数据库配置：

```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/mybatis_plus_demo?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: your_password
```

### MyBatis Plus配置
- 分页插件：支持分页查询
- 乐观锁插件：支持版本控制
- 自动填充：自动填充创建时间和更新时间
- 逻辑删除：支持软删除

## 测试

运行测试类：
```bash
mvn test
```

## 技术栈

- Spring Boot 2.7.18
- MyBatis Plus 3.5.3.1
- H2 Database (测试)
- MySQL (生产)
- Lombok
- Maven

## 扩展功能

### 1. 添加新的实体类
1. 在`entity`包下创建实体类
2. 在`mapper`包下创建Mapper接口
3. 在`service`包下创建Service接口和实现类
4. 在`controller`包下创建Controller类

### 2. 自定义查询
在Mapper接口中添加自定义方法，在对应的XML文件中编写SQL。

### 3. 添加缓存
可以集成Redis实现缓存功能。

### 4. 添加权限控制
可以集成Spring Security实现权限控制。

## 注意事项

1. 实体类需要添加`@TableName`注解指定表名
2. 主键字段需要添加`@TableId`注解
3. 逻辑删除字段需要添加`@TableLogic`注解
4. 乐观锁字段需要添加`@Version`注解
5. 自动填充字段需要添加`@TableField(fill = FieldFill.INSERT)`或`@TableField(fill = FieldFill.INSERT_UPDATE)`注解

## 许可证

MIT License