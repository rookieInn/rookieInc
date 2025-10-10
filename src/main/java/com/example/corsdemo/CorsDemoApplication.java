package com.example.corsdemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot 跨域处理示例应用
 * 
 * @author example
 * @version 1.0.0
 */
@SpringBootApplication
public class CorsDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(CorsDemoApplication.class, args);
        System.out.println("=================================");
        System.out.println("Spring Boot CORS Demo 启动成功！");
        System.out.println("访问地址: http://localhost:8080");
        System.out.println("API文档: http://localhost:8080/api/test");
        System.out.println("测试页面: http://localhost:8080/test.html");
        System.out.println("=================================");
    }
}