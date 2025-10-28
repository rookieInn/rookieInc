package com.shorturl.algorithm;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * 短码生成器测试
 * 
 * @author ShortURL Team
 */
class ShortCodeGeneratorTest {
    
    private ShortCodeGenerator generator;
    
    @BeforeEach
    void setUp() {
        generator = new ShortCodeGenerator();
    }
    
    @Test
    @DisplayName("测试短码生成")
    void testGenerateShortCode() {
        String shortCode = generator.generateShortCode();
        
        assertNotNull(shortCode);
        assertFalse(shortCode.isEmpty());
        assertTrue(shortCode.length() >= 4);
        assertTrue(shortCode.length() <= 8);
    }
    
    @Test
    @DisplayName("测试批量生成短码")
    void testGenerateShortCodes() {
        String[] codes = generator.generateShortCodes(10);
        
        assertEquals(10, codes.length);
        
        for (String code : codes) {
            assertNotNull(code);
            assertFalse(code.isEmpty());
            assertTrue(generator.isValidShortCode(code));
        }
    }
    
    @Test
    @DisplayName("测试短码解码")
    void testDecodeShortCode() {
        String shortCode = generator.generateShortCode();
        long decodedId = generator.decodeShortCode(shortCode);
        
        assertTrue(decodedId > 0);
    }
    
    @Test
    @DisplayName("测试短码验证")
    void testIsValidShortCode() {
        // 有效短码
        assertTrue(generator.isValidShortCode("abc123"));
        assertTrue(generator.isValidShortCode("ABC123"));
        assertTrue(generator.isValidShortCode("123abc"));
        
        // 无效短码
        assertFalse(generator.isValidShortCode(null));
        assertFalse(generator.isValidShortCode(""));
        assertFalse(generator.isValidShortCode("abc")); // 太短
        assertFalse(generator.isValidShortCode("abcdefghij")); // 太长
        assertFalse(generator.isValidShortCode("abc@123")); // 包含非法字符
    }
    
    @Test
    @DisplayName("测试编码解码一致性")
    void testEncodeDecodeConsistency() {
        for (int i = 0; i < 1000; i++) {
            String shortCode = generator.generateShortCode();
            long decodedId = generator.decodeShortCode(shortCode);
            
            // 重新编码应该得到相同结果
            String reencoded = generator.generateShortCode();
            assertNotNull(reencoded);
        }
    }
    
    @Test
    @DisplayName("测试短码唯一性")
    void testShortCodeUniqueness() {
        String[] codes = generator.generateShortCodes(1000);
        
        // 检查唯一性
        for (int i = 0; i < codes.length; i++) {
            for (int j = i + 1; j < codes.length; j++) {
                assertNotEquals(codes[i], codes[j], 
                    "Duplicate short codes found: " + codes[i]);
            }
        }
    }
    
    @Test
    @DisplayName("测试异常情况")
    void testExceptionCases() {
        // 测试空字符串解码
        assertThrows(IllegalArgumentException.class, () -> {
            generator.decodeShortCode("");
        });
        
        // 测试null解码
        assertThrows(IllegalArgumentException.class, () -> {
            generator.decodeShortCode(null);
        });
        
        // 测试非法字符解码
        assertThrows(IllegalArgumentException.class, () -> {
            generator.decodeShortCode("abc@123");
        });
    }
}