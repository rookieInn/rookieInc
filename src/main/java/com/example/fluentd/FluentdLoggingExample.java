package com.example.fluentd;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.Marker;
import org.apache.logging.log4j.MarkerManager;
import org.apache.logging.log4j.ThreadContext;

import java.util.Random;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Fluentd日志采集示例应用程序
 * 演示如何将Java应用日志发送到Fluentd
 */
public class FluentdLoggingExample {
    
    private static final Logger logger = LogManager.getLogger(FluentdLoggingExample.class);
    private static final Marker BUSINESS_MARKER = MarkerManager.getMarker("BUSINESS");
    private static final Marker SECURITY_MARKER = MarkerManager.getMarker("SECURITY");
    private static final Marker PERFORMANCE_MARKER = MarkerManager.getMarker("PERFORMANCE");
    
    private static final Random random = new Random();
    private static final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    
    public static void main(String[] args) {
        logger.info("Fluentd日志采集示例应用程序启动");
        
        // 设置一些MDC数据
        ThreadContext.put("application", "fluentd-example");
        ThreadContext.put("version", "1.0.0");
        ThreadContext.put("environment", "development");
        
        try {
            // 演示不同类型的日志
            demonstrateBasicLogging();
            
            // 启动模拟业务日志
            startBusinessLogSimulation();
            
            // 启动性能监控日志
            startPerformanceMonitoring();
            
            // 运行一段时间后停止
            Thread.sleep(30000); // 运行30秒
            
        } catch (InterruptedException e) {
            logger.error("应用程序被中断", e);
        } finally {
            logger.info("Fluentd日志采集示例应用程序关闭");
            scheduler.shutdown();
            ThreadContext.clearAll();
        }
    }
    
    /**
     * 演示基本日志记录
     */
    private static void demonstrateBasicLogging() {
        logger.debug("这是一条调试日志");
        logger.info("这是一条信息日志");
        logger.warn("这是一条警告日志");
        logger.error("这是一条错误日志");
        
        // 带异常信息的日志
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            logger.error("发生算术异常", e);
        }
        
        // 使用Marker的日志
        logger.info(BUSINESS_MARKER, "这是一条业务日志");
        logger.warn(SECURITY_MARKER, "检测到可疑活动");
        logger.info(PERFORMANCE_MARKER, "性能指标记录");
    }
    
    /**
     * 启动业务日志模拟
     */
    private static void startBusinessLogSimulation() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                // 模拟用户操作
                String[] operations = {"用户登录", "查看商品", "添加购物车", "提交订单", "支付完成"};
                String operation = operations[random.nextInt(operations.length)];
                
                ThreadContext.put("userId", "user_" + (1000 + random.nextInt(9000)));
                ThreadContext.put("sessionId", "session_" + System.currentTimeMillis());
                
                logger.info(BUSINESS_MARKER, "用户操作: {}", operation);
                
                // 模拟一些业务异常
                if (random.nextDouble() < 0.1) {
                    logger.error(BUSINESS_MARKER, "业务操作失败: {}", operation);
                }
                
            } catch (Exception e) {
                logger.error("业务日志模拟出错", e);
            }
        }, 0, 2, TimeUnit.SECONDS);
    }
    
    /**
     * 启动性能监控日志
     */
    private static void startPerformanceMonitoring() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                // 模拟性能指标
                long responseTime = 50 + random.nextInt(200); // 50-250ms
                int memoryUsage = 60 + random.nextInt(40); // 60-100%
                int cpuUsage = 20 + random.nextInt(60); // 20-80%
                
                ThreadContext.put("responseTime", String.valueOf(responseTime));
                ThreadContext.put("memoryUsage", String.valueOf(memoryUsage));
                ThreadContext.put("cpuUsage", String.valueOf(cpuUsage));
                
                if (responseTime > 200) {
                    logger.warn(PERFORMANCE_MARKER, "响应时间过长: {}ms", responseTime);
                } else {
                    logger.info(PERFORMANCE_MARKER, "性能指标正常 - 响应时间: {}ms, 内存使用: {}%, CPU使用: {}%", 
                              responseTime, memoryUsage, cpuUsage);
                }
                
                // 模拟内存泄漏警告
                if (memoryUsage > 90) {
                    logger.error(PERFORMANCE_MARKER, "内存使用率过高: {}%", memoryUsage);
                }
                
            } catch (Exception e) {
                logger.error("性能监控日志出错", e);
            }
        }, 0, 5, TimeUnit.SECONDS);
    }
    
    /**
     * 模拟API请求日志
     */
    public static void logApiRequest(String method, String endpoint, int statusCode, long duration) {
        ThreadContext.put("httpMethod", method);
        ThreadContext.put("endpoint", endpoint);
        ThreadContext.put("statusCode", String.valueOf(statusCode));
        ThreadContext.put("duration", String.valueOf(duration));
        
        if (statusCode >= 400) {
            logger.warn("API请求失败: {} {} - 状态码: {}, 耗时: {}ms", method, endpoint, statusCode, duration);
        } else {
            logger.info("API请求成功: {} {} - 状态码: {}, 耗时: {}ms", method, endpoint, statusCode, duration);
        }
    }
    
    /**
     * 模拟数据库操作日志
     */
    public static void logDatabaseOperation(String operation, String table, long duration, boolean success) {
        ThreadContext.put("dbOperation", operation);
        ThreadContext.put("table", table);
        ThreadContext.put("dbDuration", String.valueOf(duration));
        
        if (success) {
            logger.info("数据库操作成功: {} 表 {} - 耗时: {}ms", operation, table, duration);
        } else {
            logger.error("数据库操作失败: {} 表 {} - 耗时: {}ms", operation, table, duration);
        }
    }
}