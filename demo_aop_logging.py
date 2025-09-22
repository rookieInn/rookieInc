#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOP操作日志系统演示脚本
展示如何使用AOP装饰器记录操作日志
"""

import time
import random
from datetime import datetime
from aop_operation_logger import (
    operation_log, log_create, log_update, log_delete, log_read,
    log_login, log_logout, log_system, log_config,
    OperationType, OperationStatus, log_operation_manually
)
from operation_log_service import get_operation_log_service

# 模拟用户管理类
class UserManager:
    """用户管理类 - 演示AOP操作日志记录"""
    
    def __init__(self):
        self.users = {}
        self.user_id_counter = 1
    
    @log_create("用户创建", "创建新用户")
    def create_user(self, username, email, role='user'):
        """创建用户"""
        # 模拟业务逻辑
        time.sleep(random.uniform(0.1, 0.3))  # 模拟处理时间
        
        user_id = f"user_{self.user_id_counter:03d}"
        self.user_id_counter += 1
        
        user = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'role': role,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        self.users[user_id] = user
        
        # 模拟偶尔失败
        if random.random() < 0.1:  # 10% 失败率
            raise Exception("数据库连接失败")
        
        return user
    
    @log_update("用户更新", "更新用户信息")
    def update_user(self, user_id, **kwargs):
        """更新用户"""
        time.sleep(random.uniform(0.05, 0.2))
        
        if user_id not in self.users:
            raise ValueError("用户不存在")
        
        # 更新用户信息
        for key, value in kwargs.items():
            if key in self.users[user_id]:
                self.users[user_id][key] = value
        
        self.users[user_id]['updated_at'] = datetime.now()
        
        return self.users[user_id]
    
    @log_delete("用户删除", "删除用户")
    def delete_user(self, user_id):
        """删除用户"""
        time.sleep(random.uniform(0.05, 0.15))
        
        if user_id not in self.users:
            raise ValueError("用户不存在")
        
        user = self.users.pop(user_id)
        return user
    
    @log_read("用户查询", "查询用户信息")
    def get_user(self, user_id):
        """获取用户"""
        time.sleep(random.uniform(0.01, 0.05))
        
        if user_id not in self.users:
            return None
        
        return self.users[user_id]
    
    @log_read("用户列表查询", "查询所有用户")
    def list_users(self, role=None):
        """获取用户列表"""
        time.sleep(random.uniform(0.02, 0.08))
        
        users = list(self.users.values())
        
        if role:
            users = [u for u in users if u['role'] == role]
        
        return users

# 模拟系统管理类
class SystemManager:
    """系统管理类 - 演示系统操作日志记录"""
    
    def __init__(self):
        self.config = {
            'site_name': '演示网站',
            'max_users': 1000,
            'maintenance_mode': False
        }
    
    @log_config("配置更新", "更新系统配置")
    def update_config(self, key, value):
        """更新配置"""
        time.sleep(random.uniform(0.05, 0.1))
        
        if key not in self.config:
            raise ValueError(f"配置项 {key} 不存在")
        
        old_value = self.config[key]
        self.config[key] = value
        
        return {
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'updated_at': datetime.now()
        }
    
    @log_system("系统维护", "执行系统维护")
    def system_maintenance(self):
        """系统维护"""
        time.sleep(random.uniform(1, 2))  # 模拟维护时间
        
        # 模拟维护操作
        maintenance_tasks = [
            "清理临时文件",
            "优化数据库",
            "更新缓存",
            "检查系统状态"
        ]
        
        results = []
        for task in maintenance_tasks:
            time.sleep(0.2)
            results.append(f"{task}: 完成")
        
        return {
            'maintenance_tasks': results,
            'duration': 2.0,
            'status': 'completed'
        }

# 模拟认证类
class AuthManager:
    """认证管理类 - 演示登录登出操作日志记录"""
    
    def __init__(self):
        self.sessions = {}
    
    @log_login("用户登录", "用户登录系统")
    def login(self, username, password):
        """用户登录"""
        time.sleep(random.uniform(0.1, 0.3))
        
        # 模拟认证逻辑
        if username == "admin" and password == "admin123":
            session_id = f"session_{len(self.sessions) + 1}"
            self.sessions[session_id] = {
                'username': username,
                'login_time': datetime.now(),
                'ip_address': '127.0.0.1'
            }
            return {'session_id': session_id, 'username': username}
        else:
            raise ValueError("用户名或密码错误")
    
    @log_logout("用户登出", "用户登出系统")
    def logout(self, session_id):
        """用户登出"""
        time.sleep(random.uniform(0.05, 0.1))
        
        if session_id not in self.sessions:
            raise ValueError("会话不存在")
        
        session = self.sessions.pop(session_id)
        return {'username': session['username'], 'logout_time': datetime.now()}

def demo_basic_operations():
    """演示基本操作"""
    print("=" * 60)
    print("AOP操作日志系统演示 - 基本操作")
    print("=" * 60)
    
    # 创建管理器实例
    user_manager = UserManager()
    system_manager = SystemManager()
    auth_manager = AuthManager()
    
    print("\n1. 用户管理操作演示")
    print("-" * 30)
    
    try:
        # 创建用户
        user1 = user_manager.create_user("张三", "zhangsan@example.com", "admin")
        print(f"✅ 创建用户: {user1['username']}")
        
        user2 = user_manager.create_user("李四", "lisi@example.com", "user")
        print(f"✅ 创建用户: {user2['username']}")
        
        # 更新用户
        updated_user = user_manager.update_user(user1['user_id'], role='super_admin')
        print(f"✅ 更新用户: {updated_user['username']} -> {updated_user['role']}")
        
        # 查询用户
        user_info = user_manager.get_user(user1['user_id'])
        print(f"✅ 查询用户: {user_info['username']}")
        
        # 列出用户
        users = user_manager.list_users()
        print(f"✅ 用户列表: 共 {len(users)} 个用户")
        
        # 删除用户
        deleted_user = user_manager.delete_user(user2['user_id'])
        print(f"✅ 删除用户: {deleted_user['username']}")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
    
    print("\n2. 系统管理操作演示")
    print("-" * 30)
    
    try:
        # 更新配置
        config_result = system_manager.update_config('site_name', '新网站名称')
        print(f"✅ 更新配置: {config_result['key']} = {config_result['new_value']}")
        
        # 系统维护
        maintenance_result = system_manager.system_maintenance()
        print(f"✅ 系统维护: 完成 {len(maintenance_result['maintenance_tasks'])} 个任务")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
    
    print("\n3. 认证操作演示")
    print("-" * 30)
    
    try:
        # 用户登录
        login_result = auth_manager.login("admin", "admin123")
        print(f"✅ 用户登录: {login_result['username']}")
        
        # 用户登出
        logout_result = auth_manager.logout(login_result['session_id'])
        print(f"✅ 用户登出: {logout_result['username']}")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")

def demo_manual_logging():
    """演示手动日志记录"""
    print("\n4. 手动日志记录演示")
    print("-" * 30)
    
    # 手动记录各种操作
    operations = [
        {
            'operation_type': OperationType.CUSTOM,
            'operation_name': '数据备份',
            'description': '执行数据库备份操作',
            'user_id': 'system',
            'username': 'system',
            'status': OperationStatus.SUCCESS
        },
        {
            'operation_type': OperationType.SYSTEM,
            'operation_name': '定时任务',
            'description': '执行定时清理任务',
            'user_id': 'cron',
            'username': 'cron',
            'status': OperationStatus.SUCCESS
        },
        {
            'operation_type': OperationType.CUSTOM,
            'operation_name': '异常处理',
            'description': '处理系统异常',
            'user_id': 'error_handler',
            'username': 'error_handler',
            'status': OperationStatus.FAILED,
            'error_message': '处理超时'
        }
    ]
    
    for op in operations:
        try:
            result = log_operation_manually(**op)
            status = "✅" if result else "❌"
            print(f"{status} 手动记录: {op['operation_name']}")
        except Exception as e:
            print(f"❌ 手动记录失败: {e}")

def demo_error_handling():
    """演示错误处理"""
    print("\n5. 错误处理演示")
    print("-" * 30)
    
    user_manager = UserManager()
    
    # 故意触发一些错误
    error_operations = [
        ("查询不存在的用户", lambda: user_manager.get_user("nonexistent")),
        ("更新不存在的用户", lambda: user_manager.update_user("nonexistent", name="test")),
        ("删除不存在的用户", lambda: user_manager.delete_user("nonexistent")),
    ]
    
    for desc, operation in error_operations:
        try:
            operation()
            print(f"❌ {desc}: 应该失败但没有失败")
        except Exception as e:
            print(f"✅ {desc}: 正确捕获错误 - {e}")

def demo_performance():
    """演示性能测试"""
    print("\n6. 性能测试演示")
    print("-" * 30)
    
    user_manager = UserManager()
    
    # 批量创建用户
    start_time = time.time()
    user_count = 50
    
    for i in range(user_count):
        try:
            user_manager.create_user(f"user_{i}", f"user{i}@example.com")
        except Exception:
            pass  # 忽略错误，继续测试
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ 批量创建 {user_count} 个用户")
    print(f"   总耗时: {duration:.2f} 秒")
    print(f"   平均每个: {duration/user_count*1000:.2f} 毫秒")
    print(f"   每秒处理: {user_count/duration:.0f} 个/秒")

def show_operation_logs():
    """显示操作日志"""
    print("\n7. 操作日志查看")
    print("-" * 30)
    
    try:
        service = get_operation_log_service()
        
        # 获取最近的日志
        recent_logs = service.get_recent_logs(hours=1, limit=10)
        
        if recent_logs:
            print(f"📋 最近 {len(recent_logs)} 条操作日志:")
            print("-" * 50)
            
            for i, log in enumerate(recent_logs, 1):
                status_icon = "✅" if log['status'] == 'success' else "❌"
                timestamp = log['timestamp'][:19].replace('T', ' ')
                
                print(f"{i:2d}. {status_icon} {log['operation_name']}")
                print(f"    用户: {log.get('username', '系统')} | 模块: {log.get('module_name', 'N/A')}")
                print(f"    时间: {timestamp} | 耗时: {log.get('execution_time', 0):.1f}ms")
                
                if log.get('error_message'):
                    print(f"    错误: {log['error_message']}")
                print()
        else:
            print("📋 暂无操作日志")
        
        # 获取统计信息
        stats = service.get_statistics()
        if stats:
            print(f"📊 操作统计:")
            print(f"   总操作数: {stats.get('total_logs', 0)}")
            print(f"   成功操作: {stats.get('success_logs', 0)}")
            print(f"   失败操作: {stats.get('failed_logs', 0)}")
            print(f"   错误率: {stats.get('error_rate', 0):.1f}%")
            print(f"   平均执行时间: {stats.get('avg_execution_time', 0):.1f}ms")
    
    except Exception as e:
        print(f"❌ 获取操作日志失败: {e}")

def main():
    """主函数"""
    print("🚀 AOP操作日志系统演示")
    print("=" * 60)
    print("本演示将展示如何使用AOP装饰器自动记录操作日志")
    print("所有操作都会自动记录到操作日志中")
    print("=" * 60)
    
    try:
        # 运行各种演示
        demo_basic_operations()
        demo_manual_logging()
        demo_error_handling()
        demo_performance()
        show_operation_logs()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("=" * 60)
        print("您可以查看操作日志来了解所有操作的记录情况")
        print("启动Web界面查看详细日志: python3 operation_log_web.py")
        print("启动演示系统: python3 demo_admin_system.py")
        
    except KeyboardInterrupt:
        print("\n\n用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")

if __name__ == "__main__":
    main()