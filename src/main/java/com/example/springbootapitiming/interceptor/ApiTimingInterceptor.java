package com.example.springbootapitiming.interceptor;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * API 处理时间拦截器
 * 用于计算每个API接口的处理时间
 */
@Component
public class ApiTimingInterceptor implements HandlerInterceptor {

    private static final Logger logger = LoggerFactory.getLogger(ApiTimingInterceptor.class);
    private static final String START_TIME_ATTRIBUTE = "startTime";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        // 记录请求开始时间
        long startTime = System.currentTimeMillis();
        request.setAttribute(START_TIME_ATTRIBUTE, startTime);
        
        logger.info("API请求开始: {} {}", request.getMethod(), request.getRequestURI());
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        // 计算处理时间
        Long startTime = (Long) request.getAttribute(START_TIME_ATTRIBUTE);
        if (startTime != null) {
            long endTime = System.currentTimeMillis();
            long processingTime = endTime - startTime;
            
            // 记录处理时间
            logger.info("API请求完成: {} {} - 处理时间: {}ms, 状态码: {}", 
                       request.getMethod(), 
                       request.getRequestURI(), 
                       processingTime,
                       response.getStatus());
            
            // 将处理时间添加到响应头中
            response.setHeader("X-Processing-Time", String.valueOf(processingTime));
            response.setHeader("X-Processing-Time-Unit", "ms");
        }
    }
}