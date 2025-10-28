package com.shorturl.cache;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.shorturl.entity.ShortUrl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

/**
 * 多级缓存管理器
 * 
 * 缓存策略：
 * L1: 本地缓存 (Caffeine) - 1分钟TTL，最大10000条
 * L2: Redis缓存 - 1小时TTL
 * L3: 数据库 - 持久化存储
 * 
 * @author ShortURL Team
 */
@Component
public class CacheManager {
    
    private static final Logger logger = LoggerFactory.getLogger(CacheManager.class);
    
    // 缓存键前缀
    private static final String SHORT_URL_PREFIX = "short_url:";
    private static final String ACCESS_COUNT_PREFIX = "access_count:";
    private static final String UNIQUE_ACCESS_PREFIX = "unique_access:";
    
    // 缓存TTL配置
    private static final Duration LOCAL_CACHE_TTL = Duration.ofMinutes(1);
    private static final Duration REDIS_CACHE_TTL = Duration.ofHours(1);
    private static final Duration ACCESS_COUNT_TTL = Duration.ofMinutes(5);
    
    // 本地缓存配置
    private final Cache<String, ShortUrl> localCache = Caffeine.newBuilder()
            .maximumSize(10000)
            .expireAfterWrite(LOCAL_CACHE_TTL)
            .recordStats()
            .build();
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    /**
     * 获取短链接（多级缓存）
     * 
     * @param shortCode 短码
     * @return 短链接实体
     */
    public Optional<ShortUrl> getShortUrl(String shortCode) {
        String cacheKey = SHORT_URL_PREFIX + shortCode;
        
        // L1: 本地缓存
        ShortUrl shortUrl = localCache.getIfPresent(cacheKey);
        if (shortUrl != null) {
            logger.debug("L1 cache hit for shortCode: {}", shortCode);
            return Optional.of(shortUrl);
        }
        
        // L2: Redis缓存
        try {
            shortUrl = (ShortUrl) redisTemplate.opsForValue().get(cacheKey);
            if (shortUrl != null) {
                logger.debug("L2 cache hit for shortCode: {}", shortCode);
                // 回填本地缓存
                localCache.put(cacheKey, shortUrl);
                return Optional.of(shortUrl);
            }
        } catch (Exception e) {
            logger.warn("Redis cache error for shortCode: {}, error: {}", shortCode, e.getMessage());
        }
        
        logger.debug("Cache miss for shortCode: {}", shortCode);
        return Optional.empty();
    }
    
    /**
     * 设置短链接缓存
     * 
     * @param shortCode 短码
     * @param shortUrl 短链接实体
     */
    public void setShortUrl(String shortCode, ShortUrl shortUrl) {
        String cacheKey = SHORT_URL_PREFIX + shortCode;
        
        // L1: 本地缓存
        localCache.put(cacheKey, shortUrl);
        
        // L2: Redis缓存
        try {
            redisTemplate.opsForValue().set(cacheKey, shortUrl, REDIS_CACHE_TTL);
            logger.debug("Set cache for shortCode: {}", shortCode);
        } catch (Exception e) {
            logger.warn("Failed to set Redis cache for shortCode: {}, error: {}", shortCode, e.getMessage());
        }
    }
    
    /**
     * 删除短链接缓存
     * 
     * @param shortCode 短码
     */
    public void evictShortUrl(String shortCode) {
        String cacheKey = SHORT_URL_PREFIX + shortCode;
        
        // L1: 本地缓存
        localCache.invalidate(cacheKey);
        
        // L2: Redis缓存
        try {
            redisTemplate.delete(cacheKey);
            logger.debug("Evicted cache for shortCode: {}", shortCode);
        } catch (Exception e) {
            logger.warn("Failed to evict Redis cache for shortCode: {}, error: {}", shortCode, e.getMessage());
        }
    }
    
    /**
     * 增加访问次数（Redis原子操作）
     * 
     * @param shortCode 短码
     * @return 当前访问次数
     */
    public Long incrementAccessCount(String shortCode) {
        String cacheKey = ACCESS_COUNT_PREFIX + shortCode;
        
        try {
            Long count = redisTemplate.opsForValue().increment(cacheKey);
            redisTemplate.expire(cacheKey, ACCESS_COUNT_TTL);
            logger.debug("Incremented access count for shortCode: {}, count: {}", shortCode, count);
            return count;
        } catch (Exception e) {
            logger.warn("Failed to increment access count for shortCode: {}, error: {}", shortCode, e.getMessage());
            return 0L;
        }
    }
    
    /**
     * 增加唯一访问次数（Redis Set）
     * 
     * @param shortCode 短码
     * @param ipAddress IP地址
     * @return 是否为新访问者
     */
    public boolean incrementUniqueAccessCount(String shortCode, String ipAddress) {
        String cacheKey = UNIQUE_ACCESS_PREFIX + shortCode;
        
        try {
            Boolean isNew = redisTemplate.opsForSet().add(cacheKey, ipAddress);
            redisTemplate.expire(cacheKey, ACCESS_COUNT_TTL);
            logger.debug("Incremented unique access count for shortCode: {}, ip: {}, isNew: {}", 
                        shortCode, ipAddress, isNew);
            return Boolean.TRUE.equals(isNew);
        } catch (Exception e) {
            logger.warn("Failed to increment unique access count for shortCode: {}, error: {}", 
                       shortCode, e.getMessage());
            return false;
        }
    }
    
    /**
     * 获取访问次数
     * 
     * @param shortCode 短码
     * @return 访问次数
     */
    public Long getAccessCount(String shortCode) {
        String cacheKey = ACCESS_COUNT_PREFIX + shortCode;
        
        try {
            Object count = redisTemplate.opsForValue().get(cacheKey);
            return count != null ? Long.valueOf(count.toString()) : 0L;
        } catch (Exception e) {
            logger.warn("Failed to get access count for shortCode: {}, error: {}", shortCode, e.getMessage());
            return 0L;
        }
    }
    
    /**
     * 获取唯一访问次数
     * 
     * @param shortCode 短码
     * @return 唯一访问次数
     */
    public Long getUniqueAccessCount(String shortCode) {
        String cacheKey = UNIQUE_ACCESS_PREFIX + shortCode;
        
        try {
            return redisTemplate.opsForSet().size(cacheKey);
        } catch (Exception e) {
            logger.warn("Failed to get unique access count for shortCode: {}, error: {}", shortCode, e.getMessage());
            return 0L;
        }
    }
    
    /**
     * 清空所有缓存
     */
    public void clearAllCache() {
        // 清空本地缓存
        localCache.invalidateAll();
        
        // 清空Redis缓存
        try {
            redisTemplate.getConnectionFactory().getConnection().flushAll();
            logger.info("Cleared all cache");
        } catch (Exception e) {
            logger.warn("Failed to clear Redis cache, error: {}", e.getMessage());
        }
    }
    
    /**
     * 获取缓存统计信息
     * 
     * @return 缓存统计
     */
    public String getCacheStats() {
        var stats = localCache.stats();
        return String.format("Local Cache Stats - Hit Rate: %.2f%%, Miss Rate: %.2f%%, " +
                           "Hit Count: %d, Miss Count: %d, Eviction Count: %d",
                           stats.hitRate() * 100, stats.missRate() * 100,
                           stats.hitCount(), stats.missCount(), stats.evictionCount());
    }
}