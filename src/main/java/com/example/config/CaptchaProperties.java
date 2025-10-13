package com.example.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 验证码配置属性类
 * 
 * @author example
 * @version 1.0
 */
@Component
@ConfigurationProperties(prefix = "captcha")
public class CaptchaProperties {
    
    /**
     * 验证码长度
     */
    private int length = 4;
    
    /**
     * 验证码过期时间（秒）
     */
    private int expireTime = 300;
    
    /**
     * 图片宽度
     */
    private int width = 120;
    
    /**
     * 图片高度
     */
    private int height = 40;
    
    /**
     * 干扰线数量
     */
    private int lineCount = 20;
    
    /**
     * 干扰点数量
     */
    private int pointCount = 50;
    
    /**
     * 字体大小
     */
    private int fontSize = 24;
    
    /**
     * 字符集
     */
    private String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    // Getters and Setters
    public int getLength() {
        return length;
    }

    public void setLength(int length) {
        this.length = length;
    }

    public int getExpireTime() {
        return expireTime;
    }

    public void setExpireTime(int expireTime) {
        this.expireTime = expireTime;
    }

    public int getWidth() {
        return width;
    }

    public void setWidth(int width) {
        this.width = width;
    }

    public int getHeight() {
        return height;
    }

    public void setHeight(int height) {
        this.height = height;
    }

    public int getLineCount() {
        return lineCount;
    }

    public void setLineCount(int lineCount) {
        this.lineCount = lineCount;
    }

    public int getPointCount() {
        return pointCount;
    }

    public void setPointCount(int pointCount) {
        this.pointCount = pointCount;
    }

    public int getFontSize() {
        return fontSize;
    }

    public void setFontSize(int fontSize) {
        this.fontSize = fontSize;
    }

    public String getChars() {
        return chars;
    }

    public void setChars(String chars) {
        this.chars = chars;
    }
}