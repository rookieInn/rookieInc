package com.netease.profanity.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.netease.profanity.filter.model.FilterResponse;
import com.netease.profanity.filter.model.ImageFilterRequest;
import com.netease.profanity.filter.model.TextFilterRequest;
import okhttp3.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.concurrent.TimeUnit;

/**
 * 网易云脏字过滤客户端
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class ProfanityFilterClient {
    
    private static final Logger logger = LoggerFactory.getLogger(ProfanityFilterClient.class);
    
    private final ProfanityFilterConfig config;
    private final OkHttpClient httpClient;
    private final ObjectMapper objectMapper;
    
    /**
     * 构造函数
     * 
     * @param config 配置信息
     */
    public ProfanityFilterClient(ProfanityFilterConfig config) {
        if (config == null || !config.isValid()) {
            throw new IllegalArgumentException("Invalid configuration");
        }
        
        this.config = config;
        this.objectMapper = new ObjectMapper();
        
        // 创建HTTP客户端
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(config.getConnectTimeout(), TimeUnit.MILLISECONDS)
                .readTimeout(config.getTimeout(), TimeUnit.MILLISECONDS)
                .writeTimeout(config.getTimeout(), TimeUnit.MILLISECONDS)
                .build();
        
        if (config.isDebug()) {
            logger.info("ProfanityFilterClient initialized with config: {}", config);
        }
    }
    
    /**
     * 文本内容过滤
     * 
     * @param text 待检测的文本
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterText(String text) throws IOException {
        return filterText(text, null);
    }
    
    /**
     * 文本内容过滤
     * 
     * @param text 待检测的文本
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterText(String text, String businessId) throws IOException {
        if (text == null || text.trim().isEmpty()) {
            throw new IllegalArgumentException("Text cannot be null or empty");
        }
        
        TextFilterRequest request = new TextFilterRequest(text, businessId);
        return executeRequest("/api/v1/text/filter", request);
    }
    
    /**
     * 图片内容过滤（通过URL）
     * 
     * @param imageUrl 图片URL
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImage(String imageUrl) throws IOException {
        return filterImage(imageUrl, null);
    }
    
    /**
     * 图片内容过滤（通过URL）
     * 
     * @param imageUrl 图片URL
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImage(String imageUrl, String businessId) throws IOException {
        if (imageUrl == null || imageUrl.trim().isEmpty()) {
            throw new IllegalArgumentException("Image URL cannot be null or empty");
        }
        
        ImageFilterRequest request = new ImageFilterRequest(imageUrl);
        request.setBusinessId(businessId);
        return executeRequest("/api/v1/image/filter", request);
    }
    
    /**
     * 图片内容过滤（通过Base64数据）
     * 
     * @param imageData 图片Base64数据
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 网络异常
     */
    public FilterResponse filterImageBase64(String imageData, String businessId) throws IOException {
        if (imageData == null || imageData.trim().isEmpty()) {
            throw new IllegalArgumentException("Image data cannot be null or empty");
        }
        
        ImageFilterRequest request = new ImageFilterRequest(imageData, true);
        request.setBusinessId(businessId);
        return executeRequest("/api/v1/image/filter", request);
    }
    
    /**
     * 图片内容过滤（通过文件路径）
     * 
     * @param imagePath 图片文件路径
     * @param businessId 业务ID
     * @return 过滤结果
     * @throws IOException 文件读取或网络异常
     */
    public FilterResponse filterImageFile(String imagePath, String businessId) throws IOException {
        if (imagePath == null || imagePath.trim().isEmpty()) {
            throw new IllegalArgumentException("Image path cannot be null or empty");
        }
        
        // 读取文件并转换为Base64
        byte[] imageBytes = Files.readAllBytes(Paths.get(imagePath));
        String base64Data = Base64.getEncoder().encodeToString(imageBytes);
        
        return filterImageBase64(base64Data, businessId);
    }
    
    /**
     * 执行API请求
     * 
     * @param endpoint API端点
     * @param request 请求对象
     * @return 响应结果
     * @throws IOException 网络异常
     */
    private FilterResponse executeRequest(String endpoint, Object request) throws IOException {
        String url = config.getEndpoint() + endpoint;
        String jsonBody = objectMapper.writeValueAsString(request);
        
        if (config.isDebug()) {
            logger.debug("Sending request to: {}", url);
            logger.debug("Request body: {}", jsonBody);
        }
        
        RequestBody body = RequestBody.create(jsonBody, MediaType.get("application/json; charset=utf-8"));
        Request httpRequest = new Request.Builder()
                .url(url)
                .post(body)
                .addHeader("Content-Type", "application/json")
                .addHeader("Authorization", generateAuthHeader())
                .build();
        
        try (Response response = httpClient.newCall(httpRequest).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("HTTP request failed: " + response.code() + " " + response.message());
            }
            
            String responseBody = response.body().string();
            if (config.isDebug()) {
                logger.debug("Response body: {}", responseBody);
            }
            
            FilterResponse filterResponse = objectMapper.readValue(responseBody, FilterResponse.class);
            return filterResponse;
        }
    }
    
    /**
     * 生成认证头
     * 
     * @return 认证头字符串
     */
    private String generateAuthHeader() {
        // 这里应该实现网易云API的认证逻辑
        // 实际实现需要根据网易云API的认证方式进行调整
        return "Bearer " + config.getAccessKeyId() + ":" + config.getAccessKeySecret();
    }
    
    /**
     * 关闭客户端
     */
    public void close() {
        if (httpClient != null) {
            httpClient.dispatcher().executorService().shutdown();
            httpClient.connectionPool().evictAll();
        }
    }
}