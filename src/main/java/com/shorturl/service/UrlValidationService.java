package com.shorturl.service;

import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * URL验证服务
 * 
 * @author ShortURL Team
 */
@Service
public class UrlValidationService {
    
    // URL正则表达式
    private static final Pattern URL_PATTERN = Pattern.compile(
        "^https?://[\\w\\-]+(\\.[\\w\\-]+)+([\\w\\-\\.,@?^=%&:/~\\+#]*[\\w\\-\\@?^=%&/~\\+#])?$"
    );
    
    // 允许的协议
    private static final Set<String> ALLOWED_PROTOCOLS = new HashSet<>(Arrays.asList("http", "https"));
    
    // 禁止的域名（恶意网站检测）
    private static final Set<String> BLOCKED_DOMAINS = new HashSet<>(Arrays.asList(
        "localhost", "127.0.0.1", "0.0.0.0", "::1"
    ));
    
    // 禁止的URL模式
    private static final Set<Pattern> BLOCKED_PATTERNS = new HashSet<>(Arrays.asList(
        Pattern.compile(".*\\.(exe|bat|cmd|com|scr|pif)$", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*javascript:.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*data:.*", Pattern.CASE_INSENSITIVE),
        Pattern.compile(".*file:.*", Pattern.CASE_INSENSITIVE)
    ));
    
    /**
     * 验证URL是否有效
     * 
     * @param urlString URL字符串
     * @return 是否有效
     */
    public boolean isValidUrl(String urlString) {
        if (!StringUtils.hasText(urlString)) {
            return false;
        }
        
        // 基本格式验证
        if (!URL_PATTERN.matcher(urlString).matches()) {
            return false;
        }
        
        try {
            URL url = new URL(urlString);
            
            // 协议验证
            if (!ALLOWED_PROTOCOLS.contains(url.getProtocol().toLowerCase())) {
                return false;
            }
            
            // 域名验证
            if (!isValidDomain(url.getHost())) {
                return false;
            }
            
            // 恶意URL检测
            if (isMaliciousUrl(urlString)) {
                return false;
            }
            
            return true;
            
        } catch (MalformedURLException e) {
            return false;
        }
    }
    
    /**
     * 验证域名是否有效
     * 
     * @param domain 域名
     * @return 是否有效
     */
    private boolean isValidDomain(String domain) {
        if (!StringUtils.hasText(domain)) {
            return false;
        }
        
        // 检查是否在禁止列表中
        if (BLOCKED_DOMAINS.contains(domain.toLowerCase())) {
            return false;
        }
        
        // 检查域名格式
        String[] parts = domain.split("\\.");
        if (parts.length < 2) {
            return false;
        }
        
        // 检查每个部分
        for (String part : parts) {
            if (part.isEmpty() || part.length() > 63) {
                return false;
            }
            
            // 检查字符是否合法
            if (!part.matches("^[a-zA-Z0-9]([a-zA-Z0-9\\-]*[a-zA-Z0-9])?$")) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 检测恶意URL
     * 
     * @param urlString URL字符串
     * @return 是否为恶意URL
     */
    private boolean isMaliciousUrl(String urlString) {
        String lowerUrl = urlString.toLowerCase();
        
        // 检查禁止的模式
        for (Pattern pattern : BLOCKED_PATTERNS) {
            if (pattern.matcher(lowerUrl).matches()) {
                return true;
            }
        }
        
        // 检查可疑的URL特征
        if (containsSuspiciousContent(lowerUrl)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * 检查是否包含可疑内容
     * 
     * @param url URL字符串
     * @return 是否包含可疑内容
     */
    private boolean containsSuspiciousContent(String url) {
        // 可疑关键词
        String[] suspiciousKeywords = {
            "phishing", "malware", "virus", "trojan", "spyware",
            "scam", "fraud", "fake", "phish", "hack"
        };
        
        for (String keyword : suspiciousKeywords) {
            if (url.contains(keyword)) {
                return true;
            }
        }
        
        // 检查URL长度（过长的URL可能有问题）
        if (url.length() > 2048) {
            return true;
        }
        
        // 检查特殊字符
        if (url.contains("..") || url.contains("//")) {
            return true;
        }
        
        return false;
    }
    
    /**
     * 标准化URL
     * 
     * @param urlString URL字符串
     * @return 标准化后的URL
     */
    public String normalizeUrl(String urlString) {
        if (!StringUtils.hasText(urlString)) {
            return urlString;
        }
        
        try {
            URL url = new URL(urlString);
            
            // 确保使用小写协议
            String protocol = url.getProtocol().toLowerCase();
            
            // 确保使用小写主机名
            String host = url.getHost().toLowerCase();
            
            // 移除默认端口
            int port = url.getPort();
            if (port == -1 || 
                (protocol.equals("http") && port == 80) ||
                (protocol.equals("https") && port == 443)) {
                port = -1;
            }
            
            // 构建标准化URL
            StringBuilder normalized = new StringBuilder();
            normalized.append(protocol).append("://").append(host);
            
            if (port != -1) {
                normalized.append(":").append(port);
            }
            
            if (url.getPath() != null) {
                normalized.append(url.getPath());
            }
            
            if (url.getQuery() != null) {
                normalized.append("?").append(url.getQuery());
            }
            
            if (url.getRef() != null) {
                normalized.append("#").append(url.getRef());
            }
            
            return normalized.toString();
            
        } catch (MalformedURLException e) {
            return urlString;
        }
    }
    
    /**
     * 获取URL的域名
     * 
     * @param urlString URL字符串
     * @return 域名
     */
    public String getDomain(String urlString) {
        try {
            URL url = new URL(urlString);
            return url.getHost().toLowerCase();
        } catch (MalformedURLException e) {
            return null;
        }
    }
    
    /**
     * 检查URL是否为HTTPS
     * 
     * @param urlString URL字符串
     * @return 是否为HTTPS
     */
    public boolean isHttps(String urlString) {
        try {
            URL url = new URL(urlString);
            return "https".equals(url.getProtocol().toLowerCase());
        } catch (MalformedURLException e) {
            return false;
        }
    }
}