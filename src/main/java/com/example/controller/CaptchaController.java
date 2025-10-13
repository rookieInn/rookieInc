package com.example.controller;

import com.example.model.CaptchaResult;
import com.example.service.CaptchaService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 图形验证码控制器
 * 
 * @author example
 * @version 1.0
 */
@RestController
@RequestMapping("/api/captcha")
@CrossOrigin(origins = "*")
public class CaptchaController {
    
    private static final Logger logger = LoggerFactory.getLogger(CaptchaController.class);
    
    @Autowired
    private CaptchaService captchaService;
    
    /**
     * 生成图形验证码
     * 
     * @return ResponseEntity<Map<String, Object>> 包含验证码信息的响应
     */
    @GetMapping("/generate")
    public ResponseEntity<Map<String, Object>> generateCaptcha() {
        try {
            CaptchaResult captchaResult = captchaService.generateCaptcha();
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "验证码生成成功");
            response.put("data", captchaResult);
            
            logger.info("生成验证码成功，ID: {}", captchaResult.getCaptchaId());
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("生成验证码失败", e);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "生成验证码失败: " + e.getMessage());
            response.put("data", null);
            
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * 验证图形验证码
     * 
     * @param captchaId 验证码ID
     * @param captchaCode 用户输入的验证码
     * @return ResponseEntity<Map<String, Object>> 验证结果
     */
    @PostMapping("/verify")
    public ResponseEntity<Map<String, Object>> verifyCaptcha(
            @RequestParam("captchaId") String captchaId,
            @RequestParam("captchaCode") String captchaCode) {
        
        try {
            boolean isValid = captchaService.verifyCaptcha(captchaId, captchaCode);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", isValid ? "验证码验证成功" : "验证码验证失败");
            response.put("valid", isValid);
            
            logger.info("验证码验证结果: {}, ID: {}, 用户输入: {}", isValid, captchaId, captchaCode);
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("验证验证码时发生错误", e);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("message", "验证验证码时发生错误: " + e.getMessage());
            response.put("valid", false);
            
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * 刷新验证码（重新生成）
     * 
     * @return ResponseEntity<Map<String, Object>> 新的验证码信息
     */
    @GetMapping("/refresh")
    public ResponseEntity<Map<String, Object>> refreshCaptcha() {
        return generateCaptcha();
    }
}