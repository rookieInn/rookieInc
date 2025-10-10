package com.example.springbootapitiming.service;

import com.example.springbootapitiming.annotation.Timing;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 业务服务类
 * 演示使用@Timing注解计算方法执行时间
 */
@Service
public class BusinessService {

    /**
     * 快速业务方法
     */
    @Timing("快速业务处理")
    public Map<String, Object> quickBusiness() {
        Map<String, Object> result = new HashMap<>();
        result.put("message", "快速业务处理完成");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 慢速业务方法
     */
    @Timing("慢速业务处理")
    public Map<String, Object> slowBusiness() throws InterruptedException {
        // 模拟耗时操作
        Thread.sleep(2000);
        
        Map<String, Object> result = new HashMap<>();
        result.put("message", "慢速业务处理完成");
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 数据库操作模拟
     */
    @Timing("数据库操作")
    public Map<String, Object> databaseOperation(int recordCount) throws InterruptedException {
        // 模拟数据库操作时间
        long operationTime = recordCount * 50; // 每条记录50ms
        Thread.sleep(operationTime);
        
        Map<String, Object> result = new HashMap<>();
        result.put("message", "数据库操作完成");
        result.put("recordCount", recordCount);
        result.put("operationTime", operationTime);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 文件处理模拟
     */
    @Timing("文件处理操作")
    public Map<String, Object> fileProcessing(String filename, long fileSize) throws InterruptedException {
        // 模拟文件处理时间
        long processingTime = fileSize / 1024; // 每1KB需要1ms
        Thread.sleep(processingTime);
        
        Map<String, Object> result = new HashMap<>();
        result.put("message", "文件处理完成");
        result.put("filename", filename);
        result.put("fileSize", fileSize);
        result.put("processingTime", processingTime);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }

    /**
     * 复杂计算模拟
     */
    @Timing("复杂计算处理")
    public Map<String, Object> complexCalculation(int iterations) {
        long startTime = System.currentTimeMillis();
        
        // 模拟复杂计算
        long sum = 0;
        for (int i = 0; i < iterations; i++) {
            sum += Math.sqrt(i * i + 1);
        }
        
        long endTime = System.currentTimeMillis();
        long calculationTime = endTime - startTime;
        
        Map<String, Object> result = new HashMap<>();
        result.put("message", "复杂计算完成");
        result.put("iterations", iterations);
        result.put("sum", sum);
        result.put("calculationTime", calculationTime);
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
}