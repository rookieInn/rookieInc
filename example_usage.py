#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询结果推送到腾讯文档的使用示例
"""

from sql_to_tencent_docs import SQLToTencentDocs

def example_usage():
    """使用示例"""
    
    # 定义你的SQL查询
    sql_queries = [
        {
            "name": "用户注册统计",
            "sql": """
                SELECT 
                    DATE(created_at) as 日期,
                    COUNT(*) as 新注册用户数
                FROM users 
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at) 
                ORDER BY 日期 DESC
            """
        },
        {
            "name": "订单状态分布",
            "sql": """
                SELECT 
                    status as 订单状态,
                    COUNT(*) as 订单数量,
                    ROUND(AVG(amount), 2) as 平均金额,
                    SUM(amount) as 总金额
                FROM orders 
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY status
                ORDER BY 订单数量 DESC
            """
        },
        {
            "name": "热销商品TOP10",
            "sql": """
                SELECT 
                    p.name as 商品名称,
                    p.category as 商品分类,
                    SUM(oi.quantity) as 销售数量,
                    SUM(oi.quantity * oi.price) as 销售金额,
                    COUNT(DISTINCT oi.order_id) as 订单数
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.id, p.name, p.category
                ORDER BY 销售金额 DESC
                LIMIT 10
            """
        },
        {
            "name": "每日收入统计",
            "sql": """
                SELECT 
                    DATE(created_at) as 日期,
                    COUNT(*) as 订单数,
                    SUM(amount) as 总收入,
                    ROUND(AVG(amount), 2) as 平均订单金额
                FROM orders 
                WHERE status = 'completed'
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(created_at)
                ORDER BY 日期 DESC
            """
        }
    ]
    
    # 创建处理器实例
    processor = SQLToTencentDocs('config.ini')
    
    # 运行查询并推送到腾讯文档
    success = processor.run(
        sql_queries=sql_queries,
        sheet_name=f"业务数据汇总_{pd.Timestamp.now().strftime('%Y%m%d')}"
    )
    
    if success:
        print("✅ 数据成功推送到腾讯文档！")
    else:
        print("❌ 推送失败，请检查配置和日志")

def custom_queries_example():
    """自定义查询示例"""
    
    # 你可以根据实际业务需求修改这些查询
    custom_queries = [
        {
            "name": "用户活跃度分析",
            "sql": """
                SELECT 
                    user_id,
                    username,
                    last_login_date,
                    DATEDIFF(CURDATE(), last_login_date) as 未登录天数,
                    CASE 
                        WHEN DATEDIFF(CURDATE(), last_login_date) <= 7 THEN '活跃用户'
                        WHEN DATEDIFF(CURDATE(), last_login_date) <= 30 THEN '一般用户'
                        ELSE '流失用户'
                    END as 用户状态
                FROM users 
                ORDER BY 未登录天数 ASC
            """
        },
        {
            "name": "商品库存预警",
            "sql": """
                SELECT 
                    name as 商品名称,
                    category as 分类,
                    stock_quantity as 当前库存,
                    min_stock as 最低库存,
                    CASE 
                        WHEN stock_quantity <= min_stock THEN '需要补货'
                        WHEN stock_quantity <= min_stock * 1.5 THEN '库存偏低'
                        ELSE '库存充足'
                    END as 库存状态
                FROM products 
                WHERE stock_quantity <= min_stock * 2
                ORDER BY (stock_quantity - min_stock) ASC
            """
        }
    ]
    
    processor = SQLToTencentDocs('config.ini')
    processor.run(custom_queries, "自定义业务分析")

if __name__ == "__main__":
    # 运行示例
    example_usage()
    
    # 或者运行自定义查询
    # custom_queries_example()