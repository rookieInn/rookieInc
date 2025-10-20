# 网易云脏字过滤 Java SDK

[![Maven Central](https://img.shields.io/maven-central/v/com.netease/netease-profanity-filter.svg)](https://mvnrepository.com/artifact/com.netease/netease-profanity-filter)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Java Version](https://img.shields.io/badge/Java-11%2B-orange.svg)](https://www.oracle.com/java/)

网易云脏字过滤Java SDK，提供文本和图片内容审核功能，帮助开发者快速集成内容安全检测能力。

## 功能特性

- ✅ **文本内容审核** - 支持敏感词检测、垃圾信息识别
- ✅ **图片内容审核** - 支持色情、暴力、政治敏感等图片检测
- ✅ **多种输入方式** - 支持URL、Base64、文件路径等多种图片输入方式
- ✅ **异步处理** - 提供异步API，支持高并发场景
- ✅ **批量处理** - 支持批量文本和图片审核
- ✅ **详细结果** - 返回详细的检测结果和置信度
- ✅ **易于集成** - 简单的API设计，快速集成到现有项目

## 快速开始

### 1. 添加依赖

在您的 `pom.xml` 中添加以下依赖：

```xml
<dependency>
    <groupId>com.netease</groupId>
    <artifactId>netease-profanity-filter</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 2. 配置客户端

```java
import com.netease.profanity.filter.ProfanityFilterConfig;
import com.netease.profanity.filter.ProfanityFilterService;

// 创建配置
ProfanityFilterConfig config = new ProfanityFilterConfig(
    "your_access_key_id",      // 网易云API访问密钥ID
    "your_access_key_secret",  // 网易云API访问密钥
    "https://censor.netease.im" // API服务地址
);

// 创建服务实例
ProfanityFilterService service = new ProfanityFilterService(config);
```

### 3. 文本内容审核

```java
// 同步文本审核
FilterResponse response = service.filterText("这是一段需要审核的文本内容", "business_id");
if (response.isPass()) {
    System.out.println("文本审核通过");
} else if (response.isReject()) {
    System.out.println("文本审核不通过，敏感词：" + response.getSensitiveWords());
}

// 异步文本审核
CompletableFuture<FilterResponse> future = service.filterTextAsync("异步审核文本", "business_id");
future.thenAccept(result -> {
    if (result.isPass()) {
        System.out.println("异步文本审核通过");
    }
});
```

### 4. 图片内容审核

```java
// 通过URL审核图片
FilterResponse response = service.filterImage("https://example.com/image.jpg", "business_id");

// 通过Base64数据审核图片
String base64Data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...";
FilterResponse response = service.filterImageBase64(base64Data, "business_id");

// 通过文件路径审核图片
FilterResponse response = service.filterImageFile("/path/to/image.jpg", "business_id");
```

### 5. 批量处理

```java
// 批量文本审核
String[] texts = {"文本1", "文本2", "文本3"};
CompletableFuture<FilterResponse[]> future = service.filterTextsAsync(texts, "batch_business");
FilterResponse[] results = future.get();

// 批量图片审核
String[] imageUrls = {"https://example.com/image1.jpg", "https://example.com/image2.jpg"};
CompletableFuture<FilterResponse[]> future = service.filterImagesAsync(imageUrls, "batch_business");
FilterResponse[] results = future.get();
```

## API 参考

### ProfanityFilterConfig

配置类，用于设置API访问参数。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accessKeyId | String | 是 | 网易云API访问密钥ID |
| accessKeySecret | String | 是 | 网易云API访问密钥 |
| endpoint | String | 否 | API服务地址，默认为 https://censor.netease.im |
| timeout | int | 否 | 请求超时时间（毫秒），默认30000 |
| connectTimeout | int | 否 | 连接超时时间（毫秒），默认10000 |
| debug | boolean | 否 | 是否启用调试模式，默认false |

### FilterResponse

审核结果响应类。

| 字段 | 类型 | 说明 |
|------|------|------|
| code | Integer | 响应码，200表示成功 |
| message | String | 响应消息 |
| action | Integer | 检测结果：0-通过，1-不通过，2-疑似 |
| confidence | Double | 置信度（0-100） |
| sensitiveWords | List<String> | 检测到的敏感词列表 |
| details | List<FilterDetail> | 详细信息 |
| isPass() | boolean | 是否通过检测 |
| isReject() | boolean | 是否不通过检测 |
| isSuspect() | boolean | 是否为疑似内容 |

### 主要方法

#### 文本审核

- `filterText(String text)` - 同步文本审核
- `filterText(String text, String businessId)` - 同步文本审核（带业务ID）
- `filterTextAsync(String text)` - 异步文本审核
- `filterTextAsync(String text, String businessId)` - 异步文本审核（带业务ID）

#### 图片审核

- `filterImage(String imageUrl)` - 通过URL审核图片
- `filterImage(String imageUrl, String businessId)` - 通过URL审核图片（带业务ID）
- `filterImageBase64(String imageData, String businessId)` - 通过Base64数据审核图片
- `filterImageFile(String imagePath, String businessId)` - 通过文件路径审核图片

#### 批量处理

- `filterTextsAsync(String[] texts)` - 批量文本审核
- `filterTextsAsync(String[] texts, String businessId)` - 批量文本审核（带业务ID）
- `filterImagesAsync(String[] imageUrls)` - 批量图片审核
- `filterImagesAsync(String[] imageUrls, String businessId)` - 批量图片审核（带业务ID）

## 使用示例

### 完整示例

```java
import com.netease.profanity.filter.ProfanityFilterConfig;
import com.netease.profanity.filter.ProfanityFilterService;
import com.netease.profanity.filter.model.FilterResponse;

public class Example {
    public static void main(String[] args) {
        // 1. 创建配置
        ProfanityFilterConfig config = new ProfanityFilterConfig(
            "your_access_key_id",
            "your_access_key_secret"
        );
        config.setDebug(true);
        
        // 2. 创建服务
        ProfanityFilterService service = new ProfanityFilterService(config);
        
        try {
            // 3. 文本审核
            FilterResponse textResponse = service.filterText("测试文本内容", "demo");
            System.out.println("文本审核结果：" + textResponse.isPass());
            
            // 4. 图片审核
            FilterResponse imageResponse = service.filterImage("https://example.com/test.jpg", "demo");
            System.out.println("图片审核结果：" + imageResponse.isPass());
            
            // 5. 异步处理
            service.filterTextAsync("异步文本", "async_demo")
                .thenAccept(result -> {
                    System.out.println("异步文本审核结果：" + result.isPass());
                });
                
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // 6. 关闭服务
            service.close();
        }
    }
}
```

### Spring Boot 集成

```java
@Configuration
public class ProfanityFilterConfig {
    
    @Value("${netease.profanity.access-key-id}")
    private String accessKeyId;
    
    @Value("${netease.profanity.access-key-secret}")
    private String accessKeySecret;
    
    @Bean
    public ProfanityFilterService profanityFilterService() {
        ProfanityFilterConfig config = new ProfanityFilterConfig(accessKeyId, accessKeySecret);
        return new ProfanityFilterService(config);
    }
}

@Service
public class ContentService {
    
    @Autowired
    private ProfanityFilterService profanityFilterService;
    
    public boolean checkText(String text) {
        try {
            FilterResponse response = profanityFilterService.filterText(text);
            return response.isPass();
        } catch (IOException e) {
            // 处理异常
            return false;
        }
    }
}
```

## 错误处理

SDK 会抛出以下异常：

- `IllegalArgumentException` - 参数无效
- `IOException` - 网络请求异常

建议在调用API时进行适当的异常处理：

```java
try {
    FilterResponse response = service.filterText(text);
    // 处理结果
} catch (IllegalArgumentException e) {
    // 参数错误
    logger.error("参数错误", e);
} catch (IOException e) {
    // 网络错误
    logger.error("网络请求失败", e);
}
```

## 性能优化

1. **连接池复用** - SDK内部使用OkHttp连接池，自动复用连接
2. **异步处理** - 对于高并发场景，建议使用异步API
3. **批量处理** - 对于大量内容，使用批量处理API提高效率
4. **合理设置超时** - 根据网络环境调整超时时间

## 注意事项

1. 请妥善保管您的API密钥，不要在代码中硬编码
2. 建议在生产环境中关闭调试模式
3. 图片文件大小建议不超过10MB
4. 支持的图片格式：JPG、PNG、GIF、BMP、WEBP
5. 文本长度建议不超过10000字符

## 版本历史

### 1.0.0
- 初始版本发布
- 支持文本和图片内容审核
- 提供同步和异步API
- 支持批量处理

## 许可证

本项目采用 Apache 2.0 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 技术支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue：[GitHub Issues](https://github.com/netease/netease-profanity-filter-java/issues)
- 邮箱：support@netease.com
- 文档：[官方文档](https://docs.netease.com/profanity-filter/java)

## 相关链接

- [网易云官网](https://www.163yun.com/)
- [API文档](https://docs.netease.com/censor)
- [Java SDK下载](https://mvnrepository.com/artifact/com.netease/netease-profanity-filter)