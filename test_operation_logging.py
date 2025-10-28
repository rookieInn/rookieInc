#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOP操作日志系统测试用例
"""

import unittest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 导入被测试的模块
from aop_operation_logger import (
    OperationLog, OperationType, OperationStatus, OperationLogger,
    operation_log, log_create, log_update, log_delete, log_read,
    log_login, log_logout, log_system, log_config,
    log_operation_manually
)
from operation_log_models import OperationLogDatabase, OperationLogQuery, OperationLogStats
from operation_log_service import OperationLogService

class TestOperationLogger(unittest.TestCase):
    """操作日志记录器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.config_file.write('''
[operation_log]
enabled = true
storage_type = file
log_file = test_operation_logs.json
''')
        self.config_file.close()
        
        # 创建操作日志记录器
        self.logger = OperationLogger(self.config_file.name)
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        os.unlink(self.config_file.name)
        if os.path.exists('test_operation_logs.json'):
            os.unlink('test_operation_logs.json')
    
    def test_operation_log_creation(self):
        """测试操作日志创建"""
        log = OperationLog(
            log_id="test_001",
            user_id="user_001",
            username="test_user",
            operation_type="test",
            operation_name="测试操作",
            module_name="test_module",
            function_name="test_function",
            description="这是一个测试操作",
            request_method="POST",
            request_url="/api/test",
            request_params={"param1": "value1"},
            request_body={"data": "test"},
            response_data={"result": "success"},
            status="success",
            error_message=None,
            ip_address="127.0.0.1",
            user_agent="test_agent",
            execution_time=100.5,
            timestamp=datetime.now(),
            extra_data={"test": True}
        )
        
        # 测试转换为字典
        log_dict = log.to_dict()
        self.assertIsInstance(log_dict, dict)
        self.assertEqual(log_dict['log_id'], "test_001")
        self.assertEqual(log_dict['user_id'], "user_001")
        self.assertEqual(log_dict['operation_name'], "测试操作")
    
    def test_operation_logger_log_operation(self):
        """测试操作日志记录"""
        log = OperationLog(
            log_id="test_002",
            user_id="user_002",
            username="test_user2",
            operation_type="test",
            operation_name="测试记录",
            module_name="test_module",
            function_name="test_function",
            description="测试记录操作",
            request_method="GET",
            request_url="/api/test",
            request_params=None,
            request_body=None,
            response_data=None,
            status="success",
            error_message=None,
            ip_address="127.0.0.1",
            user_agent="test_agent",
            execution_time=50.0,
            timestamp=datetime.now(),
            extra_data=None
        )
        
        # 记录操作日志
        result = self.logger.log_operation(log)
        self.assertTrue(result)
        
        # 验证日志文件是否创建
        self.assertTrue(os.path.exists('test_operation_logs.json'))
        
        # 验证日志内容
        with open('test_operation_logs.json', 'r', encoding='utf-8') as f:
            log_data = json.loads(f.readline().strip())
            self.assertEqual(log_data['log_id'], "test_002")
            self.assertEqual(log_data['operation_name'], "测试记录")

class TestOperationLogDecorators(unittest.TestCase):
    """操作日志装饰器测试"""
    
    def test_operation_log_decorator(self):
        """测试操作日志装饰器"""
        
        @operation_log(
            operation_type=OperationType.CREATE,
            operation_name="测试创建操作",
            description="测试装饰器功能"
        )
        def test_function(param1, param2="default"):
            """测试函数"""
            return f"result: {param1}, {param2}"
        
        # 调用被装饰的函数
        result = test_function("value1", param2="value2")
        
        # 验证函数正常执行
        self.assertEqual(result, "result: value1, value2")
    
    def test_log_create_decorator(self):
        """测试创建操作装饰器"""
        
        @log_create("用户创建", "创建新用户")
        def create_user(username, email):
            return {"user_id": "001", "username": username, "email": email}
        
        result = create_user("test_user", "test@example.com")
        self.assertEqual(result["username"], "test_user")
        self.assertEqual(result["email"], "test@example.com")
    
    def test_log_update_decorator(self):
        """测试更新操作装饰器"""
        
        @log_update("用户更新", "更新用户信息")
        def update_user(user_id, **kwargs):
            return {"user_id": user_id, "updated": True, **kwargs}
        
        result = update_user("001", name="新名称", age=25)
        self.assertEqual(result["user_id"], "001")
        self.assertEqual(result["name"], "新名称")
    
    def test_log_delete_decorator(self):
        """测试删除操作装饰器"""
        
        @log_delete("用户删除", "删除用户")
        def delete_user(user_id):
            return {"deleted": True, "user_id": user_id}
        
        result = delete_user("001")
        self.assertTrue(result["deleted"])
        self.assertEqual(result["user_id"], "001")
    
    def test_log_read_decorator(self):
        """测试查询操作装饰器"""
        
        @log_read("用户查询", "查询用户信息")
        def get_user(user_id):
            return {"user_id": user_id, "username": "test_user"}
        
        result = get_user("001")
        self.assertEqual(result["user_id"], "001")
        self.assertEqual(result["username"], "test_user")
    
    def test_log_login_decorator(self):
        """测试登录操作装饰器"""
        
        @log_login("用户登录", "用户登录系统")
        def login(username, password):
            return {"success": True, "username": username}
        
        result = login("test_user", "password123")
        self.assertTrue(result["success"])
        self.assertEqual(result["username"], "test_user")
    
    def test_log_logout_decorator(self):
        """测试登出操作装饰器"""
        
        @log_logout("用户登出", "用户登出系统")
        def logout(user_id):
            return {"success": True, "user_id": user_id}
        
        result = logout("001")
        self.assertTrue(result["success"])
        self.assertEqual(result["user_id"], "001")
    
    def test_log_system_decorator(self):
        """测试系统操作装饰器"""
        
        @log_system("系统维护", "执行系统维护操作")
        def system_maintenance():
            return {"status": "completed"}
        
        result = system_maintenance()
        self.assertEqual(result["status"], "completed")
    
    def test_log_config_decorator(self):
        """测试配置操作装饰器"""
        
        @log_config("配置更新", "更新系统配置")
        def update_config(key, value):
            return {"key": key, "value": value, "updated": True}
        
        result = update_config("site_name", "新网站名称")
        self.assertEqual(result["key"], "site_name")
        self.assertEqual(result["value"], "新网站名称")
        self.assertTrue(result["updated"])

class TestOperationLogDatabase(unittest.TestCase):
    """操作日志数据库测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.config_file.write('''
[operation_log]
db_type = sqlite
db_path = test_operation_logs.db
''')
        self.config_file.close()
        
        # 创建数据库
        self.db = OperationLogDatabase(self.config_file.name)
    
    def tearDown(self):
        """测试后清理"""
        # 关闭数据库连接
        self.db.close()
        
        # 删除临时文件
        os.unlink(self.config_file.name)
        if os.path.exists('test_operation_logs.db'):
            os.unlink('test_operation_logs.db')
    
    def test_insert_log(self):
        """测试插入日志"""
        log_data = {
            'log_id': 'test_001',
            'user_id': 'user_001',
            'username': 'test_user',
            'operation_type': 'test',
            'operation_name': '测试操作',
            'module_name': 'test_module',
            'function_name': 'test_function',
            'description': '测试插入日志',
            'request_method': 'POST',
            'request_url': '/api/test',
            'request_params': json.dumps({"param1": "value1"}),
            'request_body': json.dumps({"data": "test"}),
            'response_data': json.dumps({"result": "success"}),
            'status': 'success',
            'error_message': None,
            'ip_address': '127.0.0.1',
            'user_agent': 'test_agent',
            'execution_time': 100.5,
            'timestamp': datetime.now().isoformat(),
            'extra_data': json.dumps({"test": True})
        }
        
        result = self.db.insert_log(log_data)
        self.assertTrue(result)
    
    def test_query_logs(self):
        """测试查询日志"""
        # 先插入一些测试数据
        test_logs = [
            {
                'log_id': f'test_{i:03d}',
                'user_id': f'user_{i:03d}',
                'username': f'test_user_{i}',
                'operation_type': 'test',
                'operation_name': f'测试操作_{i}',
                'module_name': 'test_module',
                'function_name': 'test_function',
                'description': f'测试操作描述_{i}',
                'request_method': 'POST',
                'request_url': '/api/test',
                'request_params': None,
                'request_body': None,
                'response_data': None,
                'status': 'success' if i % 2 == 0 else 'failed',
                'error_message': None if i % 2 == 0 else f'错误信息_{i}',
                'ip_address': '127.0.0.1',
                'user_agent': 'test_agent',
                'execution_time': 100.0 + i,
                'timestamp': datetime.now().isoformat(),
                'extra_data': None
            }
            for i in range(1, 6)
        ]
        
        # 插入测试数据
        for log_data in test_logs:
            self.db.insert_log(log_data)
        
        # 查询所有日志
        query = OperationLogQuery(limit=10)
        logs = self.db.query_logs(query)
        self.assertEqual(len(logs), 5)
        
        # 查询成功状态的日志
        query = OperationLogQuery(status='success', limit=10)
        logs = self.db.query_logs(query)
        self.assertEqual(len(logs), 3)  # 偶数索引的日志是成功状态
        
        # 查询失败状态的日志
        query = OperationLogQuery(status='failed', limit=10)
        logs = self.db.query_logs(query)
        self.assertEqual(len(logs), 2)  # 奇数索引的日志是失败状态

class TestOperationLogService(unittest.TestCase):
    """操作日志服务测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
        self.config_file.write('''
[operation_log]
db_type = sqlite
db_path = test_operation_logs_service.db
''')
        self.config_file.close()
        
        # 创建服务
        self.service = OperationLogService(self.config_file.name)
    
    def tearDown(self):
        """测试后清理"""
        # 关闭服务
        self.service.close()
        
        # 删除临时文件
        os.unlink(self.config_file.name)
        if os.path.exists('test_operation_logs_service.db'):
            os.unlink('test_operation_logs_service.db')
    
    def test_log_operation(self):
        """测试记录操作日志"""
        log = OperationLog(
            log_id="service_test_001",
            user_id="user_001",
            username="test_user",
            operation_type="test",
            operation_name="服务测试操作",
            module_name="test_module",
            function_name="test_function",
            description="测试服务记录操作",
            request_method="POST",
            request_url="/api/test",
            request_params={"param1": "value1"},
            request_body={"data": "test"},
            response_data={"result": "success"},
            status="success",
            error_message=None,
            ip_address="127.0.0.1",
            user_agent="test_agent",
            execution_time=150.0,
            timestamp=datetime.now(),
            extra_data={"test": True}
        )
        
        result = self.service.log_operation(log)
        self.assertTrue(result)
    
    def test_get_logs(self):
        """测试获取日志"""
        # 先插入一些测试数据
        for i in range(1, 6):
            log = OperationLog(
                log_id=f"service_test_{i:03d}",
                user_id=f"user_{i:03d}",
                username=f"test_user_{i}",
                operation_type="test",
                operation_name=f"服务测试操作_{i}",
                module_name="test_module",
                function_name="test_function",
                description=f"测试服务操作描述_{i}",
                request_method="POST",
                request_url="/api/test",
                request_params={"param1": f"value{i}"},
                request_body={"data": f"test{i}"},
                response_data={"result": "success"},
                status="success" if i % 2 == 0 else "failed",
                error_message=None if i % 2 == 0 else f"错误信息_{i}",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                execution_time=100.0 + i * 10,
                timestamp=datetime.now(),
                extra_data={"test": True}
            )
            self.service.log_operation(log)
        
        # 获取所有日志
        logs = self.service.get_logs(limit=10)
        self.assertEqual(len(logs), 5)
        
        # 获取成功状态的日志
        logs = self.service.get_logs(status='success', limit=10)
        self.assertEqual(len(logs), 3)
        
        # 获取失败状态的日志
        logs = self.service.get_logs(status='failed', limit=10)
        self.assertEqual(len(logs), 2)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 先插入一些测试数据
        for i in range(1, 11):
            log = OperationLog(
                log_id=f"stats_test_{i:03d}",
                user_id=f"user_{i:03d}",
                username=f"test_user_{i}",
                operation_type="test",
                operation_name=f"统计测试操作_{i}",
                module_name="test_module",
                function_name="test_function",
                description=f"统计测试操作描述_{i}",
                request_method="POST",
                request_url="/api/test",
                request_params=None,
                request_body=None,
                response_data=None,
                status="success" if i % 2 == 0 else "failed",
                error_message=None if i % 2 == 0 else f"错误信息_{i}",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                execution_time=100.0 + i * 10,
                timestamp=datetime.now(),
                extra_data=None
            )
            self.service.log_operation(log)
        
        # 获取统计信息
        stats = self.service.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_logs', stats)
        self.assertIn('success_logs', stats)
        self.assertIn('failed_logs', stats)
        self.assertEqual(stats['total_logs'], 10)
        self.assertEqual(stats['success_logs'], 5)
        self.assertEqual(stats['failed_logs'], 5)

class TestManualLogging(unittest.TestCase):
    """手动日志记录测试"""
    
    def test_log_operation_manually(self):
        """测试手动记录操作日志"""
        result = log_operation_manually(
            operation_type=OperationType.CUSTOM,
            operation_name="手动测试操作",
            description="测试手动记录操作日志",
            user_id="user_001",
            username="test_user",
            status=OperationStatus.SUCCESS,
            extra_data={"test": True}
        )
        
        self.assertTrue(result)

def run_performance_test():
    """性能测试"""
    print("开始性能测试...")
    
    # 创建临时配置文件
    config_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini')
    config_file.write('''
[operation_log]
db_type = sqlite
db_path = performance_test.db
''')
    config_file.close()
    
    try:
        # 创建服务
        service = OperationLogService(config_file.name)
        
        # 测试大量日志记录
        start_time = time.time()
        
        for i in range(1000):
            log = OperationLog(
                log_id=f"perf_test_{i:04d}",
                user_id=f"user_{i % 100:03d}",
                username=f"test_user_{i % 100}",
                operation_type="performance_test",
                operation_name=f"性能测试操作_{i}",
                module_name="test_module",
                function_name="test_function",
                description=f"性能测试操作描述_{i}",
                request_method="POST",
                request_url="/api/test",
                request_params={"param1": f"value{i}"},
                request_body={"data": f"test{i}"},
                response_data={"result": "success"},
                status="success" if i % 2 == 0 else "failed",
                error_message=None if i % 2 == 0 else f"错误信息_{i}",
                ip_address="127.0.0.1",
                user_agent="test_agent",
                execution_time=100.0 + i * 0.1,
                timestamp=datetime.now(),
                extra_data={"test": True}
            )
            service.log_operation(log)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"性能测试完成:")
        print(f"  记录日志数量: 1000")
        print(f"  总耗时: {duration:.2f} 秒")
        print(f"  平均每条日志: {duration/1000*1000:.2f} 毫秒")
        print(f"  每秒记录数: {1000/duration:.0f} 条/秒")
        
        # 测试查询性能
        start_time = time.time()
        logs = service.get_logs(limit=100)
        end_time = time.time()
        query_duration = end_time - start_time
        
        print(f"查询性能测试:")
        print(f"  查询日志数量: {len(logs)}")
        print(f"  查询耗时: {query_duration:.4f} 秒")
        
        # 测试统计性能
        start_time = time.time()
        stats = service.get_statistics()
        end_time = time.time()
        stats_duration = end_time - start_time
        
        print(f"统计性能测试:")
        print(f"  统计耗时: {stats_duration:.4f} 秒")
        print(f"  统计结果: {stats}")
        
        # 关闭服务
        service.close()
        
    finally:
        # 清理临时文件
        os.unlink(config_file.name)
        if os.path.exists('performance_test.db'):
            os.unlink('performance_test.db')

if __name__ == '__main__':
    # 运行单元测试
    print("运行单元测试...")
    unittest.main(verbosity=2, exit=False)
    
    # 运行性能测试
    print("\n" + "="*50)
    run_performance_test()