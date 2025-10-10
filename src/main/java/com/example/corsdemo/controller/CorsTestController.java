package com.example.corsdemo.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * CORS测试控制器
 * 展示不同的跨域配置方法
 * 
 * @author example
 * @version 1.0.0
 */
@RestController
@RequestMapping("/cors")
public class CorsTestController {

    /**
     * 方法4: 在方法级别使用@CrossOrigin注解
     * 只对特定方法生效
     */
    @GetMapping("/method-level")
    @CrossOrigin(
        origins = {"http://localhost:3000", "http://127.0.0.1:3000"},
        methods = {RequestMethod.GET, RequestMethod.POST},
        allowedHeaders = "*",
        allowCredentials = "true"
    )
    public ResponseEntity<Map<String, Object>> methodLevelCors() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "方法级别CORS配置测试");
        response.put("timestamp", LocalDateTime.now());
        response.put("corsMethod", "方法级别@CrossOrigin注解");
        response.put("allowedOrigins", "http://localhost:3000, http://127.0.0.1:3000");
        
        return ResponseEntity.ok(response);
    }

    /**
     * 方法5: 使用@CrossOrigin注解配置特定路径
     */
    @PostMapping("/specific-path")
    @CrossOrigin(
        origins = "*",
        methods = {RequestMethod.POST, RequestMethod.OPTIONS},
        allowedHeaders = {"Content-Type", "Authorization", "Custom-Header"},
        exposedHeaders = {"X-Custom-Response-Header"},
        allowCredentials = "false",
        maxAge = 1800
    )
    public ResponseEntity<Map<String, Object>> specificPathCors(@RequestBody(required = false) Map<String, Object> data) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "特定路径CORS配置测试");
        response.put("timestamp", LocalDateTime.now());
        response.put("corsMethod", "特定路径@CrossOrigin注解");
        response.put("receivedData", data);
        response.put("maxAge", "1800秒");
        
        // 设置自定义响应头
        return ResponseEntity.ok()
                .header("X-Custom-Response-Header", "CORS-Test-Value")
                .body(response);
    }

    /**
     * 方法6: 手动处理OPTIONS预检请求
     */
    @RequestMapping(value = "/manual-options", method = RequestMethod.OPTIONS)
    public ResponseEntity<Void> handleOptions() {
        return ResponseEntity.ok()
                .header("Access-Control-Allow-Origin", "*")
                .header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                .header("Access-Control-Allow-Headers", "Content-Type, Authorization, Custom-Header")
                .header("Access-Control-Max-Age", "3600")
                .build();
    }

    /**
     * 对应的GET请求
     */
    @GetMapping("/manual-options")
    public ResponseEntity<Map<String, Object>> manualOptionsGet() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "手动处理OPTIONS预检请求测试");
        response.put("timestamp", LocalDateTime.now());
        response.put("corsMethod", "手动处理OPTIONS请求");
        
        return ResponseEntity.ok()
                .header("Access-Control-Allow-Origin", "*")
                .header("Access-Control-Expose-Headers", "X-Custom-Response-Header")
                .header("X-Custom-Response-Header", "Manual-CORS-Test")
                .body(response);
    }

    /**
     * 测试复杂请求（需要预检）
     */
    @PostMapping("/complex-request")
    @CrossOrigin(
        origins = "*",
        methods = {RequestMethod.POST},
        allowedHeaders = {"Content-Type", "Authorization", "X-Custom-Header", "X-Requested-With"},
        exposedHeaders = {"X-Response-Header", "X-Total-Count"},
        allowCredentials = "true"
    )
    public ResponseEntity<Map<String, Object>> complexRequest(
            @RequestHeader(value = "X-Custom-Header", required = false) String customHeader,
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestBody(required = false) Map<String, Object> data) {
        
        Map<String, Object> response = new HashMap<>();
        response.put("message", "复杂请求CORS测试");
        response.put("timestamp", LocalDateTime.now());
        response.put("corsMethod", "复杂请求处理");
        response.put("customHeader", customHeader);
        response.put("authorization", auth != null ? "已提供" : "未提供");
        response.put("requestData", data);
        
        return ResponseEntity.ok()
                .header("X-Response-Header", "Complex-Request-Success")
                .header("X-Total-Count", "1")
                .body(response);
    }
}