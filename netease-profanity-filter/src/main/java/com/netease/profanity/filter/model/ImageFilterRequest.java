package com.netease.profanity.filter.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 图片过滤请求模型
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class ImageFilterRequest {
    
    /**
     * 图片URL地址
     */
    @JsonProperty("imageUrl")
    private String imageUrl;
    
    /**
     * 图片Base64编码数据
     */
    @JsonProperty("imageData")
    private String imageData;
    
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
    private Integer type = 2;
    
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
    public ImageFilterRequest() {
    }
    
    /**
     * 构造函数
     * 
     * @param imageUrl 图片URL地址
     */
    public ImageFilterRequest(String imageUrl) {
        this.imageUrl = imageUrl;
    }
    
    /**
     * 构造函数
     * 
     * @param imageData 图片Base64编码数据
     * @param isBase64 标识是否为Base64数据
     */
    public ImageFilterRequest(String imageData, boolean isBase64) {
        if (isBase64) {
            this.imageData = imageData;
        } else {
            this.imageUrl = imageData;
        }
    }
    
    // Getters and Setters
    public String getImageUrl() {
        return imageUrl;
    }
    
    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }
    
    public String getImageData() {
        return imageData;
    }
    
    public void setImageData(String imageData) {
        this.imageData = imageData;
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
    
    /**
     * 验证请求是否有效
     * 
     * @return 请求是否有效
     */
    public boolean isValid() {
        return (imageUrl != null && !imageUrl.trim().isEmpty()) ||
               (imageData != null && !imageData.trim().isEmpty());
    }
    
    @Override
    public String toString() {
        return "ImageFilterRequest{" +
                "imageUrl='" + imageUrl + '\'' +
                ", imageData='" + (imageData != null ? "[BASE64_DATA]" : "null") + '\'' +
                ", businessId='" + businessId + '\'' +
                ", userId='" + userId + '\'' +
                ", type=" + type +
                ", scene=" + scene +
                ", detail=" + detail +
                '}';
    }
}