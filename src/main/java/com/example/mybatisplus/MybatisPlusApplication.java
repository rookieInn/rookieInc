package com.example.mybatisplus;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * MyBatis Plus CRUD 应用启动类
 * 
 * @author Generated
 * @since 2024-01-01
 */
@SpringBootApplication
@MapperScan("com.example.mybatisplus.mapper")
public class MybatisPlusApplication {

    public static void main(String[] args) {
        SpringApplication.run(MybatisPlusApplication.class, args);
        System.out.println("=================================");
        System.out.println("MyBatis Plus CRUD 应用启动成功！");
        System.out.println("访问地址：http://localhost:8080");
        System.out.println("API文档：http://localhost:8080/api/users");
        System.out.println("H2控制台：http://localhost:8080/h2-console");
        System.out.println("=================================");
    }
}