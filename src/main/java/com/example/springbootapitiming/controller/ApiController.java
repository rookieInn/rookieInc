package com.example.springbootapitiming.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * API控制器
 * 提供各种测试接口用于演示处理时间计算
 */
@RestController
@RequestMapping("/api")
public class ApiController {

    /**
     * 快速响应接口
     */
    @GetMapping("/quick")
    public ResponseEntity<Map<String, Object>> quickResponse() {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "快速响应接口");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }

    /**
     * 模拟处理时间接口
     */
    @GetMapping("/process")
    public ResponseEntity<Map<String, Object>> processData(@RequestParam(defaultValue = "1000") long delay) {
        try {
            // 模拟处理时间
            Thread.sleep(delay);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "数据处理完成");
            response.put("delay", delay);
            response.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.ok(response);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 数据库查询模拟接口
     */
    @GetMapping("/database")
    public ResponseEntity<Map<String, Object>> databaseQuery(@RequestParam(defaultValue = "10") int records) {
        try {
            // 模拟数据库查询时间（每10条记录需要100ms）
            long queryTime = records * 10;
            Thread.sleep(queryTime);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "数据库查询完成");
            response.put("records", records);
            response.put("queryTime", queryTime);
            response.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.ok(response);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 文件处理模拟接口
     */
    @PostMapping("/file")
    public ResponseEntity<Map<String, Object>> processFile(@RequestParam String filename, 
                                                          @RequestParam(defaultValue = "1024") int size) {
        try {
            // 模拟文件处理时间（每1KB需要1ms）
            long processTime = size;
            Thread.sleep(processTime);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "文件处理完成");
            response.put("filename", filename);
            response.put("size", size);
            response.put("processTime", processTime);
            response.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.ok(response);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 复杂业务逻辑模拟接口
     */
    @GetMapping("/complex")
    public ResponseEntity<Map<String, Object>> complexBusiness(@RequestParam(defaultValue = "5") int steps) {
        try {
            long totalTime = 0;
            
            // 模拟多个业务步骤
            for (int i = 1; i <= steps; i++) {
                long stepTime = i * 200; // 每个步骤递增200ms
                Thread.sleep(stepTime);
                totalTime += stepTime;
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "复杂业务逻辑处理完成");
            response.put("steps", steps);
            response.put("totalTime", totalTime);
            response.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.ok(response);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 健康检查接口（不计算处理时间）
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
}