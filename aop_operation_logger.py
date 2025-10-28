#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOP操作日志记录系统
使用装饰器和切面技术记录后台管理操作
"""

import functools
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import inspect
from configparser import ConfigParser

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """操作类型枚举"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    EXPORT = "export"
    IMPORT = "import"
    CONFIG = "config"
    SYSTEM = "system"
    CUSTOM = "custom"

class OperationStatus(Enum):
    """操作状态枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

@dataclass
class OperationLog:
    """操作日志数据模型"""
    log_id: str
    user_id: Optional[str]
    username: Optional[str]
    operation_type: str
    operation_name: str
    module_name: str
    function_name: str
    description: str
    request_method: Optional[str]
    request_url: Optional[str]
    request_params: Optional[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    execution_time: float  # 执行时间（毫秒）
    timestamp: datetime
    extra_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class OperationLogger:
    """操作日志记录器"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """初始化操作日志记录器"""
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 是否启用操作日志记录
        self.enabled = self.config.getboolean('operation_log', 'enabled', fallback=True)
        
        # 日志存储配置
        self.storage_type = self.config.get('operation_log', 'storage_type', fallback='file')
        self.log_file = self.config.get('operation_log', 'log_file', fallback='logs/operation_logs.json')
        
        # 数据库配置（如果使用数据库存储）
        self.db_config = {
            'host': self.config.get('operation_log', 'db_host', fallback='localhost'),
            'port': self.config.getint('operation_log', 'db_port', fallback=27017),
            'database': self.config.get('operation_log', 'db_database', fallback='operation_logs'),
            'collection': self.config.get('operation_log', 'db_collection', fallback='logs')
        }
        
        # 初始化存储
        self._init_storage()
    
    def _init_storage(self):
        """初始化存储"""
        if self.storage_type == 'mongodb':
            try:
                from pymongo import MongoClient
                self.mongo_client = MongoClient(
                    f"mongodb://{self.db_config['host']}:{self.db_config['port']}"
                )
                self.db = self.mongo_client[self.db_config['database']]
                self.collection = self.db[self.db_config['collection']]
                logger.info("✅ MongoDB存储初始化成功")
            except ImportError:
                logger.warning("⚠️ pymongo未安装，使用文件存储")
                self.storage_type = 'file'
            except Exception as e:
                logger.error(f"❌ MongoDB连接失败: {e}，使用文件存储")
                self.storage_type = 'file'
    
    def log_operation(self, log: OperationLog) -> bool:
        """记录操作日志"""
        if not self.enabled:
            return True
        
        try:
            if self.storage_type == 'mongodb':
                return self._log_to_mongodb(log)
            else:
                return self._log_to_file(log)
        except Exception as e:
            logger.error(f"❌ 记录操作日志失败: {e}")
            return False
    
    def _log_to_mongodb(self, log: OperationLog) -> bool:
        """记录到MongoDB"""
        try:
            result = self.collection.insert_one(log.to_dict())
            logger.debug(f"✅ 操作日志已记录到MongoDB: {result.inserted_id}")
            return True
        except Exception as e:
            logger.error(f"❌ MongoDB记录失败: {e}")
            return False
    
    def _log_to_file(self, log: OperationLog) -> bool:
        """记录到文件"""
        try:
            import os
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log.to_dict(), ensure_ascii=False) + '\n')
            logger.debug(f"✅ 操作日志已记录到文件: {self.log_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 文件记录失败: {e}")
            return False
    
    def get_operation_logs(self, 
                          user_id: Optional[str] = None,
                          operation_type: Optional[str] = None,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """获取操作日志"""
        try:
            if self.storage_type == 'mongodb':
                return self._get_logs_from_mongodb(user_id, operation_type, start_date, end_date, limit)
            else:
                return self._get_logs_from_file(user_id, operation_type, start_date, end_date, limit)
        except Exception as e:
            logger.error(f"❌ 获取操作日志失败: {e}")
            return []
    
    def _get_logs_from_mongodb(self, user_id, operation_type, start_date, end_date, limit):
        """从MongoDB获取日志"""
        query = {}
        if user_id:
            query['user_id'] = user_id
        if operation_type:
            query['operation_type'] = operation_type
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
        
        cursor = self.collection.find(query).sort('timestamp', -1).limit(limit)
        return list(cursor)
    
    def _get_logs_from_file(self, user_id, operation_type, start_date, end_date, limit):
        """从文件获取日志"""
        logs = []
        try:
            if not os.path.exists(self.log_file):
                return logs
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_data = json.loads(line.strip())
                        
                        # 过滤条件
                        if user_id and log_data.get('user_id') != user_id:
                            continue
                        if operation_type and log_data.get('operation_type') != operation_type:
                            continue
                        if start_date and datetime.fromisoformat(log_data['timestamp']) < start_date:
                            continue
                        if end_date and datetime.fromisoformat(log_data['timestamp']) > end_date:
                            continue
                        
                        logs.append(log_data)
                        
                        if len(logs) >= limit:
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"❌ 读取日志文件失败: {e}")
        
        return logs

# 全局操作日志记录器实例
_operation_logger = OperationLogger()

def operation_log(operation_type: OperationType,
                 operation_name: str,
                 description: str = "",
                 module_name: str = "",
                 include_params: bool = True,
                 include_response: bool = True,
                 include_request_info: bool = True):
    """
    操作日志装饰器
    
    Args:
        operation_type: 操作类型
        operation_name: 操作名称
        description: 操作描述
        module_name: 模块名称
        include_params: 是否记录参数
        include_response: 是否记录响应
        include_request_info: 是否记录请求信息
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            log_id = str(uuid.uuid4())
            
            # 获取函数信息
            func_module = func.__module__ if not module_name else module_name
            func_name = func.__name__
            
            # 获取调用者信息
            frame = inspect.currentframe().f_back
            caller_info = {
                'filename': frame.f_code.co_filename,
                'lineno': frame.f_lineno,
                'function': frame.f_code.co_name
            }
            
            # 初始化日志对象
            log = OperationLog(
                log_id=log_id,
                user_id=None,
                username=None,
                operation_type=operation_type.value,
                operation_name=operation_name,
                module_name=func_module,
                function_name=func_name,
                description=description or f"执行{operation_name}操作",
                request_method=None,
                request_url=None,
                request_params=None,
                request_body=None,
                response_data=None,
                status=OperationStatus.SUCCESS.value,
                error_message=None,
                ip_address=None,
                user_agent=None,
                execution_time=0,
                timestamp=start_time,
                extra_data={
                    'caller_info': caller_info,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            
            # 记录参数（如果启用）
            if include_params:
                try:
                    # 获取函数签名
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    
                    # 过滤不可序列化的参数
                    serializable_args = []
                    for arg in args:
                        if isinstance(arg, (str, int, float, bool, list, dict, type(None))):
                            serializable_args.append(arg)
                        else:
                            serializable_args.append(str(type(arg).__name__))
                    
                    serializable_kwargs = {}
                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                            serializable_kwargs[key] = value
                        else:
                            serializable_kwargs[key] = str(type(value).__name__)
                    
                    log.request_params = {
                        'args': serializable_args,
                        'kwargs': serializable_kwargs,
                        'bound_args': dict(bound_args.arguments)
                    }
                except Exception as e:
                    logger.warning(f"⚠️ 记录参数失败: {e}")
            
            # 记录请求信息（如果启用且可用）
            if include_request_info:
                try:
                    from flask import request
                    log.request_method = request.method
                    log.request_url = request.url
                    log.ip_address = request.remote_addr
                    log.user_agent = request.headers.get('User-Agent')
                    
                    # 记录请求体
                    if request.is_json:
                        log.request_body = request.get_json()
                except ImportError:
                    pass  # 不在Flask环境中
                except Exception as e:
                    logger.warning(f"⚠️ 记录请求信息失败: {e}")
            
            # 执行函数
            try:
                result = func(*args, **kwargs)
                
                # 记录响应（如果启用）
                if include_response and result is not None:
                    try:
                        if isinstance(result, (dict, list, str, int, float, bool)):
                            log.response_data = {'result': result}
                        else:
                            log.response_data = {'result_type': type(result).__name__}
                    except Exception as e:
                        logger.warning(f"⚠️ 记录响应失败: {e}")
                
                log.status = OperationStatus.SUCCESS.value
                return result
                
            except Exception as e:
                log.status = OperationStatus.FAILED.value
                log.error_message = str(e)
                log.extra_data = log.extra_data or {}
                log.extra_data['traceback'] = traceback.format_exc()
                raise
                
            finally:
                # 计算执行时间
                end_time = datetime.now()
                log.execution_time = (end_time - start_time).total_seconds() * 1000
                log.timestamp = end_time
                
                # 记录日志
                _operation_logger.log_operation(log)
        
        return wrapper
    return decorator

def get_operation_logger() -> OperationLogger:
    """获取操作日志记录器实例"""
    return _operation_logger

def log_operation_manually(operation_type: OperationType,
                          operation_name: str,
                          description: str = "",
                          user_id: Optional[str] = None,
                          username: Optional[str] = None,
                          status: OperationStatus = OperationStatus.SUCCESS,
                          error_message: Optional[str] = None,
                          extra_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    手动记录操作日志
    
    Args:
        operation_type: 操作类型
        operation_name: 操作名称
        description: 操作描述
        user_id: 用户ID
        username: 用户名
        status: 操作状态
        error_message: 错误信息
        extra_data: 额外数据
    
    Returns:
        bool: 记录是否成功
    """
    log = OperationLog(
        log_id=str(uuid.uuid4()),
        user_id=user_id,
        username=username,
        operation_type=operation_type.value,
        operation_name=operation_name,
        module_name="manual",
        function_name="manual_log",
        description=description,
        request_method=None,
        request_url=None,
        request_params=None,
        request_body=None,
        response_data=None,
        status=status.value,
        error_message=error_message,
        ip_address=None,
        user_agent=None,
        execution_time=0,
        timestamp=datetime.now(),
        extra_data=extra_data
    )
    
    return _operation_logger.log_operation(log)

# 便捷的装饰器函数
def log_create(operation_name: str, description: str = ""):
    """记录创建操作的装饰器"""
    return operation_log(OperationType.CREATE, operation_name, description)

def log_update(operation_name: str, description: str = ""):
    """记录更新操作的装饰器"""
    return operation_log(OperationType.UPDATE, operation_name, description)

def log_delete(operation_name: str, description: str = ""):
    """记录删除操作的装饰器"""
    return operation_log(OperationType.DELETE, operation_name, description)

def log_read(operation_name: str, description: str = ""):
    """记录查询操作的装饰器"""
    return operation_log(OperationType.READ, operation_name, description)

def log_login(operation_name: str = "用户登录", description: str = ""):
    """记录登录操作的装饰器"""
    return operation_log(OperationType.LOGIN, operation_name, description)

def log_logout(operation_name: str = "用户登出", description: str = ""):
    """记录登出操作的装饰器"""
    return operation_log(OperationType.LOGOUT, operation_name, description)

def log_system(operation_name: str, description: str = ""):
    """记录系统操作的装饰器"""
    return operation_log(OperationType.SYSTEM, operation_name, description)

def log_config(operation_name: str, description: str = ""):
    """记录配置操作的装饰器"""
    return operation_log(OperationType.CONFIG, operation_name, description)