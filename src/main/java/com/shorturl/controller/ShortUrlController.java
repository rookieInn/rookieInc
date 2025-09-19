package com.shorturl.controller;

import com.shorturl.entity.ShortUrl;
import com.shorturl.service.ShortUrlService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * 短链接REST API控制器
 * 
 * @author ShortURL Team
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class ShortUrlController {
    
    private static final Logger logger = LoggerFactory.getLogger(ShortUrlController.class);
    
    @Autowired
    private ShortUrlService shortUrlService;
    
    /**
     * 生成短链接
     * 
     * @param request 请求体
     * @param httpRequest HTTP请求
     * @return 短链接信息
     */
    @PostMapping("/shorten")
    public ResponseEntity<Map<String, Object>> createShortUrl(@RequestBody CreateShortUrlRequest request,
                                                            HttpServletRequest httpRequest) {
        try {
            // 获取客户端信息
            String ipAddress = getClientIpAddress(httpRequest);
            String userAgent = httpRequest.getHeader("User-Agent");
            
            // 创建短链接
            ShortUrl shortUrl = shortUrlService.createShortUrl(
                request.getUrl(),
                request.getTitle(),
                request.getDescription(),
                request.getExpiresAt(),
                request.getPassword(),
                ipAddress,
                userAgent
            );
            
            // 构建响应
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("shortCode", shortUrl.getShortCode());
            response.put("shortUrl", buildShortUrl(httpRequest, shortUrl.getShortCode()));
            response.put("originalUrl", shortUrl.getOriginalUrl());
            response.put("title", shortUrl.getTitle());
            response.put("description", shortUrl.getDescription());
            response.put("expiresAt", shortUrl.getExpiresAt());
            response.put("hasPassword", shortUrl.getPassword() != null);
            response.put("createdAt", shortUrl.getCreatedAt());
            
            logger.info("Created short URL: {} -> {}", shortUrl.getShortCode(), shortUrl.getOriginalUrl());
            return ResponseEntity.ok(response);
            
        } catch (IllegalArgumentException e) {
            logger.warn("Invalid request: {}", e.getMessage());
            return ResponseEntity.badRequest().body(createErrorResponse("INVALID_URL", e.getMessage()));
        } catch (Exception e) {
            logger.error("Failed to create short URL", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("INTERNAL_ERROR", "Failed to create short URL"));
        }
    }
    
    /**
     * 获取短链接详情
     * 
     * @param shortCode 短码
     * @return 短链接详情
     */
    @GetMapping("/info/{shortCode}")
    public ResponseEntity<Map<String, Object>> getShortUrlInfo(@PathVariable String shortCode) {
        try {
            Optional<ShortUrl> shortUrlOpt = shortUrlService.getShortUrlDetails(shortCode);
            
            if (shortUrlOpt.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            
            ShortUrl shortUrl = shortUrlOpt.get();
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("shortCode", shortUrl.getShortCode());
            response.put("originalUrl", shortUrl.getOriginalUrl());
            response.put("title", shortUrl.getTitle());
            response.put("description", shortUrl.getDescription());
            response.put("accessCount", shortUrl.getAccessCount());
            response.put("uniqueAccessCount", shortUrl.getUniqueAccessCount());
            response.put("isActive", shortUrl.getIsActive());
            response.put("expiresAt", shortUrl.getExpiresAt());
            response.put("hasPassword", shortUrl.getPassword() != null);
            response.put("createdAt", shortUrl.getCreatedAt());
            response.put("updatedAt", shortUrl.getUpdatedAt());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Failed to get short URL info", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("INTERNAL_ERROR", "Failed to get short URL info"));
        }
    }
    
    /**
     * 验证短码密码
     * 
     * @param shortCode 短码
     * @param request 密码验证请求
     * @return 验证结果
     */
    @PostMapping("/validate/{shortCode}")
    public ResponseEntity<Map<String, Object>> validatePassword(@PathVariable String shortCode,
                                                              @RequestBody PasswordValidationRequest request) {
        try {
            boolean isValid = shortUrlService.validatePassword(shortCode, request.getPassword());
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("valid", isValid);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Failed to validate password", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("INTERNAL_ERROR", "Failed to validate password"));
        }
    }
    
    /**
     * 删除短链接
     * 
     * @param shortCode 短码
     * @return 删除结果
     */
    @DeleteMapping("/{shortCode}")
    public ResponseEntity<Map<String, Object>> deleteShortUrl(@PathVariable String shortCode) {
        try {
            boolean deleted = shortUrlService.deleteShortUrl(shortCode);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("deleted", deleted);
            
            if (deleted) {
                logger.info("Deleted short URL: {}", shortCode);
            }
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Failed to delete short URL", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(createErrorResponse("INTERNAL_ERROR", "Failed to delete short URL"));
        }
    }
    
    /**
     * 短链接重定向
     * 
     * @param shortCode 短码
     * @param request HTTP请求
     * @param response HTTP响应
     */
    @GetMapping("/s/{shortCode}")
    public void redirect(@PathVariable String shortCode,
                        HttpServletRequest request,
                        HttpServletResponse response) throws IOException {
        try {
            // 获取客户端信息
            String ipAddress = getClientIpAddress(request);
            String userAgent = request.getHeader("User-Agent");
            String referer = request.getHeader("Referer");
            
            // 获取原始URL
            Optional<String> originalUrlOpt = shortUrlService.getOriginalUrl(shortCode, ipAddress, userAgent, referer);
            
            if (originalUrlOpt.isEmpty()) {
                response.sendError(HttpStatus.NOT_FOUND.value(), "Short URL not found or expired");
                return;
            }
            
            String originalUrl = originalUrlOpt.get();
            
            // 重定向到原始URL
            response.sendRedirect(originalUrl);
            logger.info("Redirected {} -> {}", shortCode, originalUrl);
            
        } catch (Exception e) {
            logger.error("Failed to redirect short URL: {}", shortCode, e);
            response.sendError(HttpStatus.INTERNAL_SERVER_ERROR.value(), "Internal server error");
        }
    }
    
    /**
     * 健康检查
     * 
     * @return 健康状态
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", LocalDateTime.now());
        response.put("service", "short-url-service");
        response.put("version", "1.0.0");
        
        return ResponseEntity.ok(response);
    }
    
    /**
     * 获取客户端IP地址
     * 
     * @param request HTTP请求
     * @return IP地址
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        String xRealIp = request.getHeader("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty()) {
            return xRealIp;
        }
        
        return request.getRemoteAddr();
    }
    
    /**
     * 构建短链接URL
     * 
     * @param request HTTP请求
     * @param shortCode 短码
     * @return 短链接URL
     */
    private String buildShortUrl(HttpServletRequest request, String shortCode) {
        String scheme = request.getScheme();
        String host = request.getServerName();
        int port = request.getServerPort();
        
        StringBuilder url = new StringBuilder();
        url.append(scheme).append("://").append(host);
        
        if ((scheme.equals("http") && port != 80) || (scheme.equals("https") && port != 443)) {
            url.append(":").append(port);
        }
        
        url.append("/api/s/").append(shortCode);
        
        return url.toString();
    }
    
    /**
     * 创建错误响应
     * 
     * @param code 错误代码
     * @param message 错误消息
     * @return 错误响应
     */
    private Map<String, Object> createErrorResponse(String code, String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("error", code);
        response.put("message", message);
        return response;
    }
    
    /**
     * 创建短链接请求
     */
    public static class CreateShortUrlRequest {
        private String url;
        private String title;
        private String description;
        private LocalDateTime expiresAt;
        private String password;
        
        // Getters and Setters
        public String getUrl() { return url; }
        public void setUrl(String url) { this.url = url; }
        
        public String getTitle() { return title; }
        public void setTitle(String title) { this.title = title; }
        
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
        
        public LocalDateTime getExpiresAt() { return expiresAt; }
        public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }
        
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
    }
    
    /**
     * 密码验证请求
     */
    public static class PasswordValidationRequest {
        private String password;
        
        // Getters and Setters
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
    }
}