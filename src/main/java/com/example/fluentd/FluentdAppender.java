package com.example.fluentd;

import org.apache.logging.log4j.core.Appender;
import org.apache.logging.log4j.core.Core;
import org.apache.logging.log4j.core.Filter;
import org.apache.logging.log4j.core.Layout;
import org.apache.logging.log4j.core.LogEvent;
import org.apache.logging.log4j.core.appender.AbstractAppender;
import org.apache.logging.log4j.core.config.plugins.Plugin;
import org.apache.logging.log4j.core.config.plugins.PluginAttribute;
import org.apache.logging.log4j.core.config.plugins.PluginElement;
import org.apache.logging.log4j.core.config.plugins.PluginFactory;
import org.fluentd.logger.FluentLogger;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;

/**
 * 自定义Fluentd Appender用于Log4j2
 * 将日志事件发送到Fluentd服务器
 */
@Plugin(name = "FluentdAppender", category = Core.CATEGORY_NAME, elementType = Appender.ELEMENT_TYPE, printObject = true)
public class FluentdAppender extends AbstractAppender {

    private FluentLogger fluentLogger;
    private String tag;
    private String host;
    private int port;
    private int timeout;
    private int bufferCapacity;

    protected FluentdAppender(String name, Filter filter, Layout<? extends Serializable> layout, 
                             boolean ignoreExceptions, String tag, String host, int port, 
                             int timeout, int bufferCapacity) {
        super(name, filter, layout, ignoreExceptions);
        this.tag = tag;
        this.host = host;
        this.port = port;
        this.timeout = timeout;
        this.bufferCapacity = bufferCapacity;
        
        // 初始化Fluentd Logger
        this.fluentLogger = FluentLogger.getLogger(tag, host, port, timeout, bufferCapacity);
    }

    @Override
    public void append(LogEvent event) {
        try {
            // 构建日志数据
            Map<String, Object> data = new HashMap<>();
            data.put("timestamp", event.getTimeMillis());
            data.put("level", event.getLevel().toString());
            data.put("logger", event.getLoggerName());
            data.put("thread", event.getThreadName());
            data.put("message", event.getMessage().getFormattedMessage());
            
            // 添加异常信息
            if (event.getThrown() != null) {
                data.put("exception", event.getThrown().getMessage());
                data.put("stackTrace", getStackTrace(event.getThrown()));
            }
            
            // 添加MDC数据
            if (event.getContextData() != null && !event.getContextData().isEmpty()) {
                Map<String, String> mdcData = new HashMap<>();
                event.getContextData().forEach((key, value) -> mdcData.put(key, String.valueOf(value)));
                data.put("mdc", mdcData);
            }
            
            // 发送到Fluentd
            fluentLogger.log(tag, data);
            
        } catch (Exception e) {
            // 如果发送失败，记录错误但不抛出异常
            System.err.println("Failed to send log to Fluentd: " + e.getMessage());
        }
    }

    @Override
    public void stop() {
        super.stop();
        if (fluentLogger != null) {
            fluentLogger.close();
        }
    }

    /**
     * 获取异常堆栈跟踪信息
     */
    private String getStackTrace(Throwable throwable) {
        java.io.StringWriter sw = new java.io.StringWriter();
        java.io.PrintWriter pw = new java.io.PrintWriter(sw);
        throwable.printStackTrace(pw);
        return sw.toString();
    }

    @PluginFactory
    public static FluentdAppender createAppender(
            @PluginAttribute("name") String name,
            @PluginElement("Filter") Filter filter,
            @PluginElement("Layout") Layout<? extends Serializable> layout,
            @PluginAttribute("ignoreExceptions") boolean ignoreExceptions,
            @PluginAttribute("tag") String tag,
            @PluginAttribute("host") String host,
            @PluginAttribute("port") int port,
            @PluginAttribute("timeout") int timeout,
            @PluginAttribute("bufferCapacity") int bufferCapacity) {
        
        // 设置默认值
        if (tag == null) {
            tag = "java.logs";
        }
        if (host == null) {
            host = "localhost";
        }
        if (port == 0) {
            port = 24224;
        }
        if (timeout == 0) {
            timeout = 3000;
        }
        if (bufferCapacity == 0) {
            bufferCapacity = 8192;
        }
        
        return new FluentdAppender(name, filter, layout, ignoreExceptions, 
                                 tag, host, port, timeout, bufferCapacity);
    }
}