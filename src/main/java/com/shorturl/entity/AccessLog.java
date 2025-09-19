package com.shorturl.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 访问记录实体
 * 
 * @author ShortURL Team
 */
@Entity
@Table(name = "access_logs", indexes = {
    @Index(name = "idx_short_url_id", columnList = "shortUrlId"),
    @Index(name = "idx_accessed_at", columnList = "accessedAt"),
    @Index(name = "idx_ip_address", columnList = "ipAddress"),
    @Index(name = "idx_user_agent", columnList = "userAgent")
})
public class AccessLog {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "short_url_id", nullable = false)
    private Long shortUrlId;
    
    @Column(name = "ip_address", length = 45)
    private String ipAddress;
    
    @Column(name = "user_agent", length = 500)
    private String userAgent;
    
    @Column(name = "referer", length = 2048)
    private String referer;
    
    @Column(name = "country", length = 2)
    private String country;
    
    @Column(name = "city", length = 100)
    private String city;
    
    @Column(name = "device_type", length = 20)
    private String deviceType;
    
    @Column(name = "browser", length = 50)
    private String browser;
    
    @Column(name = "os", length = 50)
    private String os;
    
    @CreationTimestamp
    @Column(name = "accessed_at", nullable = false, updatable = false)
    private LocalDateTime accessedAt;
    
    // 构造函数
    public AccessLog() {}
    
    public AccessLog(Long shortUrlId, String ipAddress, String userAgent) {
        this.shortUrlId = shortUrlId;
        this.ipAddress = ipAddress;
        this.userAgent = userAgent;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public Long getShortUrlId() {
        return shortUrlId;
    }
    
    public void setShortUrlId(Long shortUrlId) {
        this.shortUrlId = shortUrlId;
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
    
    public String getReferer() {
        return referer;
    }
    
    public void setReferer(String referer) {
        this.referer = referer;
    }
    
    public String getCountry() {
        return country;
    }
    
    public void setCountry(String country) {
        this.country = country;
    }
    
    public String getCity() {
        return city;
    }
    
    public void setCity(String city) {
        this.city = city;
    }
    
    public String getDeviceType() {
        return deviceType;
    }
    
    public void setDeviceType(String deviceType) {
        this.deviceType = deviceType;
    }
    
    public String getBrowser() {
        return browser;
    }
    
    public void setBrowser(String browser) {
        this.browser = browser;
    }
    
    public String getOs() {
        return os;
    }
    
    public void setOs(String os) {
        this.os = os;
    }
    
    public LocalDateTime getAccessedAt() {
        return accessedAt;
    }
    
    public void setAccessedAt(LocalDateTime accessedAt) {
        this.accessedAt = accessedAt;
    }
    
    @Override
    public String toString() {
        return "AccessLog{" +
                "id=" + id +
                ", shortUrlId=" + shortUrlId +
                ", ipAddress='" + ipAddress + '\'' +
                ", userAgent='" + userAgent + '\'' +
                ", accessedAt=" + accessedAt +
                '}';
    }
}