package com.example.springbootapitiming.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 处理时间注解
 * 用于标记需要计算处理时间的方法
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Timing {
    /**
     * 方法描述
     */
    String value() default "";
    
    /**
     * 是否记录到日志
     */
    boolean log() default true;
}