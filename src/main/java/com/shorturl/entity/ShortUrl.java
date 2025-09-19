package com.shorturl.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * 短链接实体
 * 
 * @author ShortURL Team
 */
@Entity
@Table(name = "short_urls", indexes = {
    @Index(name = "idx_short_code", columnList = "shortCode", unique = true),
    @Index(name = "idx_original_url", columnList = "originalUrl"),
    @Index(name = "idx_created_at", columnList = "createdAt"),
    @Index(name = "idx_expires_at", columnList = "expiresAt")
})
public class ShortUrl {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "short_code", nullable = false, unique = true, length = 8)
    private String shortCode;
    
    @Column(name = "original_url", nullable = false, length = 2048)
    private String originalUrl;
    
    @Column(name = "title", length = 255)
    private String title;
    
    @Column(name = "description", length = 500)
    private String description;
    
    @Column(name = "access_count", nullable = false)
    private Long accessCount = 0L;
    
    @Column(name = "unique_access_count", nullable = false)
    private Long uniqueAccessCount = 0L;
    
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;
    
    @Column(name = "expires_at")
    private LocalDateTime expiresAt;
    
    @Column(name = "password", length = 64)
    private String password;
    
    @Column(name = "ip_address", length = 45)
    private String ipAddress;
    
    @Column(name = "user_agent", length = 500)
    private String userAgent;
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
    
    // 构造函数
    public ShortUrl() {}
    
    public ShortUrl(String shortCode, String originalUrl) {
        this.shortCode = shortCode;
        this.originalUrl = originalUrl;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getShortCode() {
        return shortCode;
    }
    
    public void setShortCode(String shortCode) {
        this.shortCode = shortCode;
    }
    
    public String getOriginalUrl() {
        return originalUrl;
    }
    
    public void setOriginalUrl(String originalUrl) {
        this.originalUrl = originalUrl;
    }
    
    public String getTitle() {
        return title;
    }
    
    public void setTitle(String title) {
        this.title = title;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public Long getAccessCount() {
        return accessCount;
    }
    
    public void setAccessCount(Long accessCount) {
        this.accessCount = accessCount;
    }
    
    public Long getUniqueAccessCount() {
        return uniqueAccessCount;
    }
    
    public void setUniqueAccessCount(Long uniqueAccessCount) {
        this.uniqueAccessCount = uniqueAccessCount;
    }
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
    
    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }
    
    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public String getIpAddress() {
        return ipAddress;
    }
    
    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }
    
    public String getUserAgent() {
        return userAgent;
    }
    
    public void setUserAgent(String userAgent) {
        this.userAgent = userAgent;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    /**
     * 增加访问次数
     */
    public void incrementAccessCount() {
        this.accessCount++;
    }
    
    /**
     * 增加唯一访问次数
     */
    public void incrementUniqueAccessCount() {
        this.uniqueAccessCount++;
    }
    
    /**
     * 检查是否已过期
     */
    public boolean isExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }
    
    @Override
    public String toString() {
        return "ShortUrl{" +
                "id=" + id +
                ", shortCode='" + shortCode + '\'' +
                ", originalUrl='" + originalUrl + '\'' +
                ", accessCount=" + accessCount +
                ", isActive=" + isActive +
                ", createdAt=" + createdAt +
                '}';
    }
}