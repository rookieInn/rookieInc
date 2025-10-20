package com.netease.profanity.filter.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 文本过滤请求模型
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class TextFilterRequest {
    
    /**
     * 待检测的文本内容
     */
    @JsonProperty("text")
    private String text;
    
    /**
     * 业务ID，用于追踪请求
     */
    @JsonProperty("businessId")
    private String businessId;
    
    /**
     * 用户ID
     */
    @JsonProperty("userId")
    private String userId;
    
    /**
     * 检测类型：1-文本检测，2-图片检测
     */
    @JsonProperty("type")
    private Integer type = 1;
    
    /**
     * 检测场景：1-通用，2-社交，3-电商，4-直播
     */
    @JsonProperty("scene")
    private Integer scene = 1;
    
    /**
     * 是否返回详细信息
     */
    @JsonProperty("detail")
    private Boolean detail = true;
    
    /**
     * 默认构造函数
     */
    public TextFilterRequest() {
    }
    
    /**
     * 构造函数
     * 
     * @param text 待检测的文本内容
     */
    public TextFilterRequest(String text) {
        this.text = text;
    }
    
    /**
     * 构造函数
     * 
     * @param text 待检测的文本内容
     * @param businessId 业务ID
     */
    public TextFilterRequest(String text, String businessId) {
        this.text = text;
        this.businessId = businessId;
    }
    
    // Getters and Setters
    public String getText() {
        return text;
    }
    
    public void setText(String text) {
        this.text = text;
    }
    
    public String getBusinessId() {
        return businessId;
    }
    
    public void setBusinessId(String businessId) {
        this.businessId = businessId;
    }
    
    public String getUserId() {
        return userId;
    }
    
    public void setUserId(String userId) {
        this.userId = userId;
    }
    
    public Integer getType() {
        return type;
    }
    
    public void setType(Integer type) {
        this.type = type;
    }
    
    public Integer getScene() {
        return scene;
    }
    
    public void setScene(Integer scene) {
        this.scene = scene;
    }
    
    public Boolean getDetail() {
        return detail;
    }
    
    public void setDetail(Boolean detail) {
        this.detail = detail;
    }
    
    @Override
    public String toString() {
        return "TextFilterRequest{" +
                "text='" + text + '\'' +
                ", businessId='" + businessId + '\'' +
                ", userId='" + userId + '\'' +
                ", type=" + type +
                ", scene=" + scene +
                ", detail=" + detail +
                '}';
    }
}