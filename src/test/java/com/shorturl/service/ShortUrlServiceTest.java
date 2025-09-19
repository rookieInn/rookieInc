package com.shorturl.service;

import com.shorturl.entity.ShortUrl;
import com.shorturl.repository.ShortUrlRepository;
import com.shorturl.repository.AccessLogRepository;
import com.shorturl.algorithm.ShortCodeGenerator;
import com.shorturl.cache.CacheManager;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * 短链接服务测试
 * 
 * @author ShortURL Team
 */
@SpringBootTest
class ShortUrlServiceTest {
    
    @Mock
    private ShortUrlRepository shortUrlRepository;
    
    @Mock
    private AccessLogRepository accessLogRepository;
    
    @Mock
    private ShortCodeGenerator shortCodeGenerator;
    
    @Mock
    private CacheManager cacheManager;
    
    @Mock
    private UrlValidationService urlValidationService;
    
    private ShortUrlService shortUrlService;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        shortUrlService = new ShortUrlService();
        // 使用反射设置私有字段（实际项目中应使用@InjectMocks）
    }
    
    @Test
    @DisplayName("测试创建短链接")
    void testCreateShortUrl() {
        // 准备测试数据
        String originalUrl = "https://www.example.com";
        String shortCode = "abc123";
        String ipAddress = "192.168.1.1";
        String userAgent = "Mozilla/5.0";
        
        ShortUrl expectedShortUrl = new ShortUrl(shortCode, originalUrl);
        expectedShortUrl.setId(1L);
        
        // 模拟依赖行为
        when(urlValidationService.isValidUrl(originalUrl)).thenReturn(true);
        when(shortUrlRepository.findByOriginalUrl(originalUrl)).thenReturn(Optional.empty());
        when(shortCodeGenerator.generateShortCode()).thenReturn(shortCode);
        when(shortUrlRepository.save(any(ShortUrl.class))).thenReturn(expectedShortUrl);
        
        // 执行测试
        ShortUrl result = shortUrlService.createShortUrl(
            originalUrl, null, null, null, null, ipAddress, userAgent
        );
        
        // 验证结果
        assertNotNull(result);
        assertEquals(shortCode, result.getShortCode());
        assertEquals(originalUrl, result.getOriginalUrl());
        assertEquals(ipAddress, result.getIpAddress());
        assertEquals(userAgent, result.getUserAgent());
        
        // 验证方法调用
        verify(urlValidationService).isValidUrl(originalUrl);
        verify(shortUrlRepository).findByOriginalUrl(originalUrl);
        verify(shortCodeGenerator).generateShortCode();
        verify(shortUrlRepository).save(any(ShortUrl.class));
    }
    
    @Test
    @DisplayName("测试获取原始URL")
    void testGetOriginalUrl() {
        // 准备测试数据
        String shortCode = "abc123";
        String originalUrl = "https://www.example.com";
        String ipAddress = "192.168.1.1";
        String userAgent = "Mozilla/5.0";
        
        ShortUrl shortUrl = new ShortUrl(shortCode, originalUrl);
        shortUrl.setId(1L);
        shortUrl.setIsActive(true);
        
        // 模拟依赖行为
        when(cacheManager.getShortUrl(shortCode)).thenReturn(Optional.of(shortUrl));
        
        // 执行测试
        Optional<String> result = shortUrlService.getOriginalUrl(
            shortCode, ipAddress, userAgent, null
        );
        
        // 验证结果
        assertTrue(result.isPresent());
        assertEquals(originalUrl, result.get());
        
        // 验证方法调用
        verify(cacheManager).getShortUrl(shortCode);
    }
    
    @Test
    @DisplayName("测试获取不存在的短链接")
    void testGetNonExistentShortUrl() {
        // 准备测试数据
        String shortCode = "nonexistent";
        String ipAddress = "192.168.1.1";
        String userAgent = "Mozilla/5.0";
        
        // 模拟依赖行为
        when(cacheManager.getShortUrl(shortCode)).thenReturn(Optional.empty());
        when(shortUrlRepository.findActiveByShortCode(eq(shortCode), any(LocalDateTime.class)))
            .thenReturn(Optional.empty());
        
        // 执行测试
        Optional<String> result = shortUrlService.getOriginalUrl(
            shortCode, ipAddress, userAgent, null
        );
        
        // 验证结果
        assertFalse(result.isPresent());
        
        // 验证方法调用
        verify(cacheManager).getShortUrl(shortCode);
        verify(shortUrlRepository).findActiveByShortCode(eq(shortCode), any(LocalDateTime.class));
    }
    
    @Test
    @DisplayName("测试密码验证")
    void testValidatePassword() {
        // 准备测试数据
        String shortCode = "abc123";
        String password = "password123";
        
        ShortUrl shortUrl = new ShortUrl(shortCode, "https://www.example.com");
        shortUrl.setPassword(password);
        
        // 模拟依赖行为
        when(cacheManager.getShortUrl(shortCode)).thenReturn(Optional.of(shortUrl));
        
        // 执行测试
        boolean result = shortUrlService.validatePassword(shortCode, password);
        
        // 验证结果
        assertTrue(result);
        
        // 验证错误密码
        boolean wrongResult = shortUrlService.validatePassword(shortCode, "wrongpassword");
        assertFalse(wrongResult);
    }
    
    @Test
    @DisplayName("测试删除短链接")
    void testDeleteShortUrl() {
        // 准备测试数据
        String shortCode = "abc123";
        ShortUrl shortUrl = new ShortUrl(shortCode, "https://www.example.com");
        shortUrl.setId(1L);
        
        // 模拟依赖行为
        when(shortUrlRepository.findByShortCode(shortCode)).thenReturn(Optional.of(shortUrl));
        when(shortUrlRepository.save(any(ShortUrl.class))).thenReturn(shortUrl);
        
        // 执行测试
        boolean result = shortUrlService.deleteShortUrl(shortCode);
        
        // 验证结果
        assertTrue(result);
        
        // 验证方法调用
        verify(shortUrlRepository).findByShortCode(shortCode);
        verify(shortUrlRepository).save(any(ShortUrl.class));
        verify(cacheManager).evictShortUrl(shortCode);
    }
    
    @Test
    @DisplayName("测试删除不存在的短链接")
    void testDeleteNonExistentShortUrl() {
        // 准备测试数据
        String shortCode = "nonexistent";
        
        // 模拟依赖行为
        when(shortUrlRepository.findByShortCode(shortCode)).thenReturn(Optional.empty());
        
        // 执行测试
        boolean result = shortUrlService.deleteShortUrl(shortCode);
        
        // 验证结果
        assertFalse(result);
        
        // 验证方法调用
        verify(shortUrlRepository).findByShortCode(shortCode);
        verify(cacheManager, never()).evictShortUrl(anyString());
    }
}