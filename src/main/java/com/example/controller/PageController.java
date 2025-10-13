package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

/**
 * 页面控制器
 * 
 * @author example
 * @version 1.0
 */
@Controller
public class PageController {
    
    /**
     * 首页
     */
    @GetMapping("/")
    public String index() {
        return "index";
    }
    
    /**
     * 验证码演示页面
     */
    @GetMapping("/demo")
    public String demo() {
        return "demo";
    }
}