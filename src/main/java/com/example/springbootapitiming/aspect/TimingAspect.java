package com.example.springbootapitiming.aspect;

import com.example.springbootapitiming.annotation.Timing;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * 处理时间切面
 * 使用AOP方式计算方法执行时间
 */
@Aspect
@Component
public class TimingAspect {

    private static final Logger logger = LoggerFactory.getLogger(TimingAspect.class);

    @Around("@annotation(timing)")
    public Object around(ProceedingJoinPoint joinPoint, Timing timing) throws Throwable {
        long startTime = System.currentTimeMillis();
        
        try {
            Object result = joinPoint.proceed();
            return result;
        } finally {
            long endTime = System.currentTimeMillis();
            long executionTime = endTime - startTime;
            
            String methodName = joinPoint.getSignature().toShortString();
            String description = timing.value().isEmpty() ? methodName : timing.value();
            
            if (timing.log()) {
                logger.info("方法执行完成: {} - 执行时间: {}ms", description, executionTime);
            }
        }
    }
}