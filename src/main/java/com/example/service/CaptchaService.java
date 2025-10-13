package com.example.service;

import com.example.config.CaptchaProperties;
import com.example.model.CaptchaResult;
import org.apache.commons.lang3.RandomStringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Base64;
import java.util.Random;
import java.util.concurrent.TimeUnit;

/**
 * 图形验证码服务类
 * 
 * @author example
 * @version 1.0
 */
@Service
public class CaptchaService {
    
    private static final Logger logger = LoggerFactory.getLogger(CaptchaService.class);
    
    @Autowired
    private CaptchaProperties captchaProperties;
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String CAPTCHA_PREFIX = "captcha:";
    
    /**
     * 生成图形验证码
     * 
     * @return CaptchaResult 验证码结果
     */
    public CaptchaResult generateCaptcha() {
        try {
            // 生成验证码答案
            String answer = RandomStringUtils.random(captchaProperties.getLength(), captchaProperties.getChars());
            
            // 生成验证码图片
            BufferedImage image = createCaptchaImage(answer);
            
            // 将图片转换为Base64
            String imageBase64 = imageToBase64(image);
            
            // 生成验证码ID
            String captchaId = RandomStringUtils.randomAlphanumeric(32);
            
            // 计算过期时间
            long expireTime = System.currentTimeMillis() + captchaProperties.getExpireTime() * 1000L;
            
            // 存储到Redis
            redisTemplate.opsForValue().set(
                CAPTCHA_PREFIX + captchaId, 
                answer, 
                captchaProperties.getExpireTime(), 
                TimeUnit.SECONDS
            );
            
            logger.info("生成验证码成功，ID: {}, 答案: {}", captchaId, answer);
            
            return new CaptchaResult(imageBase64, answer, captchaId, expireTime);
            
        } catch (Exception e) {
            logger.error("生成验证码失败", e);
            throw new RuntimeException("生成验证码失败", e);
        }
    }
    
    /**
     * 验证验证码
     * 
     * @param captchaId 验证码ID
     * @param userInput 用户输入
     * @return boolean 验证结果
     */
    public boolean verifyCaptcha(String captchaId, String userInput) {
        if (captchaId == null || userInput == null) {
            return false;
        }
        
        try {
            String storedAnswer = redisTemplate.opsForValue().get(CAPTCHA_PREFIX + captchaId);
            
            if (storedAnswer == null) {
                logger.warn("验证码不存在或已过期，ID: {}", captchaId);
                return false;
            }
            
            boolean isValid = storedAnswer.equalsIgnoreCase(userInput.trim());
            
            if (isValid) {
                // 验证成功后删除验证码
                redisTemplate.delete(CAPTCHA_PREFIX + captchaId);
                logger.info("验证码验证成功，ID: {}", captchaId);
            } else {
                logger.warn("验证码验证失败，ID: {}, 用户输入: {}, 正确答案: {}", captchaId, userInput, storedAnswer);
            }
            
            return isValid;
            
        } catch (Exception e) {
            logger.error("验证验证码时发生错误", e);
            return false;
        }
    }
    
    /**
     * 创建验证码图片
     * 
     * @param text 验证码文本
     * @return BufferedImage 验证码图片
     */
    private BufferedImage createCaptchaImage(String text) {
        int width = captchaProperties.getWidth();
        int height = captchaProperties.getHeight();
        
        BufferedImage image = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = image.createGraphics();
        
        // 设置抗锯齿
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2d.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        
        // 设置背景色
        g2d.setColor(Color.WHITE);
        g2d.fillRect(0, 0, width, height);
        
        // 绘制边框
        g2d.setColor(Color.BLACK);
        g2d.drawRect(0, 0, width - 1, height - 1);
        
        // 绘制干扰线
        drawInterferenceLines(g2d, width, height);
        
        // 绘制干扰点
        drawInterferencePoints(g2d, width, height);
        
        // 绘制验证码文字
        drawText(g2d, text, width, height);
        
        g2d.dispose();
        return image;
    }
    
    /**
     * 绘制干扰线
     */
    private void drawInterferenceLines(Graphics2D g2d, int width, int height) {
        Random random = new Random();
        g2d.setStroke(new BasicStroke(1.0f));
        
        for (int i = 0; i < captchaProperties.getLineCount(); i++) {
            int x1 = random.nextInt(width);
            int y1 = random.nextInt(height);
            int x2 = random.nextInt(width);
            int y2 = random.nextInt(height);
            
            g2d.setColor(new Color(random.nextInt(255), random.nextInt(255), random.nextInt(255)));
            g2d.drawLine(x1, y1, x2, y2);
        }
    }
    
    /**
     * 绘制干扰点
     */
    private void drawInterferencePoints(Graphics2D g2d, int width, int height) {
        Random random = new Random();
        
        for (int i = 0; i < captchaProperties.getPointCount(); i++) {
            int x = random.nextInt(width);
            int y = random.nextInt(height);
            
            g2d.setColor(new Color(random.nextInt(255), random.nextInt(255), random.nextInt(255)));
            g2d.fillOval(x, y, 2, 2);
        }
    }
    
    /**
     * 绘制验证码文字
     */
    private void drawText(Graphics2D g2d, String text, int width, int height) {
        Random random = new Random();
        Font font = new Font("Arial", Font.BOLD, captchaProperties.getFontSize());
        g2d.setFont(font);
        
        FontMetrics fontMetrics = g2d.getFontMetrics();
        int textWidth = fontMetrics.stringWidth(text);
        int textHeight = fontMetrics.getHeight();
        
        int startX = (width - textWidth) / 2;
        int startY = (height - textHeight) / 2 + fontMetrics.getAscent();
        
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            int x = startX + i * (textWidth / text.length());
            int y = startY + random.nextInt(10) - 5; // 随机上下偏移
            
            // 随机颜色
            g2d.setColor(new Color(random.nextInt(100), random.nextInt(100), random.nextInt(100)));
            
            // 随机旋转角度
            double angle = (random.nextDouble() - 0.5) * 0.5; // -0.25 到 0.25 弧度
            g2d.rotate(angle, x, y);
            
            g2d.drawString(String.valueOf(c), x, y);
            
            // 恢复旋转
            g2d.rotate(-angle, x, y);
        }
    }
    
    /**
     * 将图片转换为Base64字符串
     */
    private String imageToBase64(BufferedImage image) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ImageIO.write(image, "PNG", baos);
        byte[] imageBytes = baos.toByteArray();
        return "data:image/png;base64," + Base64.getEncoder().encodeToString(imageBytes);
    }
}