package com.example.springbootapitiming.config;

import com.example.springbootapitiming.interceptor.ApiTimingInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web配置类
 * 配置API处理时间拦截器
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private ApiTimingInterceptor apiTimingInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(apiTimingInterceptor)
                .addPathPatterns("/api/**")  // 只拦截 /api/** 路径的请求
                .excludePathPatterns("/api/health"); // 排除健康检查接口
    }
}