package com.shorturl;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * 短链接服务主应用类
 * 
 * @author ShortURL Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableCaching
@EnableAsync
public class ShortUrlServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(ShortUrlServiceApplication.class, args);
    }
}