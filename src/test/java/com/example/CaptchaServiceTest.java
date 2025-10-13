package com.example;

import com.example.service.CaptchaService;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 验证码服务测试类
 */
@SpringBootTest
@TestPropertySource(properties = {
    "spring.redis.host=localhost",
    "spring.redis.port=6379",
    "spring.redis.timeout=2000ms"
})
public class CaptchaServiceTest {
    
    @Test
    public void contextLoads() {
        // 测试Spring上下文是否能正常加载
        assertTrue(true);
    }
}