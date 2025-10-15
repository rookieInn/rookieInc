# 多级分类系统 / Multi-Level Category System

这是一个完整的Java多级分类系统，支持分类的存储、查询、查询全部、查询树状结构等功能。

This is a complete Java multi-level category system that supports category storage, querying, querying all, and tree structure querying.

## 功能特性 / Features

### 核心功能 / Core Features
- ✅ **多级分类支持** / Multi-level category support
- ✅ **分类存储** / Category storage
- ✅ **分类查询** / Category querying
- ✅ **查询全部分类** / Query all categories
- ✅ **树状结构查询** / Tree structure querying
- ✅ **分类搜索** / Category search
- ✅ **分类移动** / Category moving
- ✅ **软删除** / Soft delete
- ✅ **REST API** / REST API endpoints

### 技术特性 / Technical Features
- ✅ **内存存储** / In-memory storage
- ✅ **JPA数据库支持** / JPA database support
- ✅ **Spring Boot集成** / Spring Boot integration
- ✅ **RESTful API** / RESTful API
- ✅ **JSON序列化** / JSON serialization

## 项目结构 / Project Structure

```
src/main/java/com/example/category/
├── CategoryApplication.java              # Spring Boot主应用类
├── model/
│   └── Category.java                    # 分类模型类（内存版本）
├── entity/
│   └── CategoryEntity.java              # 分类JPA实体类（数据库版本）
├── repository/
│   ├── CategoryRepository.java          # 分类仓库接口
│   ├── CategoryJpaRepository.java       # JPA仓库接口
│   └── impl/
│       └── InMemoryCategoryRepository.java  # 内存存储实现
├── service/
│   └── CategoryService.java             # 分类服务类
├── controller/
│   ├── CategoryController.java          # 分类控制器（普通版本）
│   └── CategoryRestController.java      # REST控制器（Spring Boot版本）
└── demo/
    └── CategoryDemo.java                # 演示程序
```

## 快速开始 / Quick Start

### 1. 运行演示程序 / Run Demo Application

```bash
# 编译项目
mvn compile

# 运行演示程序
mvn exec:java -Dexec.mainClass="com.example.category.demo.CategoryDemo"
```

### 2. 运行Spring Boot应用 / Run Spring Boot Application

```bash
# 运行Spring Boot应用
mvn spring-boot:run
```

应用将在 `http://localhost:8080` 启动。

The application will start at `http://localhost:8080`.

### 3. 访问H2数据库控制台 / Access H2 Database Console

访问 `http://localhost:8080/h2-console` 查看数据库内容。

Access `http://localhost:8080/h2-console` to view database content.

## API接口 / API Endpoints

### 基础CRUD操作 / Basic CRUD Operations

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/categories` | 创建分类 |
| GET | `/api/categories/{id}` | 根据ID获取分类 |
| GET | `/api/categories` | 获取所有分类 |
| PUT | `/api/categories/{id}` | 更新分类 |
| DELETE | `/api/categories/{id}` | 删除分类 |

### 查询操作 / Query Operations

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/categories/active` | 获取所有激活的分类 |
| GET | `/api/categories/root` | 获取根分类 |
| GET | `/api/categories/parent/{parentId}` | 根据父ID获取子分类 |
| GET | `/api/categories/tree` | 获取完整分类树 |
| GET | `/api/categories/{id}/subtree` | 获取指定分类的子树 |
| GET | `/api/categories/{id}/path` | 获取分类的完整路径 |
| GET | `/api/categories/search?name={name}` | 根据名称搜索分类 |
| GET | `/api/categories/level/{level}` | 根据层级获取分类 |

### 高级操作 / Advanced Operations

| 方法 | 路径 | 描述 |
|------|------|------|
| PUT | `/api/categories/{id}/move?parentId={parentId}` | 移动分类到新的父分类下 |
| DELETE | `/api/categories/{id}/soft` | 软删除分类 |

## 使用示例 / Usage Examples

### 1. 创建分类 / Create Categories

```java
// 创建根分类
Category electronics = new Category("电子产品", "各种电子设备和配件", null);
electronics = categoryService.createCategory(electronics);

// 创建子分类
Category smartphones = new Category("智能手机", "各种品牌的智能手机", electronics.getId());
smartphones = categoryService.createCategory(smartphones);
```

### 2. 查询分类 / Query Categories

```java
// 获取所有分类
List<Category> allCategories = categoryService.getAllCategories();

// 获取根分类
List<Category> rootCategories = categoryService.getRootCategories();

// 获取子分类
List<Category> childCategories = categoryService.getChildCategories(electronics.getId());

// 获取分类树
List<Category> categoryTree = categoryService.getCategoryTree();
```

### 3. 搜索分类 / Search Categories

```java
// 根据名称搜索
List<Category> searchResults = categoryService.searchCategoriesByName("手机");

// 根据层级搜索
List<Category> level2Categories = categoryService.getCategoriesByLevel(2);
```

### 4. 移动分类 / Move Categories

```java
// 移动分类到新的父分类下
Category movedCategory = categoryService.moveCategory(categoryId, newParentId);
```

## 数据模型 / Data Model

### Category实体属性 / Category Entity Properties

| 属性 | 类型 | 描述 |
|------|------|------|
| id | Long | 分类ID（主键） |
| name | String | 分类名称 |
| description | String | 分类描述 |
| parentId | Long | 父分类ID |
| level | Integer | 分类层级 |
| path | String | 分类路径（如：/1/2/3/） |
| sortOrder | Integer | 排序顺序 |
| isActive | Boolean | 是否激活 |
| createTime | LocalDateTime | 创建时间 |
| updateTime | LocalDateTime | 更新时间 |
| children | List<Category> | 子分类列表（用于树形结构） |

## 树形结构 / Tree Structure

系统支持完整的树形结构操作：

The system supports complete tree structure operations:

- **构建树形结构** / Build tree structure
- **查询子树** / Query subtrees
- **获取分类路径** / Get category paths
- **移动分类** / Move categories
- **防止循环引用** / Prevent circular references

## 配置说明 / Configuration

### 数据库配置 / Database Configuration

在 `application.properties` 中配置数据库连接：

Configure database connection in `application.properties`:

```properties
# H2内存数据库（演示用）
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.username=sa
spring.datasource.password=password

# MySQL数据库（生产环境）
# spring.datasource.url=jdbc:mysql://localhost:3306/category_db
# spring.datasource.username=root
# spring.datasource.password=password
```

## 扩展功能 / Extended Features

### 1. 数据库持久化 / Database Persistence

系统提供了JPA实体类 `CategoryEntity` 和对应的仓库接口 `CategoryJpaRepository`，支持数据库持久化。

The system provides JPA entity class `CategoryEntity` and corresponding repository interface `CategoryJpaRepository` for database persistence.

### 2. 缓存支持 / Cache Support

可以通过Spring Cache注解添加缓存支持：

Cache support can be added through Spring Cache annotations:

```java
@Cacheable("categories")
public List<Category> getCategoryTree() {
    // 实现逻辑
}
```

### 3. 权限控制 / Permission Control

可以集成Spring Security实现权限控制：

Permission control can be implemented by integrating Spring Security:

```java
@PreAuthorize("hasRole('ADMIN')")
public Category createCategory(Category category) {
    // 实现逻辑
}
```

## 测试 / Testing

### 运行演示程序 / Run Demo Program

```bash
mvn exec:java -Dexec.mainClass="com.example.category.demo.CategoryDemo"
```

### 运行单元测试 / Run Unit Tests

```bash
mvn test
```

## 许可证 / License

MIT License

## 贡献 / Contributing

欢迎提交Issue和Pull Request！

Issues and Pull Requests are welcome!