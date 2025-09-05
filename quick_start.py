#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动脚本 - 修改配置后直接运行
"""

import pandas as pd
from sql_to_tencent_docs import SQLToTencentDocs

def main():
    """快速启动主函数"""
    
    print("🚀 SQL查询结果推送到腾讯文档 - 快速启动")
    print("=" * 50)
    
    # 在这里修改你的SQL查询
    sql_queries = [
        {
            "name": "示例查询1",
            "sql": "SELECT 'Hello' as 消息, 'World' as 内容, NOW() as 时间"
        },
        {
            "name": "示例查询2", 
            "sql": "SELECT 1 as 数字, '测试' as 文本, 3.14 as 小数"
        }
    ]
    
    # 检查配置文件是否存在
    import os
    if not os.path.exists('config.ini'):
        print("❌ 配置文件 config.ini 不存在！")
        print("请先配置数据库和腾讯文档信息")
        return
    
    try:
        # 创建处理器
        processor = SQLToTencentDocs('config.ini')
        
        # 运行查询
        print("📊 开始执行SQL查询...")
        success = processor.run(
            sql_queries=sql_queries,
            sheet_name=f"测试数据_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if success:
            print("✅ 数据成功推送到腾讯文档！")
            print("📋 请检查你的腾讯文档文件")
        else:
            print("❌ 推送失败，请检查配置和日志文件")
            
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        print("请检查配置文件和依赖是否正确安装")

if __name__ == "__main__":
    main()