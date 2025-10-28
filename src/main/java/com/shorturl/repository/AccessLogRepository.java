package com.shorturl.repository;

import com.shorturl.entity.AccessLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 访问记录数据访问接口
 * 
 * @author ShortURL Team
 */
@Repository
public interface AccessLogRepository extends JpaRepository<AccessLog, Long> {
    
    /**
     * 根据短链接ID查找访问记录
     * 
     * @param shortUrlId 短链接ID
     * @return 访问记录列表
     */
    List<AccessLog> findByShortUrlIdOrderByAccessedAtDesc(Long shortUrlId, 
                                                         org.springframework.data.domain.Pageable pageable);
    
    /**
     * 统计短链接的访问次数
     * 
     * @param shortUrlId 短链接ID
     * @return 访问次数
     */
    @Query("SELECT COUNT(a) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId")
    Long countByShortUrlId(@Param("shortUrlId") Long shortUrlId);
    
    /**
     * 统计短链接的唯一访问次数（按IP）
     * 
     * @param shortUrlId 短链接ID
     * @return 唯一访问次数
     */
    @Query("SELECT COUNT(DISTINCT a.ipAddress) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId")
    Long countUniqueByShortUrlId(@Param("shortUrlId") Long shortUrlId);
    
    /**
     * 统计指定时间范围内的访问次数
     * 
     * @param shortUrlId 短链接ID
     * @param startTime 开始时间
     * @param endTime 结束时间
     * @return 访问次数
     */
    @Query("SELECT COUNT(a) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId " +
           "AND a.accessedAt BETWEEN :startTime AND :endTime")
    Long countByShortUrlIdAndTimeRange(@Param("shortUrlId") Long shortUrlId,
                                     @Param("startTime") LocalDateTime startTime,
                                     @Param("endTime") LocalDateTime endTime);
    
    /**
     * 统计按国家分布的访问次数
     * 
     * @param shortUrlId 短链接ID
     * @return 国家访问统计
     */
    @Query("SELECT a.country, COUNT(a) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId " +
           "AND a.country IS NOT NULL GROUP BY a.country ORDER BY COUNT(a) DESC")
    List<Object[]> countByCountry(@Param("shortUrlId") Long shortUrlId);
    
    /**
     * 统计按设备类型分布的访问次数
     * 
     * @param shortUrlId 短链接ID
     * @return 设备类型访问统计
     */
    @Query("SELECT a.deviceType, COUNT(a) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId " +
           "AND a.deviceType IS NOT NULL GROUP BY a.deviceType ORDER BY COUNT(a) DESC")
    List<Object[]> countByDeviceType(@Param("shortUrlId") Long shortUrlId);
    
    /**
     * 统计按浏览器分布的访问次数
     * 
     * @param shortUrlId 短链接ID
     * @return 浏览器访问统计
     */
    @Query("SELECT a.browser, COUNT(a) FROM AccessLog a WHERE a.shortUrlId = :shortUrlId " +
           "AND a.browser IS NOT NULL GROUP BY a.browser ORDER BY COUNT(a) DESC")
    List<Object[]> countByBrowser(@Param("shortUrlId") Long shortUrlId);
    
    /**
     * 查找最近访问记录
     * 
     * @param shortUrlId 短链接ID
     * @param limit 限制数量
     * @return 最近访问记录
     */
    @Query("SELECT a FROM AccessLog a WHERE a.shortUrlId = :shortUrlId " +
           "ORDER BY a.accessedAt DESC")
    List<AccessLog> findRecentAccess(@Param("shortUrlId") Long shortUrlId,
                                   org.springframework.data.domain.Pageable pageable);
    
    /**
     * 统计每日访问量
     * 
     * @param shortUrlId 短链接ID
     * @param startDate 开始日期
     * @param endDate 结束日期
     * @return 每日访问统计
     */
    @Query("SELECT DATE(a.accessedAt) as date, COUNT(a) as count FROM AccessLog a " +
           "WHERE a.shortUrlId = :shortUrlId AND a.accessedAt BETWEEN :startDate AND :endDate " +
           "GROUP BY DATE(a.accessedAt) ORDER BY DATE(a.accessedAt)")
    List<Object[]> countDailyAccess(@Param("shortUrlId") Long shortUrlId,
                                  @Param("startDate") LocalDateTime startDate,
                                  @Param("endDate") LocalDateTime endDate);
    
    /**
     * 统计每小时访问量
     * 
     * @param shortUrlId 短链接ID
     * @param date 指定日期
     * @return 每小时访问统计
     */
    @Query("SELECT HOUR(a.accessedAt) as hour, COUNT(a) as count FROM AccessLog a " +
           "WHERE a.shortUrlId = :shortUrlId AND DATE(a.accessedAt) = DATE(:date) " +
           "GROUP BY HOUR(a.accessedAt) ORDER BY HOUR(a.accessedAt)")
    List<Object[]> countHourlyAccess(@Param("shortUrlId") Long shortUrlId,
                                   @Param("date") LocalDateTime date);
    
    /**
     * 删除过期访问记录
     * 
     * @param expireTime 过期时间
     * @return 删除记录数
     */
    @Query("DELETE FROM AccessLog a WHERE a.accessedAt < :expireTime")
    int deleteExpiredLogs(@Param("expireTime") LocalDateTime expireTime);
}