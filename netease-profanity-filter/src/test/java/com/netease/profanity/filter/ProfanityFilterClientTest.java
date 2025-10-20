package com.netease.profanity.filter;

import com.netease.profanity.filter.model.FilterResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/**
 * 网易云脏字过滤客户端测试类
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
@ExtendWith(MockitoExtension.class)
class ProfanityFilterClientTest {
    
    @Mock
    private ProfanityFilterConfig mockConfig;
    
    private ProfanityFilterClient client;
    
    @BeforeEach
    void setUp() {
        when(mockConfig.isValid()).thenReturn(true);
        when(mockConfig.getAccessKeyId()).thenReturn("test_access_key");
        when(mockConfig.getAccessKeySecret()).thenReturn("test_secret");
        when(mockConfig.getEndpoint()).thenReturn("https://test.example.com");
        when(mockConfig.getTimeout()).thenReturn(30000);
        when(mockConfig.getConnectTimeout()).thenReturn(10000);
        when(mockConfig.isDebug()).thenReturn(false);
        
        client = new ProfanityFilterClient(mockConfig);
    }
    
    @Test
    void testConstructorWithValidConfig() {
        assertNotNull(client);
    }
    
    @Test
    void testConstructorWithNullConfig() {
        assertThrows(IllegalArgumentException.class, () -> {
            new ProfanityFilterClient(null);
        });
    }
    
    @Test
    void testConstructorWithInvalidConfig() {
        when(mockConfig.isValid()).thenReturn(false);
        
        assertThrows(IllegalArgumentException.class, () -> {
            new ProfanityFilterClient(mockConfig);
        });
    }
    
    @Test
    void testFilterTextWithNullText() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterText(null);
        });
    }
    
    @Test
    void testFilterTextWithEmptyText() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterText("");
        });
    }
    
    @Test
    void testFilterImageWithNullUrl() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImage(null);
        });
    }
    
    @Test
    void testFilterImageWithEmptyUrl() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImage("");
        });
    }
    
    @Test
    void testFilterImageBase64WithNullData() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImageBase64(null, "test");
        });
    }
    
    @Test
    void testFilterImageBase64WithEmptyData() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImageBase64("", "test");
        });
    }
    
    @Test
    void testFilterImageFileWithNullPath() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImageFile(null, "test");
        });
    }
    
    @Test
    void testFilterImageFileWithEmptyPath() {
        assertThrows(IllegalArgumentException.class, () -> {
            client.filterImageFile("", "test");
        });
    }
}