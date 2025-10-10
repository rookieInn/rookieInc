package com.example.springbootapitiming.controller;

import com.example.springbootapitiming.service.BusinessService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 服务控制器
 * 演示使用@Timing注解的服务方法
 */
@RestController
@RequestMapping("/api/service")
public class ServiceController {

    @Autowired
    private BusinessService businessService;

    /**
     * 快速业务接口
     */
    @GetMapping("/quick")
    public ResponseEntity<Map<String, Object>> quickBusiness() {
        Map<String, Object> result = businessService.quickBusiness();
        return ResponseEntity.ok(result);
    }

    /**
     * 慢速业务接口
     */
    @GetMapping("/slow")
    public ResponseEntity<Map<String, Object>> slowBusiness() throws InterruptedException {
        Map<String, Object> result = businessService.slowBusiness();
        return ResponseEntity.ok(result);
    }

    /**
     * 数据库操作接口
     */
    @GetMapping("/database")
    public ResponseEntity<Map<String, Object>> databaseOperation(@RequestParam(defaultValue = "20") int records) throws InterruptedException {
        Map<String, Object> result = businessService.databaseOperation(records);
        return ResponseEntity.ok(result);
    }

    /**
     * 文件处理接口
     */
    @PostMapping("/file")
    public ResponseEntity<Map<String, Object>> fileProcessing(@RequestParam String filename, 
                                                            @RequestParam(defaultValue = "2048") long fileSize) throws InterruptedException {
        Map<String, Object> result = businessService.fileProcessing(filename, fileSize);
        return ResponseEntity.ok(result);
    }

    /**
     * 复杂计算接口
     */
    @GetMapping("/calculation")
    public ResponseEntity<Map<String, Object>> complexCalculation(@RequestParam(defaultValue = "100000") int iterations) {
        Map<String, Object> result = businessService.complexCalculation(iterations);
        return ResponseEntity.ok(result);
    }
}