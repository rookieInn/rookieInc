package com.netease.profanity.filter;

import com.netease.profanity.filter.model.FilterResponse;
import com.netease.profanity.filter.model.ImageFilterRequest;
import com.netease.profanity.filter.model.TextFilterRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 网易云脏字过滤服务类
 * 提供高级功能和批量处理能力
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class ProfanityFilterService {
    
    private static final Logger logger = LoggerFactory.getLogger(ProfanityFilterService.class);
    
    private final ProfanityFilterClient client;
    private final ExecutorService executorService;
    
    /**
     * 构造函数
     * 
     * @param config 配置信息
     */
    public ProfanityFilterService(ProfanityFilterConfig config) {
        this.client = new ProfanityFilterClient(config);
        this.executorService = Executors.newFixedThreadPool(10);
    }
    
    /**
     * 构造函数
     * 
     * @param client 客户端实例
     */
    public ProfanityFilterService(ProfanityFilterClient client) {
        this.client = client;
        this.executorService = Executors.newFixedThreadPool(10);
    }
    
    /**
     * 异步文本过滤
     * 
     * @param text 待检测的文本
     * @return CompletableFuture包装的过滤结果
     */
    public CompletableFuture<FilterResponse> filterTextAsync(String text) {
        return filterTextAsync(text, null);
    }
    
    /**
     * 异步文本过滤
     * 
     * @param text 待检测的文本
     * @param businessId 业务ID
     * @return CompletableFuture包装的过滤结果
     */
    public CompletableFuture<FilterResponse> filterTextAsync(String text, String businessId) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return client.filterText(text, businessId);
            } catch (IOException e) {
                logger.error("Failed to filter text asynchronously", e);
                throw new RuntimeException("Text filtering failed", e);
            }
        }, executorService);
    }
    
    /**
     * 异步图片过滤
     * 
     * @param imageUrl 图片URL
     * @return CompletableFuture包装的过滤结果
     */
    public CompletableFuture<FilterResponse> filterImageAsync(String imageUrl) {
        return filterImageAsync(imageUrl, null);
    }
    
    /**
     * 异步图片过滤
     * 
     * @param imageUrl 图片URL
     * @param businessId 业务ID
     * @return CompletableFuture包装的过滤结果
     */
    public CompletableFuture<FilterResponse> filterImageAsync(String imageUrl, String businessId) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return client.filterImage(imageUrl, businessId);
            } catch (IOException e) {
                logger.error("Failed to filter image asynchronously", e);
                throw new RuntimeException("Image filtering failed", e);
            }
        }, executorService);
    }
    
    /**
     * 批量文本过滤
     * 
     * @param texts 文本列表
     * @return 过滤结果列表
     */
    public CompletableFuture<FilterResponse[]> filterTextsAsync(String[] texts) {
        return filterTextsAsync(texts, null);
    }
    
    /**
     * 批量文本过滤
     * 
     * @param texts 文本列表
     * @param businessId 业务ID
     * @return 过滤结果列表
     */
    public CompletableFuture<FilterResponse[]> filterTextsAsync(String[] texts, String businessId) {
        CompletableFuture<FilterResponse>[] futures = new CompletableFuture[texts.length];
        
        for (int i = 0; i < texts.length; i++) {
            final int index = i;
            futures[i] = filterTextAsync(texts[i], businessId + "_" + index);
        }
        
        return CompletableFuture.allOf(futures)
                .thenApply(v -> {
                    FilterResponse[] results = new FilterResponse[texts.length];
                    for (int i = 0; i < futures.length; i++) {
                        results[i] = futures[i].join();
                    }
                    return results;
                });
    }
    
    /**
     * 批量图片过滤
     * 
     * @param imageUrls 图片URL列表
     * @return 过滤结果列表
     */
    public CompletableFuture<FilterResponse[]> filterImagesAsync(String[] imageUrls) {
        return filterImagesAsync(imageUrls, null);
    }
    
    /**
     * 批量图片过滤
     * 
     * @param imageUrls 图片URL列表
     * @param businessId 业务ID
     * @return 过滤结果列表
     */
    public CompletableFuture<FilterResponse[]> filterImagesAsync(String[] imageUrls, String businessId) {
        CompletableFuture<FilterResponse>[] futures = new CompletableFuture[imageUrls.length];
        
        for (int i = 0; i < imageUrls.length; i++) {
            final int index = i;
            futures[i] = filterImageAsync(imageUrls[i], businessId + "_" + index);
        }
        
        return CompletableFuture.allOf(futures)
                .thenApply(v -> {
                    FilterResponse[] results = new FilterResponse[imageUrls.length];
                    for (int i = 0; i < futures.length; i++) {
                        results[i] = futures[i].join();
                    }
                    return results;
                });
    }
    
    /**
     * 同步文本过滤（委托给客户端）
     * 
     * @param text 待检测的文本
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterText(String text) throws IOException {
        return client.filterText(text);
    }
    
    /**
     * 同步文本过滤（委托给客户端）
     * 
     * @param text 待检测的文本
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterText(String text, String businessId) throws IOException {
        return client.filterText(text, businessId);
    }
    
    /**
     * 同步图片过滤（委托给客户端）
     * 
     * @param imageUrl 图片URL
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImage(String imageUrl) throws IOException {
        return client.filterImage(imageUrl);
    }
    
    /**
     * 同步图片过滤（委托给客户端）
     * 
     * @param imageUrl 图片URL
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImage(String imageUrl, String businessId) throws IOException {
        return client.filterImage(imageUrl, businessId);
    }
    
    /**
     * 同步图片过滤（通过Base64数据）
     * 
     * @param imageData 图片Base64数据
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImageBase64(String imageData, String businessId) throws IOException {
        return client.filterImageBase64(imageData, businessId);
    }
    
    /**
     * 同步图片过滤（通过文件路径）
     * 
     * @param imagePath 图片文件路径
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 文件读取或网络异常
     */
    public FilterResponse filterImageFile(String imagePath, String businessId) throws IOException {
        return client.filterImageFile(imagePath, businessId);
    }
    
    /**
     * 关闭服务
     */
    public void close() {
        if (executorService != null) {
            executorService.shutdown();
        }
        if (client != null) {
            client.close();
        }
    }
}