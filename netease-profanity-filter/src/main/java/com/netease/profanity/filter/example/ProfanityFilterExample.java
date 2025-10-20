package com.netease.profanity.filter.example;

import com.netease.profanity.filter.ProfanityFilterClient;
import com.netease.profanity.filter.ProfanityFilterConfig;
import com.netease.profanity.filter.ProfanityFilterService;
import com.netease.profanity.filter.model.FilterResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;

/**
 * 网易云脏字过滤使用示例
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class ProfanityFilterExample {
    
    private static final Logger logger = LoggerFactory.getLogger(ProfanityFilterExample.class);
    
    public static void main(String[] args) {
        // 配置信息（请替换为实际的配置）
        ProfanityFilterConfig config = new ProfanityFilterConfig(
            "your_access_key_id",
            "your_access_key_secret",
            "https://censor.netease.im"
        );
        config.setDebug(true);
        
        // 创建服务实例
        ProfanityFilterService service = new ProfanityFilterService(config);
        
        try {
            // 示例1：同步文本过滤
            demonstrateTextFiltering(service);
            
            // 示例2：异步文本过滤
            demonstrateAsyncTextFiltering(service);
            
            // 示例3：图片过滤
            demonstrateImageFiltering(service);
            
            // 示例4：批量处理
            demonstrateBatchProcessing(service);
            
        } catch (Exception e) {
            logger.error("Example execution failed", e);
        } finally {
            // 关闭服务
            service.close();
        }
    }
    
    /**
     * 演示同步文本过滤
     */
    private static void demonstrateTextFiltering(ProfanityFilterService service) {
        System.out.println("\n=== 同步文本过滤示例 ===");
        
        String[] testTexts = {
            "这是一段正常的文本内容",
            "这里包含一些敏感词汇",
            "Hello World!",
            "测试文本，包含不当内容"
        };
        
        for (String text : testTexts) {
            try {
                FilterResponse response = service.filterText(text, "demo_business");
                printFilterResult("文本过滤", text, response);
            } catch (IOException e) {
                logger.error("文本过滤失败: " + text, e);
            }
        }
    }
    
    /**
     * 演示异步文本过滤
     */
    private static void demonstrateAsyncTextFiltering(ProfanityFilterService service) {
        System.out.println("\n=== 异步文本过滤示例 ===");
        
        String[] testTexts = {
            "异步处理文本1",
            "异步处理文本2",
            "异步处理文本3"
        };
        
        CompletableFuture<FilterResponse>[] futures = new CompletableFuture[testTexts.length];
        
        for (int i = 0; i < testTexts.length; i++) {
            final int index = i;
            futures[i] = service.filterTextAsync(testTexts[i], "async_demo_" + index);
        }
        
        // 等待所有异步任务完成
        CompletableFuture.allOf(futures).thenRun(() -> {
            for (int i = 0; i < futures.length; i++) {
                try {
                    FilterResponse response = futures[i].get();
                    printFilterResult("异步文本过滤", testTexts[i], response);
                } catch (Exception e) {
                    logger.error("异步文本过滤失败: " + testTexts[i], e);
                }
            }
        }).join();
    }
    
    /**
     * 演示图片过滤
     */
    private static void demonstrateImageFiltering(ProfanityFilterService service) {
        System.out.println("\n=== 图片过滤示例 ===");
        
        // 示例图片URL（请替换为实际的图片URL）
        String[] imageUrls = {
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
            "https://example.com/image3.gif"
        };
        
        for (String imageUrl : imageUrls) {
            try {
                FilterResponse response = service.filterImage(imageUrl, "image_demo");
                printFilterResult("图片过滤", imageUrl, response);
            } catch (IOException e) {
                logger.error("图片过滤失败: " + imageUrl, e);
            }
        }
        
        // 示例：通过文件路径过滤图片
        try {
            String imagePath = "/path/to/your/image.jpg";
            FilterResponse response = service.filterImageFile(imagePath, "file_demo");
            printFilterResult("文件图片过滤", imagePath, response);
        } catch (IOException e) {
            logger.error("文件图片过滤失败", e);
        }
    }
    
    /**
     * 演示批量处理
     */
    private static void demonstrateBatchProcessing(ProfanityFilterService service) {
        System.out.println("\n=== 批量处理示例 ===");
        
        String[] batchTexts = {
            "批量处理文本1",
            "批量处理文本2",
            "批量处理文本3",
            "批量处理文本4",
            "批量处理文本5"
        };
        
        try {
            CompletableFuture<FilterResponse[]> future = service.filterTextsAsync(batchTexts, "batch_demo");
            FilterResponse[] responses = future.get();
            
            for (int i = 0; i < responses.length; i++) {
                printFilterResult("批量文本过滤", batchTexts[i], responses[i]);
            }
        } catch (Exception e) {
            logger.error("批量处理失败", e);
        }
    }
    
    /**
     * 打印过滤结果
     */
    private static void printFilterResult(String type, String content, FilterResponse response) {
        System.out.println(String.format("\n%s结果:", type));
        System.out.println("  内容: " + content);
        System.out.println("  状态码: " + response.getCode());
        System.out.println("  消息: " + response.getMessage());
        System.out.println("  动作: " + response.getAction());
        System.out.println("  置信度: " + response.getConfidence());
        System.out.println("  是否通过: " + response.isPass());
        System.out.println("  是否拒绝: " + response.isReject());
        System.out.println("  是否疑似: " + response.isSuspect());
        
        if (response.getSensitiveWords() != null && !response.getSensitiveWords().isEmpty()) {
            System.out.println("  敏感词: " + response.getSensitiveWords());
        }
        
        if (response.getDetails() != null && !response.getDetails().isEmpty()) {
            System.out.println("  详细信息: " + response.getDetails());
        }
    }
}