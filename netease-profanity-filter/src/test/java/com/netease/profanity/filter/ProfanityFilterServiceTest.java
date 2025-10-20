package com.netease.profanity.filter;

import com.netease.profanity.filter.model.FilterResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.io.IOException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/**
 * 网易云脏字过滤服务测试类
 * 
 * @author NetEase Cloud
 * @version 1.0.0
 */
@ExtendWith(MockitoExtension.class)
class ProfanityFilterServiceTest {
    
    @Mock
    private ProfanityFilterClient mockClient;
    
    @Mock
    private ProfanityFilterConfig mockConfig;
    
    private ProfanityFilterService service;
    
    @BeforeEach
    void setUp() {
        when(mockConfig.isValid()).thenReturn(true);
        when(mockConfig.getAccessKeyId()).thenReturn("test_access_key");
        when(mockConfig.getAccessKeySecret()).thenReturn("test_secret");
        when(mockConfig.getEndpoint()).thenReturn("https://test.example.com");
        when(mockConfig.getTimeout()).thenReturn(30000);
        when(mockConfig.getConnectTimeout()).thenReturn(10000);
        when(mockConfig.isDebug()).thenReturn(false);
        
        service = new ProfanityFilterService(mockClient);
    }
    
    @Test
    void testFilterTextAsync() throws ExecutionException, InterruptedException {
        // 准备测试数据
        String testText = "测试文本";
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(0);
        mockResponse.setMessage("成功");
        
        when(mockClient.filterText(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        CompletableFuture<FilterResponse> future = service.filterTextAsync(testText, "test_business");
        FilterResponse result = future.get();
        
        // 验证结果
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals(0, result.getAction());
        assertTrue(result.isPass());
        
        verify(mockClient, times(1)).filterText(testText, "test_business");
    }
    
    @Test
    void testFilterImageAsync() throws ExecutionException, InterruptedException {
        // 准备测试数据
        String testImageUrl = "https://example.com/test.jpg";
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(1);
        mockResponse.setMessage("检测到敏感内容");
        
        when(mockClient.filterImage(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        CompletableFuture<FilterResponse> future = service.filterImageAsync(testImageUrl, "test_business");
        FilterResponse result = future.get();
        
        // 验证结果
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals(1, result.getAction());
        assertTrue(result.isReject());
        
        verify(mockClient, times(1)).filterImage(testImageUrl, "test_business");
    }
    
    @Test
    void testFilterTextsAsync() throws ExecutionException, InterruptedException {
        // 准备测试数据
        String[] testTexts = {"文本1", "文本2", "文本3"};
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(0);
        mockResponse.setMessage("成功");
        
        when(mockClient.filterText(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        CompletableFuture<FilterResponse[]> future = service.filterTextsAsync(testTexts, "batch_test");
        FilterResponse[] results = future.get();
        
        // 验证结果
        assertNotNull(results);
        assertEquals(3, results.length);
        
        for (FilterResponse result : results) {
            assertNotNull(result);
            assertEquals(200, result.getCode());
            assertTrue(result.isPass());
        }
        
        verify(mockClient, times(3)).filterText(anyString(), anyString());
    }
    
    @Test
    void testFilterImagesAsync() throws ExecutionException, InterruptedException {
        // 准备测试数据
        String[] testImageUrls = {
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        };
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(0);
        mockResponse.setMessage("成功");
        
        when(mockClient.filterImage(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        CompletableFuture<FilterResponse[]> future = service.filterImagesAsync(testImageUrls, "batch_image_test");
        FilterResponse[] results = future.get();
        
        // 验证结果
        assertNotNull(results);
        assertEquals(3, results.length);
        
        for (FilterResponse result : results) {
            assertNotNull(result);
            assertEquals(200, result.getCode());
            assertTrue(result.isPass());
        }
        
        verify(mockClient, times(3)).filterImage(anyString(), anyString());
    }
    
    @Test
    void testSyncFilterText() throws IOException {
        // 准备测试数据
        String testText = "同步测试文本";
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(0);
        mockResponse.setMessage("成功");
        
        when(mockClient.filterText(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        FilterResponse result = service.filterText(testText, "sync_test");
        
        // 验证结果
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertTrue(result.isPass());
        
        verify(mockClient, times(1)).filterText(testText, "sync_test");
    }
    
    @Test
    void testSyncFilterImage() throws IOException {
        // 准备测试数据
        String testImageUrl = "https://example.com/sync_test.jpg";
        FilterResponse mockResponse = new FilterResponse();
        mockResponse.setCode(200);
        mockResponse.setAction(1);
        mockResponse.setMessage("检测到敏感内容");
        
        when(mockClient.filterImage(anyString(), anyString())).thenReturn(mockResponse);
        
        // 执行测试
        FilterResponse result = service.filterImage(testImageUrl, "sync_image_test");
        
        // 验证结果
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertTrue(result.isReject());
        
        verify(mockClient, times(1)).filterImage(testImageUrl, "sync_image_test");
    }
}