package com.shorturl.service;

import com.shorturl.algorithm.ShortCodeGenerator;
import com.shorturl.cache.CacheManager;
import com.shorturl.entity.AccessLog;
import com.shorturl.entity.ShortUrl;
import com.shorturl.repository.AccessLogRepository;
import com.shorturl.repository.ShortUrlRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.net.MalformedURLException;
import java.net.URL;
import java.time.LocalDateTime;
import java.util.Optional;

/**
 * 短链接业务服务
 * 
 * @author ShortURL Team
 */
@Service
@Transactional
public class ShortUrlService {
    
    private static final Logger logger = LoggerFactory.getLogger(ShortUrlService.class);
    
    @Autowired
    private ShortUrlRepository shortUrlRepository;
    
    @Autowired
    private AccessLogRepository accessLogRepository;
    
    @Autowired
    private ShortCodeGenerator shortCodeGenerator;
    
    @Autowired
    private CacheManager cacheManager;
    
    @Autowired
    private UrlValidationService urlValidationService;
    
    /**
     * 创建短链接
     * 
     * @param originalUrl 原始URL
     * @param title 标题
     * @param description 描述
     * @param expiresAt 过期时间
     * @param password 密码
     * @param ipAddress IP地址
     * @param userAgent 用户代理
     * @return 短链接实体
     */
    public ShortUrl createShortUrl(String originalUrl, String title, String description,
                                 LocalDateTime expiresAt, String password, String ipAddress, String userAgent) {
        
        // 验证URL格式
        if (!urlValidationService.isValidUrl(originalUrl)) {
            throw new IllegalArgumentException("Invalid URL format: " + originalUrl);
        }
        
        // 检查URL是否已存在
        Optional<ShortUrl> existingUrl = shortUrlRepository.findByOriginalUrl(originalUrl);
        if (existingUrl.isPresent() && existingUrl.get().getIsActive()) {
            logger.info("URL already exists: {}", originalUrl);
            return existingUrl.get();
        }
        
        // 生成短码
        String shortCode = generateUniqueShortCode();
        
        // 创建短链接实体
        ShortUrl shortUrl = new ShortUrl(shortCode, originalUrl);
        shortUrl.setTitle(title);
        shortUrl.setDescription(description);
        shortUrl.setExpiresAt(expiresAt);
        shortUrl.setPassword(password);
        shortUrl.setIpAddress(ipAddress);
        shortUrl.setUserAgent(userAgent);
        
        // 保存到数据库
        shortUrl = shortUrlRepository.save(shortUrl);
        
        // 设置缓存
        cacheManager.setShortUrl(shortCode, shortUrl);
        
        logger.info("Created short URL: {} -> {}", shortCode, originalUrl);
        return shortUrl;
    }
    
    /**
     * 根据短码获取原始URL
     * 
     * @param shortCode 短码
     * @param ipAddress IP地址
     * @param userAgent 用户代理
     * @param referer 来源页面
     * @return 原始URL
     */
    @Transactional(readOnly = true)
    public Optional<String> getOriginalUrl(String shortCode, String ipAddress, String userAgent, String referer) {
        // 从缓存获取
        Optional<ShortUrl> shortUrlOpt = cacheManager.getShortUrl(shortCode);
        
        if (shortUrlOpt.isEmpty()) {
            // 从数据库获取
            shortUrlOpt = shortUrlRepository.findActiveByShortCode(shortCode, LocalDateTime.now());
            if (shortUrlOpt.isPresent()) {
                // 回填缓存
                cacheManager.setShortUrl(shortCode, shortUrlOpt.get());
            }
        }
        
        if (shortUrlOpt.isEmpty()) {
            logger.warn("Short URL not found: {}", shortCode);
            return Optional.empty();
        }
        
        ShortUrl shortUrl = shortUrlOpt.get();
        
        // 检查是否过期
        if (shortUrl.isExpired()) {
            logger.warn("Short URL expired: {}", shortCode);
            return Optional.empty();
        }
        
        // 记录访问日志
        recordAccess(shortUrl, ipAddress, userAgent, referer);
        
        // 更新访问统计
        updateAccessStats(shortCode, ipAddress);
        
        return Optional.of(shortUrl.getOriginalUrl());
    }
    
    /**
     * 根据短码获取短链接详情
     * 
     * @param shortCode 短码
     * @return 短链接实体
     */
    @Transactional(readOnly = true)
    public Optional<ShortUrl> getShortUrlDetails(String shortCode) {
        // 从缓存获取
        Optional<ShortUrl> shortUrlOpt = cacheManager.getShortUrl(shortCode);
        
        if (shortUrlOpt.isEmpty()) {
            // 从数据库获取
            shortUrlOpt = shortUrlRepository.findByShortCode(shortCode);
            if (shortUrlOpt.isPresent()) {
                // 回填缓存
                cacheManager.setShortUrl(shortCode, shortUrlOpt.get());
            }
        }
        
        return shortUrlOpt;
    }
    
    /**
     * 验证短码密码
     * 
     * @param shortCode 短码
     * @param password 密码
     * @return 是否验证通过
     */
    @Transactional(readOnly = true)
    public boolean validatePassword(String shortCode, String password) {
        Optional<ShortUrl> shortUrlOpt = getShortUrlDetails(shortCode);
        if (shortUrlOpt.isEmpty()) {
            return false;
        }
        
        ShortUrl shortUrl = shortUrlOpt.get();
        if (shortUrl.getPassword() == null) {
            return true; // 无密码保护
        }
        
        return shortUrl.getPassword().equals(password);
    }
    
    /**
     * 删除短链接
     * 
     * @param shortCode 短码
     * @return 是否删除成功
     */
    public boolean deleteShortUrl(String shortCode) {
        Optional<ShortUrl> shortUrlOpt = shortUrlRepository.findByShortCode(shortCode);
        if (shortUrlOpt.isEmpty()) {
            return false;
        }
        
        ShortUrl shortUrl = shortUrlOpt.get();
        shortUrl.setIsActive(false);
        shortUrlRepository.save(shortUrl);
        
        // 清除缓存
        cacheManager.evictShortUrl(shortCode);
        
        logger.info("Deleted short URL: {}", shortCode);
        return true;
    }
    
    /**
     * 生成唯一的短码
     * 
     * @return 短码
     */
    private String generateUniqueShortCode() {
        int maxRetries = 10;
        int retryCount = 0;
        
        while (retryCount < maxRetries) {
            String shortCode = shortCodeGenerator.generateShortCode();
            
            if (!shortUrlRepository.existsByShortCode(shortCode)) {
                return shortCode;
            }
            
            retryCount++;
            logger.warn("Short code collision detected, retrying... (attempt {})", retryCount);
        }
        
        throw new RuntimeException("Failed to generate unique short code after " + maxRetries + " attempts");
    }
    
    /**
     * 记录访问日志
     * 
     * @param shortUrl 短链接实体
     * @param ipAddress IP地址
     * @param userAgent 用户代理
     * @param referer 来源页面
     */
    private void recordAccess(ShortUrl shortUrl, String ipAddress, String userAgent, String referer) {
        try {
            AccessLog accessLog = new AccessLog(shortUrl.getId(), ipAddress, userAgent);
            accessLog.setReferer(referer);
            
            // 解析用户代理信息
            parseUserAgent(accessLog, userAgent);
            
            // 异步保存访问日志
            accessLogRepository.save(accessLog);
            
            logger.debug("Recorded access log for shortCode: {}", shortUrl.getShortCode());
        } catch (Exception e) {
            logger.warn("Failed to record access log: {}", e.getMessage());
        }
    }
    
    /**
     * 更新访问统计
     * 
     * @param shortCode 短码
     * @param ipAddress IP地址
     */
    private void updateAccessStats(String shortCode, String ipAddress) {
        try {
            // 更新访问次数
            cacheManager.incrementAccessCount(shortCode);
            
            // 更新唯一访问次数
            boolean isNewVisitor = cacheManager.incrementUniqueAccessCount(shortCode, ipAddress);
            
            // 定期同步到数据库
            if (isNewVisitor) {
                shortUrlRepository.incrementUniqueAccessCount(shortCode);
            }
            
            // 每100次访问同步一次到数据库
            Long accessCount = cacheManager.getAccessCount(shortCode);
            if (accessCount % 100 == 0) {
                shortUrlRepository.incrementAccessCount(shortCode);
            }
            
        } catch (Exception e) {
            logger.warn("Failed to update access stats: {}", e.getMessage());
        }
    }
    
    /**
     * 解析用户代理信息
     * 
     * @param accessLog 访问日志
     * @param userAgent 用户代理字符串
     */
    private void parseUserAgent(AccessLog accessLog, String userAgent) {
        if (!StringUtils.hasText(userAgent)) {
            return;
        }
        
        try {
            // 简单的用户代理解析（实际项目中应使用专门的库如User-Agent-Utils）
            String ua = userAgent.toLowerCase();
            
            // 设备类型检测
            if (ua.contains("mobile") || ua.contains("android") || ua.contains("iphone")) {
                accessLog.setDeviceType("mobile");
            } else if (ua.contains("tablet") || ua.contains("ipad")) {
                accessLog.setDeviceType("tablet");
            } else {
                accessLog.setDeviceType("desktop");
            }
            
            // 浏览器检测
            if (ua.contains("chrome")) {
                accessLog.setBrowser("Chrome");
            } else if (ua.contains("firefox")) {
                accessLog.setBrowser("Firefox");
            } else if (ua.contains("safari")) {
                accessLog.setBrowser("Safari");
            } else if (ua.contains("edge")) {
                accessLog.setBrowser("Edge");
            }
            
            // 操作系统检测
            if (ua.contains("windows")) {
                accessLog.setOs("Windows");
            } else if (ua.contains("mac")) {
                accessLog.setOs("macOS");
            } else if (ua.contains("linux")) {
                accessLog.setOs("Linux");
            } else if (ua.contains("android")) {
                accessLog.setOs("Android");
            } else if (ua.contains("ios")) {
                accessLog.setOs("iOS");
            }
            
        } catch (Exception e) {
            logger.warn("Failed to parse user agent: {}", e.getMessage());
        }
    }
}