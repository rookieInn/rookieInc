# MyBatis JSON字段查询示例

本项目演示如何在MyBatis中判断某个ID是否在数据库JSON字段中。

## 项目结构

```
src/
├── main/
│   ├── java/
│   │   └── com/example/
│   │       ├── entity/
│   │       │   └── User.java                    # 用户实体类
│   │       ├── mapper/
│   │       │   └── UserMapper.java              # MyBatis Mapper接口
│   │       ├── service/
│   │       │   └── UserService.java             # 用户服务类
│   │       ├── typehandler/
│   │       │   └── JsonListTypeHandler.java     # JSON类型处理器
│   │       ├── config/
│   │       │   └── MyBatisConfig.java           # MyBatis配置
│   │       └── MyBatisJsonExample.java          # 示例主类
│   └── resources/
│       ├── mapper/
│       │   └── UserMapper.xml                   # MyBatis XML映射文件
│       ├── mybatis-config.xml                   # MyBatis配置文件
│       └── database.properties                  # 数据库连接配置
├── database_init.sql                            # 数据库初始化脚本
└── pom.xml                                      # Maven依赖配置
```

## 核心功能

### 1. 判断ID是否在JSON字段中

```java
// 检查用户是否拥有指定角色
boolean hasRole = userService.hasRole(userId, roleId);
```

对应的SQL：
```xml
<select id="isRoleIdInJson" resultType="boolean">
    SELECT JSON_CONTAINS(role_ids, JSON_QUOTE(#{roleId}))
    FROM users 
    WHERE id = #{userId}
</select>
```

### 2. 查询包含指定ID的所有记录

```java
// 获取拥有指定角色的所有用户
List<User> users = userService.getUsersByRole(roleId);
```

对应的SQL：
```xml
<select id="selectUsersByRoleId" resultMap="UserResultMap">
    SELECT id, name, email, role_ids
    FROM users 
    WHERE JSON_CONTAINS(role_ids, JSON_QUOTE(#{roleId}))
</select>
```

### 3. 查询包含任意指定ID的记录

```java
// 获取拥有任意指定角色的用户
List<User> users = userService.getUsersByAnyRole(Arrays.asList(1L, 2L, 3L));
```

对应的SQL：
```xml
<select id="selectUsersByAnyRoleId" resultMap="UserResultMap">
    SELECT id, name, email, role_ids
    FROM users 
    WHERE JSON_OVERLAPS(role_ids, JSON_ARRAY(
    <foreach collection="roleIds" item="roleId" separator=",">
        #{roleId}
    </foreach>
    ))
</select>
```

### 4. 查询包含所有指定ID的记录

```java
// 获取拥有所有指定角色的用户
List<User> users = userService.getUsersByAllRoles(Arrays.asList(1L, 2L));
```

对应的SQL：
```xml
<select id="selectUsersByAllRoleIds" resultMap="UserResultMap">
    SELECT id, name, email, role_ids
    FROM users 
    WHERE 
    <foreach collection="roleIds" item="roleId" separator=" AND ">
        JSON_CONTAINS(role_ids, JSON_QUOTE(#{roleId}))
    </foreach>
</select>
```

## 数据库表结构

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    role_ids JSON COMMENT '角色ID列表，存储为JSON数组，如[1,2,3,4,5]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 主要MySQL JSON函数

1. **JSON_CONTAINS(json_doc, val)**: 检查JSON文档是否包含指定值
2. **JSON_OVERLAPS(json_doc1, json_doc2)**: 检查两个JSON文档是否有重叠
3. **JSON_ARRAY(val1, val2, ...)**: 创建JSON数组
4. **JSON_QUOTE(str)**: 将字符串转换为JSON字符串
5. **JSON_EXTRACT(json_doc, path)**: 从JSON文档中提取值
6. **JSON_SEARCH(json_doc, one_or_all, search_str)**: 在JSON文档中搜索字符串

## 运行示例

1. 确保MySQL数据库运行并执行 `database_init.sql` 初始化数据
2. 修改 `database.properties` 中的数据库连接信息
3. 运行 `MyBatisJsonExample.java` 查看示例输出

## 示例输出

```
=== MyBatis JSON字段查询示例 ===

=== 创建测试数据 ===
测试数据创建完成

=== 演示JSON字段查询方法 ===

1. 检查用户是否拥有指定角色:
张三拥有角色2: true
张三拥有角色4: false

2. 查询拥有指定角色的所有用户:
拥有角色2的用户: [User{id=1, name='张三', email='zhangsan@example.com', roleIds=[1, 2, 3]}, User{id=2, name='李四', email='lisi@example.com', roleIds=[2, 4, 5]}]

3. 查询拥有任意指定角色的用户:
拥有角色1或4的用户: [User{id=1, name='张三', email='zhangsan@example.com', roleIds=[1, 2, 3]}, User{id=2, name='李四', email='lisi@example.com', roleIds=[2, 4, 5]}, User{id=3, name='王五', email='wangwu@example.com', roleIds=[1, 5]}]

4. 查询拥有所有指定角色的用户:
同时拥有角色1和5的用户: [User{id=3, name='王五', email='wangwu@example.com', roleIds=[1, 5]}]

5. 统计拥有指定角色的用户数量:
拥有角色1的用户数量: 3
拥有角色2的用户数量: 2
拥有角色6的用户数量: 0
```

## 注意事项

1. 确保MySQL版本支持JSON数据类型（5.7+）
2. 为JSON字段创建适当的索引以提高查询性能
3. 使用类型处理器处理Java对象与JSON字符串的转换
4. 注意SQL注入防护，使用参数化查询