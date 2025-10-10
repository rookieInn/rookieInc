package com.example.springbootapitiming;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot 主应用程序类
 * 用于计算后端接口处理时间
 */
@SpringBootApplication
public class SpringBootApiTimingApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringBootApiTimingApplication.class, args);
    }
}