#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志数据模型和数据库管理
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from configparser import ConfigParser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OperationLogQuery:
    """操作日志查询条件"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    operation_type: Optional[str] = None
    operation_name: Optional[str] = None
    module_name: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    limit: int = 100
    offset: int = 0
    order_by: str = "timestamp"
    order_desc: bool = True

@dataclass
class OperationLogStats:
    """操作日志统计信息"""
    total_logs: int
    success_logs: int
    failed_logs: int
    operation_type_stats: Dict[str, int]
    user_stats: Dict[str, int]
    daily_stats: List[Dict[str, Any]]
    module_stats: Dict[str, int]
    avg_execution_time: float
    error_rate: float

class OperationLogDatabase:
    """操作日志数据库管理类"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """初始化数据库连接"""
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 数据库配置
        self.db_type = self.config.get('operation_log', 'db_type', fallback='sqlite')
        self.db_path = self.config.get('operation_log', 'db_path', fallback='operation_logs.db')
        
        if self.db_type == 'sqlite':
            self._init_sqlite()
        elif self.db_type == 'mongodb':
            self._init_mongodb()
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
    
    def _init_sqlite(self):
        """初始化SQLite数据库"""
        try:
            # 确保目录存在
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"✅ SQLite数据库初始化成功: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ SQLite数据库初始化失败: {e}")
            raise
    
    def _init_mongodb(self):
        """初始化MongoDB数据库"""
        try:
            from pymongo import MongoClient
            from pymongo.collection import Collection
            from pymongo.database import Database
            
            host = self.config.get('operation_log', 'mongodb_host', fallback='localhost')
            port = self.config.getint('operation_log', 'mongodb_port', fallback=27017)
            database = self.config.get('operation_log', 'mongodb_database', fallback='operation_logs')
            collection = self.config.get('operation_log', 'mongodb_collection', fallback='logs')
            
            self.mongo_client = MongoClient(f"mongodb://{host}:{port}")
            self.db: Database = self.mongo_client[database]
            self.collection: Collection = self.db[collection]
            
            # 创建索引
            self._create_mongodb_indexes()
            logger.info(f"✅ MongoDB数据库初始化成功: {database}.{collection}")
        except ImportError:
            logger.error("❌ pymongo未安装，无法使用MongoDB")
            raise
        except Exception as e:
            logger.error(f"❌ MongoDB数据库初始化失败: {e}")
            raise
    
    def _create_tables(self):
        """创建SQLite表结构"""
        cursor = self.conn.cursor()
        
        # 创建操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                username TEXT,
                operation_type TEXT NOT NULL,
                operation_name TEXT NOT NULL,
                module_name TEXT NOT NULL,
                function_name TEXT NOT NULL,
                description TEXT,
                request_method TEXT,
                request_url TEXT,
                request_params TEXT,
                request_body TEXT,
                response_data TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                ip_address TEXT,
                user_agent TEXT,
                execution_time REAL,
                timestamp DATETIME NOT NULL,
                extra_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_id ON operation_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_operation_type ON operation_logs(operation_type)",
            "CREATE INDEX IF NOT EXISTS idx_status ON operation_logs(status)",
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON operation_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_module_name ON operation_logs(module_name)",
            "CREATE INDEX IF NOT EXISTS idx_operation_name ON operation_logs(operation_name)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.conn.commit()
        logger.info("✅ SQLite表结构创建成功")
    
    def _create_mongodb_indexes(self):
        """创建MongoDB索引"""
        try:
            indexes = [
                ("user_id", 1),
                ("operation_type", 1),
                ("status", 1),
                ("timestamp", -1),
                ("module_name", 1),
                ("operation_name", 1),
                ("ip_address", 1)
            ]
            
            for field, direction in indexes:
                self.collection.create_index([(field, direction)])
            
            logger.info("✅ MongoDB索引创建成功")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB索引创建失败: {e}")
    
    def insert_log(self, log_data: Dict[str, Any]) -> bool:
        """插入操作日志"""
        try:
            if self.db_type == 'sqlite':
                return self._insert_sqlite(log_data)
            else:
                return self._insert_mongodb(log_data)
        except Exception as e:
            logger.error(f"❌ 插入操作日志失败: {e}")
            return False
    
    def _insert_sqlite(self, log_data: Dict[str, Any]) -> bool:
        """插入到SQLite"""
        cursor = self.conn.cursor()
        
        # 处理JSON字段
        request_params = json.dumps(log_data.get('request_params'), ensure_ascii=False) if log_data.get('request_params') else None
        request_body = json.dumps(log_data.get('request_body'), ensure_ascii=False) if log_data.get('request_body') else None
        response_data = json.dumps(log_data.get('response_data'), ensure_ascii=False) if log_data.get('response_data') else None
        extra_data = json.dumps(log_data.get('extra_data'), ensure_ascii=False) if log_data.get('extra_data') else None
        
        cursor.execute('''
            INSERT INTO operation_logs (
                log_id, user_id, username, operation_type, operation_name,
                module_name, function_name, description, request_method,
                request_url, request_params, request_body, response_data,
                status, error_message, ip_address, user_agent,
                execution_time, timestamp, extra_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_data.get('log_id'),
            log_data.get('user_id'),
            log_data.get('username'),
            log_data.get('operation_type'),
            log_data.get('operation_name'),
            log_data.get('module_name'),
            log_data.get('function_name'),
            log_data.get('description'),
            log_data.get('request_method'),
            log_data.get('request_url'),
            request_params,
            request_body,
            response_data,
            log_data.get('status'),
            log_data.get('error_message'),
            log_data.get('ip_address'),
            log_data.get('user_agent'),
            log_data.get('execution_time'),
            log_data.get('timestamp'),
            extra_data
        ))
        
        self.conn.commit()
        return True
    
    def _insert_mongodb(self, log_data: Dict[str, Any]) -> bool:
        """插入到MongoDB"""
        result = self.collection.insert_one(log_data)
        return result.inserted_id is not None
    
    def query_logs(self, query: OperationLogQuery) -> List[Dict[str, Any]]:
        """查询操作日志"""
        try:
            if self.db_type == 'sqlite':
                return self._query_sqlite(query)
            else:
                return self._query_mongodb(query)
        except Exception as e:
            logger.error(f"❌ 查询操作日志失败: {e}")
            return []
    
    def _query_sqlite(self, query: OperationLogQuery) -> List[Dict[str, Any]]:
        """从SQLite查询"""
        cursor = self.conn.cursor()
        
        # 构建WHERE条件
        where_conditions = []
        params = []
        
        if query.user_id:
            where_conditions.append("user_id = ?")
            params.append(query.user_id)
        
        if query.username:
            where_conditions.append("username LIKE ?")
            params.append(f"%{query.username}%")
        
        if query.operation_type:
            where_conditions.append("operation_type = ?")
            params.append(query.operation_type)
        
        if query.operation_name:
            where_conditions.append("operation_name LIKE ?")
            params.append(f"%{query.operation_name}%")
        
        if query.module_name:
            where_conditions.append("module_name = ?")
            params.append(query.module_name)
        
        if query.status:
            where_conditions.append("status = ?")
            params.append(query.status)
        
        if query.ip_address:
            where_conditions.append("ip_address = ?")
            params.append(query.ip_address)
        
        if query.start_date:
            where_conditions.append("timestamp >= ?")
            params.append(query.start_date.isoformat())
        
        if query.end_date:
            where_conditions.append("timestamp <= ?")
            params.append(query.end_date.isoformat())
        
        # 构建SQL
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        order_direction = "DESC" if query.order_desc else "ASC"
        
        sql = f'''
            SELECT * FROM operation_logs 
            WHERE {where_clause}
            ORDER BY {query.order_by} {order_direction}
            LIMIT ? OFFSET ?
        '''
        
        params.extend([query.limit, query.offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # 转换为字典列表
        logs = []
        for row in rows:
            log_dict = dict(row)
            
            # 解析JSON字段
            for field in ['request_params', 'request_body', 'response_data', 'extra_data']:
                if log_dict.get(field):
                    try:
                        log_dict[field] = json.loads(log_dict[field])
                    except json.JSONDecodeError:
                        pass
            
            logs.append(log_dict)
        
        return logs
    
    def _query_mongodb(self, query: OperationLogQuery) -> List[Dict[str, Any]]:
        """从MongoDB查询"""
        # 构建查询条件
        mongo_query = {}
        
        if query.user_id:
            mongo_query['user_id'] = query.user_id
        
        if query.username:
            mongo_query['username'] = {'$regex': query.username, '$options': 'i'}
        
        if query.operation_type:
            mongo_query['operation_type'] = query.operation_type
        
        if query.operation_name:
            mongo_query['operation_name'] = {'$regex': query.operation_name, '$options': 'i'}
        
        if query.module_name:
            mongo_query['module_name'] = query.module_name
        
        if query.status:
            mongo_query['status'] = query.status
        
        if query.ip_address:
            mongo_query['ip_address'] = query.ip_address
        
        if query.start_date or query.end_date:
            mongo_query['timestamp'] = {}
            if query.start_date:
                mongo_query['timestamp']['$gte'] = query.start_date
            if query.end_date:
                mongo_query['timestamp']['$lte'] = query.end_date
        
        # 构建排序
        sort_direction = -1 if query.order_desc else 1
        sort_field = query.order_by if query.order_by != 'timestamp' else 'timestamp'
        
        # 执行查询
        cursor = self.collection.find(mongo_query).sort(sort_field, sort_direction).skip(query.offset).limit(query.limit)
        return list(cursor)
    
    def get_log_statistics(self, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None) -> OperationLogStats:
        """获取操作日志统计信息"""
        try:
            if self.db_type == 'sqlite':
                return self._get_stats_sqlite(start_date, end_date)
            else:
                return self._get_stats_mongodb(start_date, end_date)
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return OperationLogStats(0, 0, 0, {}, {}, [], {}, 0.0, 0.0)
    
    def _get_stats_sqlite(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> OperationLogStats:
        """从SQLite获取统计信息"""
        cursor = self.conn.cursor()
        
        # 基础条件
        where_conditions = []
        params = []
        
        if start_date:
            where_conditions.append("timestamp >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            where_conditions.append("timestamp <= ?")
            params.append(end_date.isoformat())
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 总日志数
        cursor.execute(f"SELECT COUNT(*) FROM operation_logs WHERE {where_clause}", params)
        total_logs = cursor.fetchone()[0]
        
        # 成功/失败日志数
        cursor.execute(f"SELECT status, COUNT(*) FROM operation_logs WHERE {where_clause} GROUP BY status", params)
        status_counts = dict(cursor.fetchall())
        success_logs = status_counts.get('success', 0)
        failed_logs = status_counts.get('failed', 0)
        
        # 操作类型统计
        cursor.execute(f"SELECT operation_type, COUNT(*) FROM operation_logs WHERE {where_clause} GROUP BY operation_type", params)
        operation_type_stats = dict(cursor.fetchall())
        
        # 用户统计
        cursor.execute(f"SELECT username, COUNT(*) FROM operation_logs WHERE {where_clause} AND username IS NOT NULL GROUP BY username ORDER BY COUNT(*) DESC LIMIT 10", params)
        user_stats = dict(cursor.fetchall())
        
        # 模块统计
        cursor.execute(f"SELECT module_name, COUNT(*) FROM operation_logs WHERE {where_clause} GROUP BY module_name ORDER BY COUNT(*) DESC", params)
        module_stats = dict(cursor.fetchall())
        
        # 平均执行时间
        cursor.execute(f"SELECT AVG(execution_time) FROM operation_logs WHERE {where_clause} AND execution_time IS NOT NULL", params)
        avg_execution_time = cursor.fetchone()[0] or 0.0
        
        # 错误率
        error_rate = (failed_logs / total_logs * 100) if total_logs > 0 else 0.0
        
        # 每日统计
        daily_stats = []
        if start_date and end_date:
            cursor.execute(f'''
                SELECT DATE(timestamp) as date, 
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM operation_logs 
                WHERE {where_clause}
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', params)
            
            for row in cursor.fetchall():
                daily_stats.append({
                    'date': row[0],
                    'total': row[1],
                    'success': row[2],
                    'failed': row[3]
                })
        
        return OperationLogStats(
            total_logs=total_logs,
            success_logs=success_logs,
            failed_logs=failed_logs,
            operation_type_stats=operation_type_stats,
            user_stats=user_stats,
            daily_stats=daily_stats,
            module_stats=module_stats,
            avg_execution_time=avg_execution_time,
            error_rate=error_rate
        )
    
    def _get_stats_mongodb(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> OperationLogStats:
        """从MongoDB获取统计信息"""
        # 构建查询条件
        query = {}
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
        
        # 总日志数
        total_logs = self.collection.count_documents(query)
        
        # 成功/失败统计
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        status_counts = {item['_id']: item['count'] for item in self.collection.aggregate(pipeline)}
        success_logs = status_counts.get('success', 0)
        failed_logs = status_counts.get('failed', 0)
        
        # 操作类型统计
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$operation_type',
                'count': {'$sum': 1}
            }}
        ]
        operation_type_stats = {item['_id']: item['count'] for item in self.collection.aggregate(pipeline)}
        
        # 用户统计
        pipeline = [
            {'$match': {**query, 'username': {'$ne': None}}},
            {'$group': {
                '_id': '$username',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]
        user_stats = {item['_id']: item['count'] for item in self.collection.aggregate(pipeline)}
        
        # 模块统计
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$module_name',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        module_stats = {item['_id']: item['count'] for item in self.collection.aggregate(pipeline)}
        
        # 平均执行时间
        pipeline = [
            {'$match': {**query, 'execution_time': {'$ne': None}}},
            {'$group': {
                '_id': None,
                'avg_time': {'$avg': '$execution_time'}
            }}
        ]
        result = list(self.collection.aggregate(pipeline))
        avg_execution_time = result[0]['avg_time'] if result else 0.0
        
        # 错误率
        error_rate = (failed_logs / total_logs * 100) if total_logs > 0 else 0.0
        
        # 每日统计
        daily_stats = []
        if start_date and end_date:
            pipeline = [
                {'$match': query},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$timestamp'},
                        'month': {'$month': '$timestamp'},
                        'day': {'$dayOfMonth': '$timestamp'}
                    },
                    'total': {'$sum': 1},
                    'success': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'success']}, 1, 0]}
                    },
                    'failed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'failed']}, 1, 0]}
                    }
                }},
                {'$sort': {'_id': 1}}
            ]
            
            for item in self.collection.aggregate(pipeline):
                date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
                daily_stats.append({
                    'date': date_str,
                    'total': item['total'],
                    'success': item['success'],
                    'failed': item['failed']
                })
        
        return OperationLogStats(
            total_logs=total_logs,
            success_logs=success_logs,
            failed_logs=failed_logs,
            operation_type_stats=operation_type_stats,
            user_stats=user_stats,
            daily_stats=daily_stats,
            module_stats=module_stats,
            avg_execution_time=avg_execution_time,
            error_rate=error_rate
        )
    
    def delete_old_logs(self, days: int = 30) -> int:
        """删除指定天数前的日志"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if self.db_type == 'sqlite':
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM operation_logs WHERE timestamp < ?", (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                self.conn.commit()
                return deleted_count
            else:
                result = self.collection.delete_many({'timestamp': {'$lt': cutoff_date}})
                return result.deleted_count
        except Exception as e:
            logger.error(f"❌ 删除旧日志失败: {e}")
            return 0
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.db_type == 'sqlite' and hasattr(self, 'conn'):
                self.conn.close()
            elif self.db_type == 'mongodb' and hasattr(self, 'mongo_client'):
                self.mongo_client.close()
            logger.info("✅ 数据库连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭数据库连接失败: {e}")

# 全局数据库实例
_operation_log_db = None

def get_operation_log_db() -> OperationLogDatabase:
    """获取操作日志数据库实例"""
    global _operation_log_db
    if _operation_log_db is None:
        _operation_log_db = OperationLogDatabase()
    return _operation_log_db