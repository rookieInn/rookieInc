#!/usr/bin/env python3
"""
直播间管理系统启动脚本
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from app import app, init_db, run_scheduler
from hardware_simulator import get_hardware_simulator
import threading

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('livestream_management.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_default_rooms():
    """创建默认房间"""
    from app import Room, db
    
    with app.app_context():
        if not Room.query.first():
            logger = logging.getLogger(__name__)
            logger.info("创建默认房间...")
            
            default_rooms = [
                {'name': '直播间1'},
                {'name': '直播间2'},
                {'name': '直播间3'},
            ]
            
            for room_data in default_rooms:
                room = Room(name=room_data['name'])
                db.session.add(room)
            
            db.session.commit()
            logger.info("默认房间创建完成")

def start_hardware_simulation():
    """启动硬件模拟"""
    logger = logging.getLogger(__name__)
    logger.info("启动硬件模拟器...")
    
    simulator = get_hardware_simulator()
    
    def hardware_callback(room_id, event_type, data):
        logger.info(f"硬件事件: 房间{room_id} {event_type} - {data}")
    
    simulator.register_callback(hardware_callback)
    simulator.start_simulation()
    
    return simulator

def main():
    parser = argparse.ArgumentParser(description='直播间管理系统')
    parser.add_argument('--host', default='0.0.0.0', help='服务器地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--no-hardware', action='store_true', help='禁用硬件模拟')
    parser.add_argument('--init-db', action='store_true', help='初始化数据库')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("直播间管理系统启动")
    logger.info(f"启动时间: {datetime.now()}")
    logger.info(f"服务器地址: {args.host}:{args.port}")
    logger.info(f"调试模式: {args.debug}")
    logger.info("=" * 50)
    
    try:
        # 初始化数据库
        if args.init_db:
            logger.info("初始化数据库...")
            init_db()
            create_default_rooms()
            logger.info("数据库初始化完成")
        
        # 启动硬件模拟（如果启用）
        if not args.no_hardware:
            simulator = start_hardware_simulation()
        
        # 启动定时任务
        logger.info("启动定时任务...")
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # 启动Web服务器
        logger.info("启动Web服务器...")
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=False  # 避免在调试模式下重复启动
        )
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭系统...")
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        sys.exit(1)
    finally:
        logger.info("系统已关闭")

if __name__ == '__main__':
    main()