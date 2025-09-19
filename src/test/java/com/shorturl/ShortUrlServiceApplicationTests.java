package com.shorturl;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class ShortUrlServiceApplicationTests {

    @Test
    void contextLoads() {
        // 测试Spring上下文是否能正常加载
    }
}