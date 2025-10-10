package com.example.corsdemo.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

/**
 * API控制器
 * 提供各种HTTP方法的接口用于测试跨域
 * 
 * @author example
 * @version 1.0.0
 */
@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*", maxAge = 3600)  // 方法3: 在Controller级别使用@CrossOrigin注解
public class ApiController {

    /**
     * GET请求测试
     */
    @GetMapping("/test")
    public ResponseEntity<Map<String, Object>> testGet() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "GET请求成功！");
        response.put("timestamp", LocalDateTime.now());
        response.put("method", "GET");
        response.put("cors", "已配置跨域支持");
        
        return ResponseEntity.ok(response);
    }

    /**
     * POST请求测试
     */
    @PostMapping("/test")
    public ResponseEntity<Map<String, Object>> testPost(@RequestBody(required = false) Map<String, Object> data) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "POST请求成功！");
        response.put("timestamp", LocalDateTime.now());
        response.put("method", "POST");
        response.put("receivedData", data);
        response.put("cors", "已配置跨域支持");
        
        return ResponseEntity.ok(response);
    }

    /**
     * PUT请求测试
     */
    @PutMapping("/test/{id}")
    public ResponseEntity<Map<String, Object>> testPut(@PathVariable String id, @RequestBody(required = false) Map<String, Object> data) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "PUT请求成功！");
        response.put("timestamp", LocalDateTime.now());
        response.put("method", "PUT");
        response.put("id", id);
        response.put("receivedData", data);
        response.put("cors", "已配置跨域支持");
        
        return ResponseEntity.ok(response);
    }

    /**
     * DELETE请求测试
     */
    @DeleteMapping("/test/{id}")
    public ResponseEntity<Map<String, Object>> testDelete(@PathVariable String id) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "DELETE请求成功！");
        response.put("timestamp", LocalDateTime.now());
        response.put("method", "DELETE");
        response.put("id", id);
        response.put("cors", "已配置跨域支持");
        
        return ResponseEntity.ok(response);
    }

    /**
     * OPTIONS请求测试（预检请求）
     */
    @RequestMapping(value = "/test", method = RequestMethod.OPTIONS)
    public ResponseEntity<Void> testOptions() {
        return ResponseEntity.ok().build();
    }

    /**
     * 带自定义请求头的测试
     */
    @PostMapping("/test/headers")
    public ResponseEntity<Map<String, Object>> testWithHeaders(
            @RequestHeader(value = "Custom-Header", required = false) String customHeader,
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        
        Map<String, Object> response = new HashMap<>();
        response.put("message", "带自定义请求头的POST请求成功！");
        response.put("timestamp", LocalDateTime.now());
        response.put("method", "POST");
        response.put("customHeader", customHeader);
        response.put("authorization", authorization != null ? "已提供" : "未提供");
        response.put("cors", "已配置跨域支持");
        
        return ResponseEntity.ok(response);
    }

    /**
     * 返回JSON数据的测试
     */
    @GetMapping("/data")
    public ResponseEntity<Map<String, Object>> getData() {
        Map<String, Object> data = new HashMap<>();
        data.put("users", Arrays.asList(
            Map.of("id", 1, "name", "张三", "email", "zhangsan@example.com"),
            Map.of("id", 2, "name", "李四", "email", "lisi@example.com"),
            Map.of("id", 3, "name", "王五", "email", "wangwu@example.com")
        ));
        data.put("total", 3);
        data.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.ok(data);
    }
}