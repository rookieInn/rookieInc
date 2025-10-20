package com.netease.profanity.filter.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * 过滤响应模型
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class FilterResponse {
    
    /**
     * 响应码：200-成功，其他-失败
     */
    @JsonProperty("code")
    private Integer code;
    
    /**
     * 响应消息
     */
    @JsonProperty("message")
    private String message;
    
    /**
     * 业务ID
     */
    @JsonProperty("businessId")
    private String businessId;
    
    /**
     * 检测结果：0-通过，1-不通过，2-疑似
     */
    @JsonProperty("action")
    private Integer action;
    
    /**
     * 置信度（0-100）
     */
    @JsonProperty("confidence")
    private Double confidence;
    
    /**
     * 检测到的敏感词列表
     */
    @JsonProperty("sensitiveWords")
    private List<String> sensitiveWords;
    
    /**
     * 详细信息
     */
    @JsonProperty("details")
    private List<FilterDetail> details;
    
    /**
     * 请求ID
     */
    @JsonProperty("requestId")
    private String requestId;
    
    /**
     * 处理时间（毫秒）
     */
    @JsonProperty("processTime")
    private Long processTime;
    
    /**
     * 默认构造函数
     */
    public FilterResponse() {
    }
    
    // Getters and Setters
    public Integer getCode() {
        return code;
    }
    
    public void setCode(Integer code) {
        this.code = code;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public String getBusinessId() {
        return businessId;
    }
    
    public void setBusinessId(String businessId) {
        this.businessId = businessId;
    }
    
    public Integer getAction() {
        return action;
    }
    
    public void setAction(Integer action) {
        this.action = action;
    }
    
    public Double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }
    
    public List<String> getSensitiveWords() {
        return sensitiveWords;
    }
    
    public void setSensitiveWords(List<String> sensitiveWords) {
        this.sensitiveWords = sensitiveWords;
    }
    
    public List<FilterDetail> getDetails() {
        return details;
    }
    
    public void setDetails(List<FilterDetail> details) {
        this.details = details;
    }
    
    public String getRequestId() {
        return requestId;
    }
    
    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }
    
    public Long getProcessTime() {
        return processTime;
    }
    
    public void setProcessTime(Long processTime) {
        this.processTime = processTime;
    }
    
    /**
     * 判断是否检测通过
     * 
     * @return 是否通过
     */
    public boolean isPass() {
        return code != null && code == 200 && action != null && action == 0;
    }
    
    /**
     * 判断是否检测不通过
     * 
     * @return 是否不通过
     */
    public boolean isReject() {
        return code != null && code == 200 && action != null && action == 1;
    }
    
    /**
     * 判断是否为疑似内容
     * 
     * @return 是否为疑似
     */
    public boolean isSuspect() {
        return code != null && code == 200 && action != null && action == 2;
    }
    
    @Override
    public String toString() {
        return "FilterResponse{" +
                "code=" + code +
                ", message='" + message + '\'' +
                ", businessId='" + businessId + '\'' +
                ", action=" + action +
                ", confidence=" + confidence +
                ", sensitiveWords=" + sensitiveWords +
                ", details=" + details +
                ", requestId='" + requestId + '\'' +
                ", processTime=" + processTime +
                '}';
    }
}