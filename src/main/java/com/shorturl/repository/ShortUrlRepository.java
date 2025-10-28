package com.shorturl.repository;

import com.shorturl.entity.ShortUrl;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 短链接数据访问接口
 * 
 * @author ShortURL Team
 */
@Repository
public interface ShortUrlRepository extends JpaRepository<ShortUrl, Long> {
    
    /**
     * 根据短码查找短链接
     * 
     * @param shortCode 短码
     * @return 短链接实体
     */
    Optional<ShortUrl> findByShortCode(String shortCode);
    
    /**
     * 根据短码查找活跃的短链接
     * 
     * @param shortCode 短码
     * @return 短链接实体
     */
    @Query("SELECT s FROM ShortUrl s WHERE s.shortCode = :shortCode AND s.isActive = true " +
           "AND (s.expiresAt IS NULL OR s.expiresAt > :now)")
    Optional<ShortUrl> findActiveByShortCode(@Param("shortCode") String shortCode, 
                                           @Param("now") LocalDateTime now);
    
    /**
     * 根据原始URL查找短链接
     * 
     * @param originalUrl 原始URL
     * @return 短链接实体
     */
    Optional<ShortUrl> findByOriginalUrl(String originalUrl);
    
    /**
     * 检查短码是否存在
     * 
     * @param shortCode 短码
     * @return 是否存在
     */
    boolean existsByShortCode(String shortCode);
    
    /**
     * 增加访问次数
     * 
     * @param shortCode 短码
     * @return 更新行数
     */
    @Modifying
    @Query("UPDATE ShortUrl s SET s.accessCount = s.accessCount + 1 WHERE s.shortCode = :shortCode")
    int incrementAccessCount(@Param("shortCode") String shortCode);
    
    /**
     * 增加唯一访问次数
     * 
     * @param shortCode 短码
     * @return 更新行数
     */
    @Modifying
    @Query("UPDATE ShortUrl s SET s.uniqueAccessCount = s.uniqueAccessCount + 1 WHERE s.shortCode = :shortCode")
    int incrementUniqueAccessCount(@Param("shortCode") String shortCode);
    
    /**
     * 查找过期的短链接
     * 
     * @param now 当前时间
     * @return 过期短链接列表
     */
    @Query("SELECT s FROM ShortUrl s WHERE s.expiresAt IS NOT NULL AND s.expiresAt <= :now")
    List<ShortUrl> findExpiredUrls(@Param("now") LocalDateTime now);
    
    /**
     * 批量删除过期短链接
     * 
     * @param now 当前时间
     * @return 删除行数
     */
    @Modifying
    @Query("DELETE FROM ShortUrl s WHERE s.expiresAt IS NOT NULL AND s.expiresAt <= :now")
    int deleteExpiredUrls(@Param("now") LocalDateTime now);
    
    /**
     * 根据IP地址查找短链接
     * 
     * @param ipAddress IP地址
     * @param limit 限制数量
     * @return 短链接列表
     */
    @Query("SELECT s FROM ShortUrl s WHERE s.ipAddress = :ipAddress ORDER BY s.createdAt DESC")
    List<ShortUrl> findByIpAddress(@Param("ipAddress") String ipAddress, 
                                 org.springframework.data.domain.Pageable pageable);
    
    /**
     * 统计访问量排名
     * 
     * @param limit 限制数量
     * @return 访问量排名列表
     */
    @Query("SELECT s FROM ShortUrl s WHERE s.isActive = true ORDER BY s.accessCount DESC")
    List<ShortUrl> findTopByAccessCount(org.springframework.data.domain.Pageable pageable);
    
    /**
     * 统计总访问量
     * 
     * @return 总访问量
     */
    @Query("SELECT COALESCE(SUM(s.accessCount), 0) FROM ShortUrl s WHERE s.isActive = true")
    Long getTotalAccessCount();
    
    /**
     * 统计活跃短链接数量
     * 
     * @return 活跃短链接数量
     */
    @Query("SELECT COUNT(s) FROM ShortUrl s WHERE s.isActive = true " +
           "AND (s.expiresAt IS NULL OR s.expiresAt > :now)")
    Long countActiveUrls(@Param("now") LocalDateTime now);
}