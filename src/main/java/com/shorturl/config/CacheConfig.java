package com.shorturl.config;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

/**
 * 缓存配置类
 * 
 * @author ShortURL Team
 */
@Configuration
@EnableCaching
public class CacheConfig {
    
    /**
     * Caffeine缓存管理器
     * 
     * @return 缓存管理器
     */
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(caffeineConfig());
        return cacheManager;
    }
    
    /**
     * Caffeine缓存配置
     * 
     * @return Caffeine配置
     */
    @Bean
    public Caffeine<Object, Object> caffeineConfig() {
        return Caffeine.newBuilder()
                .maximumSize(10000)
                .expireAfterWrite(Duration.ofMinutes(10))
                .recordStats();
    }
    
    /**
     * 短链接缓存
     * 
     * @return 短链接缓存
     */
    @Bean("shortUrlCache")
    public Cache<String, Object> shortUrlCache() {
        return Caffeine.newBuilder()
                .maximumSize(50000)
                .expireAfterWrite(Duration.ofMinutes(5))
                .recordStats()
                .build();
    }
    
    /**
     * 访问统计缓存
     * 
     * @return 访问统计缓存
     */
    @Bean("accessStatsCache")
    public Cache<String, Object> accessStatsCache() {
        return Caffeine.newBuilder()
                .maximumSize(100000)
                .expireAfterWrite(Duration.ofMinutes(1))
                .recordStats()
                .build();
    }
}