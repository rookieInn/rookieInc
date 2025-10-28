#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AOP操作日志系统启动脚本
一键启动所有相关服务
"""

import os
import sys
import time
import subprocess
import threading
import signal
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OperationLoggingSystem:
    """AOP操作日志系统管理器"""
    
    def __init__(self):
        """初始化系统管理器"""
        self.processes = {}
        self.running = False
        
        # 服务配置
        self.services = {
            'operation_log_web': {
                'script': 'operation_log_web.py',
                'port': 5001,
                'description': '操作日志Web管理界面'
            },
            'demo_admin': {
                'script': 'demo_admin_system.py',
                'port': 5002,
                'description': '演示后台管理系统'
            },
            'enhanced_api': {
                'script': 'enhanced_tracking_api.py',
                'port': 5000,
                'description': '增强的API服务'
            }
        }
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            'data',
            'logs',
            'exports',
            'templates'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ 创建目录: {directory}")
    
    def start_service(self, service_name):
        """启动单个服务"""
        if service_name not in self.services:
            logger.error(f"❌ 未知服务: {service_name}")
            return False
        
        service_config = self.services[service_name]
        script_path = service_config['script']
        
        if not os.path.exists(script_path):
            logger.error(f"❌ 脚本文件不存在: {script_path}")
            return False
        
        try:
            # 启动服务进程
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = process
            logger.info(f"🚀 启动服务: {service_config['description']} (PID: {process.pid})")
            
            # 等待服务启动
            time.sleep(2)
            
            # 检查服务是否正常运行
            if process.poll() is None:
                logger.info(f"✅ 服务启动成功: {service_name}")
                return True
            else:
                logger.error(f"❌ 服务启动失败: {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 启动服务失败: {service_name}, 错误: {e}")
            return False
    
    def stop_service(self, service_name):
        """停止单个服务"""
        if service_name not in self.processes:
            logger.warning(f"⚠️ 服务未运行: {service_name}")
            return
        
        process = self.processes[service_name]
        
        try:
            # 发送终止信号
            process.terminate()
            
            # 等待进程结束
            process.wait(timeout=5)
            
            logger.info(f"🛑 服务已停止: {service_name}")
            
        except subprocess.TimeoutExpired:
            # 强制杀死进程
            process.kill()
            logger.warning(f"⚠️ 强制停止服务: {service_name}")
            
        except Exception as e:
            logger.error(f"❌ 停止服务失败: {service_name}, 错误: {e}")
        
        finally:
            # 从进程列表中移除
            if service_name in self.processes:
                del self.processes[service_name]
    
    def start_all_services(self):
        """启动所有服务"""
        logger.info("🚀 开始启动AOP操作日志系统...")
        
        success_count = 0
        total_count = len(self.services)
        
        for service_name in self.services:
            if self.start_service(service_name):
                success_count += 1
        
        if success_count == total_count:
            logger.info(f"✅ 所有服务启动成功 ({success_count}/{total_count})")
            self.running = True
            return True
        else:
            logger.error(f"❌ 部分服务启动失败 ({success_count}/{total_count})")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        logger.info("🛑 开始停止所有服务...")
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        self.running = False
        logger.info("✅ 所有服务已停止")
    
    def restart_service(self, service_name):
        """重启单个服务"""
        logger.info(f"🔄 重启服务: {service_name}")
        self.stop_service(service_name)
        time.sleep(1)
        return self.start_service(service_name)
    
    def restart_all_services(self):
        """重启所有服务"""
        logger.info("🔄 重启所有服务...")
        self.stop_all_services()
        time.sleep(2)
        return self.start_all_services()
    
    def get_service_status(self):
        """获取服务状态"""
        status = {}
        
        for service_name, process in self.processes.items():
            if process.poll() is None:
                status[service_name] = "运行中"
            else:
                status[service_name] = "已停止"
        
        return status
    
    def show_service_info(self):
        """显示服务信息"""
        print("\n" + "="*60)
        print("AOP操作日志系统服务信息")
        print("="*60)
        
        for service_name, config in self.services.items():
            status = "运行中" if service_name in self.processes and self.processes[service_name].poll() is None else "已停止"
            print(f"📊 {config['description']}")
            print(f"   脚本: {config['script']}")
            print(f"   端口: {config['port']}")
            print(f"   状态: {status}")
            print(f"   访问: http://localhost:{config['port']}")
            print()
    
    def monitor_services(self):
        """监控服务状态"""
        while self.running:
            try:
                # 检查所有服务状态
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"⚠️ 服务异常退出: {service_name}")
                        # 可以选择自动重启
                        # self.restart_service(service_name)
                
                time.sleep(5)  # 每5秒检查一次
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ 监控服务时出错: {e}")
                time.sleep(5)
    
    def run_interactive_mode(self):
        """运行交互模式"""
        print("\n" + "="*60)
        print("AOP操作日志系统管理控制台")
        print("="*60)
        print("可用命令:")
        print("  start [service]  - 启动服务 (不指定服务名则启动所有)")
        print("  stop [service]   - 停止服务 (不指定服务名则停止所有)")
        print("  restart [service]- 重启服务 (不指定服务名则重启所有)")
        print("  status          - 查看服务状态")
        print("  info            - 显示服务信息")
        print("  monitor         - 启动监控模式")
        print("  quit            - 退出")
        print("="*60)
        
        while True:
            try:
                command = input("\n请输入命令: ").strip().split()
                
                if not command:
                    continue
                
                cmd = command[0].lower()
                service = command[1] if len(command) > 1 else None
                
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd == 'start':
                    if service:
                        self.start_service(service)
                    else:
                        self.start_all_services()
                elif cmd == 'stop':
                    if service:
                        self.stop_service(service)
                    else:
                        self.stop_all_services()
                elif cmd == 'restart':
                    if service:
                        self.restart_service(service)
                    else:
                        self.restart_all_services()
                elif cmd == 'status':
                    status = self.get_service_status()
                    print("\n服务状态:")
                    for name, state in status.items():
                        print(f"  {name}: {state}")
                elif cmd == 'info':
                    self.show_service_info()
                elif cmd == 'monitor':
                    print("启动监控模式... (按Ctrl+C退出)")
                    try:
                        self.monitor_services()
                    except KeyboardInterrupt:
                        print("监控模式已退出")
                else:
                    print("未知命令，请重新输入")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ 执行命令时出错: {e}")
        
        # 退出时停止所有服务
        self.stop_all_services()

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到退出信号，正在停止所有服务...")
    sys.exit(0)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AOP操作日志系统启动脚本')
    parser.add_argument('--mode', choices=['auto', 'interactive'], default='auto',
                       help='运行模式: auto(自动启动) 或 interactive(交互模式)')
    parser.add_argument('--service', choices=['operation_log_web', 'demo_admin', 'enhanced_api'],
                       help='指定要启动的服务')
    parser.add_argument('--no-monitor', action='store_true',
                       help='不启动监控模式')
    
    args = parser.parse_args()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建系统管理器
    system = OperationLoggingSystem()
    
    try:
        if args.mode == 'interactive':
            # 交互模式
            system.run_interactive_mode()
        else:
            # 自动模式
            if args.service:
                # 启动指定服务
                if system.start_service(args.service):
                    system.show_service_info()
                    if not args.no_monitor:
                        print("服务已启动，按Ctrl+C停止...")
                        try:
                            system.monitor_services()
                        except KeyboardInterrupt:
                            pass
                else:
                    logger.error("服务启动失败")
                    sys.exit(1)
            else:
                # 启动所有服务
                if system.start_all_services():
                    system.show_service_info()
                    print("\n所有服务已启动！")
                    print("按Ctrl+C停止所有服务...")
                    
                    if not args.no_monitor:
                        try:
                            system.monitor_services()
                        except KeyboardInterrupt:
                            pass
                else:
                    logger.error("部分服务启动失败")
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        logger.error(f"❌ 系统运行出错: {e}")
        sys.exit(1)
    finally:
        # 清理资源
        system.stop_all_services()
        print("系统已停止")

if __name__ == "__main__":
    main()