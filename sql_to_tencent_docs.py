#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL查询结果汇总并推送到腾讯文档的脚本
"""

import pandas as pd
import pymysql
import requests
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import configparser
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sql_to_docs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SQLToTencentDocs:
    """SQL查询结果推送到腾讯文档的主类"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """初始化配置"""
        self.config = self._load_config(config_file)
        self.db_connection = None
        self.tencent_docs_token = self.config.get('tencent_docs', 'access_token')
        self.tencent_docs_file_id = self.config.get('tencent_docs', 'file_id')
        
    def _load_config(self, config_file: str) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file, encoding='utf-8')
        else:
            logger.warning(f"配置文件 {config_file} 不存在，将使用默认配置")
        return config
    
    def connect_database(self) -> bool:
        """连接数据库"""
        try:
            self.db_connection = pymysql.connect(
                host=self.config.get('database', 'host', fallback='localhost'),
                port=int(self.config.get('database', 'port', fallback=3306)),
                user=self.config.get('database', 'user', fallback='root'),
                password=self.config.get('database', 'password', fallback=''),
                database=self.config.get('database', 'database', fallback='test'),
                charset='utf8mb4'
            )
            logger.info("数据库连接成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def execute_sql_queries(self, sql_queries: List[Dict[str, str]]) -> List[pd.DataFrame]:
        """执行多条SQL查询"""
        results = []
        
        if not self.db_connection:
            logger.error("数据库未连接")
            return results
        
        try:
            cursor = self.db_connection.cursor()
            
            for i, query_info in enumerate(sql_queries):
                query_name = query_info.get('name', f'Query_{i+1}')
                sql = query_info.get('sql', '')
                
                if not sql:
                    logger.warning(f"查询 {query_name} 的SQL为空，跳过")
                    continue
                
                logger.info(f"执行查询: {query_name}")
                cursor.execute(sql)
                
                # 获取列名
                columns = [desc[0] for desc in cursor.description]
                
                # 获取数据
                data = cursor.fetchall()
                
                # 创建DataFrame
                df = pd.DataFrame(data, columns=columns)
                df['查询名称'] = query_name  # 添加查询标识列
                
                results.append(df)
                logger.info(f"查询 {query_name} 完成，返回 {len(df)} 行数据")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"执行SQL查询时出错: {e}")
        
        return results
    
    def merge_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """合并多个DataFrame"""
        if not dataframes:
            logger.warning("没有数据需要合并")
            return pd.DataFrame()
        
        # 使用concat合并所有DataFrame
        merged_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"合并完成，总共 {len(merged_df)} 行数据")
        
        return merged_df
    
    def format_data_for_tencent_docs(self, df: pd.DataFrame) -> List[List[str]]:
        """将DataFrame格式化为腾讯文档表格格式"""
        if df.empty:
            return []
        
        # 转换所有数据为字符串
        df_str = df.astype(str)
        
        # 创建表格数据
        table_data = []
        
        # 添加表头
        headers = list(df_str.columns)
        table_data.append(headers)
        
        # 添加数据行
        for _, row in df_str.iterrows():
            table_data.append(list(row))
        
        return table_data
    
    def send_to_tencent_docs(self, table_data: List[List[str]], sheet_name: str = "SQL查询结果") -> bool:
        """发送数据到腾讯文档"""
        if not table_data:
            logger.warning("没有数据需要发送")
            return False
        
        try:
            # 腾讯文档API URL
            url = f"https://docs.qq.com/openapi/drive/v3/files/{self.tencent_docs_file_id}/sheets"
            
            headers = {
                'Authorization': f'Bearer {self.tencent_docs_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备数据
            payload = {
                "requests": [
                    {
                        "createSheet": {
                            "properties": {
                                "title": sheet_name
                            }
                        }
                    }
                ]
            }
            
            # 创建表格
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info("表格创建成功")
                
                # 获取新创建的表格ID
                sheet_id = response.json().get('replies', [{}])[0].get('createSheet', {}).get('properties', {}).get('sheetId')
                
                if sheet_id:
                    # 写入数据
                    self._write_data_to_sheet(sheet_id, table_data)
                    return True
                else:
                    logger.error("无法获取表格ID")
                    return False
            else:
                logger.error(f"创建表格失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"发送到腾讯文档时出错: {e}")
            return False
    
    def _write_data_to_sheet(self, sheet_id: str, table_data: List[List[str]]) -> bool:
        """向表格写入数据"""
        try:
            url = f"https://docs.qq.com/openapi/drive/v3/files/{self.tencent_docs_file_id}/sheets/{sheet_id}/values"
            
            headers = {
                'Authorization': f'Bearer {self.tencent_docs_token}',
                'Content-Type': 'application/json'
            }
            
            # 准备数据范围
            end_row = len(table_data)
            end_col = len(table_data[0]) if table_data else 0
            
            range_name = f"A1:{chr(64 + end_col)}{end_row}"
            
            payload = {
                "values": table_data,
                "range": range_name
            }
            
            response = requests.put(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"数据写入成功，范围: {range_name}")
                return True
            else:
                logger.error(f"数据写入失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"写入数据时出错: {e}")
            return False
    
    def close_database(self):
        """关闭数据库连接"""
        if self.db_connection:
            self.db_connection.close()
            logger.info("数据库连接已关闭")
    
    def run(self, sql_queries: List[Dict[str, str]], sheet_name: str = None):
        """运行主流程"""
        if not sheet_name:
            sheet_name = f"SQL查询结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info("开始执行SQL查询并推送到腾讯文档")
        
        # 连接数据库
        if not self.connect_database():
            return False
        
        try:
            # 执行SQL查询
            results = self.execute_sql_queries(sql_queries)
            
            if not results:
                logger.warning("没有查询结果")
                return False
            
            # 合并数据
            merged_df = self.merge_dataframes(results)
            
            # 格式化为腾讯文档格式
            table_data = self.format_data_for_tencent_docs(merged_df)
            
            # 发送到腾讯文档
            success = self.send_to_tencent_docs(table_data, sheet_name)
            
            if success:
                logger.info("数据成功推送到腾讯文档")
            else:
                logger.error("推送数据到腾讯文档失败")
            
            return success
            
        finally:
            self.close_database()


def main():
    """主函数"""
    # 示例SQL查询配置
    sql_queries = [
        {
            "name": "用户统计",
            "sql": "SELECT COUNT(*) as 用户总数, DATE(created_at) as 日期 FROM users GROUP BY DATE(created_at) ORDER BY 日期 DESC LIMIT 10"
        },
        {
            "name": "订单统计", 
            "sql": "SELECT status as 订单状态, COUNT(*) as 数量, SUM(amount) as 总金额 FROM orders GROUP BY status"
        },
        {
            "name": "产品销售排行",
            "sql": "SELECT product_name as 产品名称, SUM(quantity) as 销售数量, SUM(amount) as 销售金额 FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY product_name ORDER BY 销售金额 DESC LIMIT 10"
        }
    ]
    
    # 创建实例并运行
    processor = SQLToTencentDocs()
    success = processor.run(sql_queries, "每日数据汇总")
    
    if success:
        print("✅ 数据成功推送到腾讯文档")
    else:
        print("❌ 推送失败，请检查日志")


if __name__ == "__main__":
    main()