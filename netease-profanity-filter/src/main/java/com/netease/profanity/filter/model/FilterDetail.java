package com.netease.profanity.filter.model;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 过滤详细信息模型
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
public class FilterDetail {
    
    /**
     * 敏感词类型
     */
    @JsonProperty("type")
    private String type;
    
    /**
     * 敏感词内容
     */
    @JsonProperty("word")
    private String word;
    
    /**
     * 敏感词位置（开始位置）
     */
    @JsonProperty("start")
    private Integer start;
    
    /**
     * 敏感词位置（结束位置）
     */
    @JsonProperty("end")
    private Integer end;
    
    /**
     * 置信度
     */
    @JsonProperty("confidence")
    private Double confidence;
    
    /**
     * 风险等级：1-低风险，2-中风险，3-高风险
     */
    @JsonProperty("riskLevel")
    private Integer riskLevel;
    
    /**
     * 建议操作：1-通过，2-拒绝，3-人工审核
     */
    @JsonProperty("suggestion")
    private Integer suggestion;
    
    /**
     * 默认构造函数
     */
    public FilterDetail() {
    }
    
    /**
     * 构造函数
     * 
     * @param type 敏感词类型
     * @param word 敏感词内容
     * @param start 开始位置
     * @param end 结束位置
     */
    public FilterDetail(String type, String word, Integer start, Integer end) {
        this.type = type;
        this.word = word;
        this.start = start;
        this.end = end;
    }
    
    // Getters and Setters
    public String getType() {
        return type;
    }
    
    public void setType(String type) {
        this.type = type;
    }
    
    public String getWord() {
        return word;
    }
    
    public void setWord(String word) {
        this.word = word;
    }
    
    public Integer getStart() {
        return start;
    }
    
    public void setStart(Integer start) {
        this.start = start;
    }
    
    public Integer getEnd() {
        return end;
    }
    
    public void setEnd(Integer end) {
        this.end = end;
    }
    
    public Double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }
    
    public Integer getRiskLevel() {
        return riskLevel;
    }
    
    public void setRiskLevel(Integer riskLevel) {
        this.riskLevel = riskLevel;
    }
    
    public Integer getSuggestion() {
        return suggestion;
    }
    
    public void setSuggestion(Integer suggestion) {
        this.suggestion = suggestion;
    }
    
    @Override
    public String toString() {
        return "FilterDetail{" +
                "type='" + type + '\'' +
                ", word='" + word + '\'' +
                ", start=" + start +
                ", end=" + end +
                ", confidence=" + confidence +
                ", riskLevel=" + riskLevel +
                ", suggestion=" + suggestion +
                '}';
    }
}