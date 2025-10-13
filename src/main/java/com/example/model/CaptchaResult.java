package com.example.model;

/**
 * 验证码生成结果
 * 
 * @author example
 * @version 1.0
 */
public class CaptchaResult {
    
    /**
     * 验证码图片的Base64编码
     */
    private String imageBase64;
    
    /**
     * 验证码答案
     */
    private String answer;
    
    /**
     * 验证码唯一标识
     */
    private String captchaId;
    
    /**
     * 过期时间（时间戳）
     */
    private long expireTime;

    public CaptchaResult() {
    }

    public CaptchaResult(String imageBase64, String answer, String captchaId, long expireTime) {
        this.imageBase64 = imageBase64;
        this.answer = answer;
        this.captchaId = captchaId;
        this.expireTime = expireTime;
    }

    // Getters and Setters
    public String getImageBase64() {
        return imageBase64;
    }

    public void setImageBase64(String imageBase64) {
        this.imageBase64 = imageBase64;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public String getCaptchaId() {
        return captchaId;
    }

    public void setCaptchaId(String captchaId) {
        this.captchaId = captchaId;
    }

    public long getExpireTime() {
        return expireTime;
    }

    public void setExpireTime(long expireTime) {
        this.expireTime = expireTime;
    }

    @Override
    public String toString() {
        return "CaptchaResult{" +
                "imageBase64='" + imageBase64 + '\'' +
                ", answer='" + answer + '\'' +
                ", captchaId='" + captchaId + '\'' +
                ", expireTime=" + expireTime +
                '}';
    }
}