package com.netease.profanity.filter;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 网易云脏字过滤配置类
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class ProfanityFilterConfig {
    
    /**
     * 网易云API访问密钥ID
     */
    @JsonProperty("accessKeyId")
    private String accessKeyId;
    
    /**
     * 网易云API访问密钥
     */
    @JsonProperty("accessKeySecret")
    private String accessKeySecret;
    
    /**
     * 网易云API服务地址
     */
    @JsonProperty("endpoint")
    private String endpoint = "https://censor.netease.im";
    
    /**
     * 请求超时时间（毫秒）
     */
    @JsonProperty("timeout")
    private int timeout = 30000;
    
    /**
     * 连接超时时间（毫秒）
     */
    @JsonProperty("connectTimeout")
    private int connectTimeout = 10000;
    
    /**
     * 是否启用调试模式
     */
    @JsonProperty("debug")
    private boolean debug = false;
    
    /**
     * 默认构造函数
     */
    public ProfanityFilterConfig() {
    }
    
    /**
     * 构造函数
     * 
     * @param accessKeyId 访问密钥ID
     * @param accessKeySecret 访问密钥
     */
    public ProfanityFilterConfig(String accessKeyId, String accessKeySecret) {
        this.accessKeyId = accessKeyId;
        this.accessKeySecret = accessKeySecret;
    }
    
    /**
     * 构造函数
     * 
     * @param accessKeyId 访问密钥ID
     * @param accessKeySecret 访问密钥
     * @param endpoint API服务地址
     */
    public ProfanityFilterConfig(String accessKeyId, String accessKeySecret, String endpoint) {
        this.accessKeyId = accessKeyId;
        this.accessKeySecret = accessKeySecret;
        this.endpoint = endpoint;
    }
    
    // Getters and Setters
    public String getAccessKeyId() {
        return accessKeyId;
    }
    
    public void setAccessKeyId(String accessKeyId) {
        this.accessKeyId = accessKeyId;
    }
    
    public String getAccessKeySecret() {
        return accessKeySecret;
    }
    
    public void setAccessKeySecret(String accessKeySecret) {
        this.accessKeySecret = accessKeySecret;
    }
    
    public String getEndpoint() {
        return endpoint;
    }
    
    public void setEndpoint(String endpoint) {
        this.endpoint = endpoint;
    }
    
    public int getTimeout() {
        return timeout;
    }
    
    public void setTimeout(int timeout) {
        this.timeout = timeout;
    }
    
    public int getConnectTimeout() {
        return connectTimeout;
    }
    
    public void setConnectTimeout(int connectTimeout) {
        this.connectTimeout = connectTimeout;
    }
    
    public boolean isDebug() {
        return debug;
    }
    
    public void setDebug(boolean debug) {
        this.debug = debug;
    }
    
    /**
     * 验证配置是否有效
     * 
     * @return 配置是否有效
     */
    public boolean isValid() {
        return accessKeyId != null && !accessKeyId.trim().isEmpty() &&
               accessKeySecret != null && !accessKeySecret.trim().isEmpty() &&
               endpoint != null && !endpoint.trim().isEmpty();
    }
    
    @Override
    public String toString() {
        return "ProfanityFilterConfig{" +
                "accessKeyId='" + accessKeyId + '\'' +
                ", accessKeySecret='[HIDDEN]'" +
                ", endpoint='" + endpoint + '\'' +
                ", timeout=" + timeout +
                ", connectTimeout=" + connectTimeout +
                ", debug=" + debug +
                '}';
    }
}