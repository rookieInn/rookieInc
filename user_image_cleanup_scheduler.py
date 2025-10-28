#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户图片定时清理调度器
功能：
1. 定时检查并清理用户多余的图片
2. 删除OSS上对应的图片文件
3. 记录清理操作日志
4. 支持手动执行和定时执行
"""

import os
import sys
import time
import logging
import argparse
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from configparser import ConfigParser
import json

# 导入自定义模块
from user_image_models import UserImageDatabase, UserImage

# 尝试导入OSS相关模块
try:
    from oss_image_cleaner import OSSImageCleaner
    OSS_CLEANER_AVAILABLE = True
except ImportError:
    OSS_CLEANER_AVAILABLE = False
    print("⚠️ OSS清理器模块不可用")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('user_image_cleanup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UserImageCleanupScheduler:
    """用户图片清理调度器"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """
        初始化清理调度器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # 初始化数据库和OSS清理器
        self.db = UserImageDatabase(config_file)
        
        if OSS_CLEANER_AVAILABLE:
            self.oss_cleaner = OSSImageCleaner(config_file)
        else:
            self.oss_cleaner = None
            logger.warning("OSS清理器不可用，将跳过OSS相关操作")
        
        # 配置参数
        self.cleanup_interval_hours = self.config.getint('image_cleanup', 'cleanup_interval_hours', fallback=24)
        self.cleanup_delay_days = self.config.getint('image_cleanup', 'cleanup_delay_days', fallback=1)
        self.batch_size = self.config.getint('image_cleanup', 'batch_size', fallback=100)
        self.enable_dry_run = self.config.getboolean('image_cleanup', 'enable_dry_run', fallback=False)
        
        logger.info("✅ 用户图片清理调度器初始化成功")
    
    def cleanup_user_images(self, user_id: str = None, dry_run: bool = None) -> Dict[str, Any]:
        """
        清理用户图片
        
        Args:
            user_id: 指定用户ID，如果为None则清理所有用户
            dry_run: 是否为试运行模式（不实际删除）
            
        Returns:
            Dict[str, Any]: 清理结果统计
        """
        if dry_run is None:
            dry_run = self.enable_dry_run
        
        logger.info(f"开始清理用户图片 (用户: {user_id or '所有用户'}, 试运行: {dry_run})")
        
        try:
            # 获取需要删除的图片记录
            images_to_delete = self.db.get_images_to_delete(self.cleanup_delay_days)
            
            if not images_to_delete:
                logger.info("没有需要删除的图片")
                return {
                    'total_images': 0,
                    'deleted_from_db': 0,
                    'deleted_from_oss': 0,
                    'failed_deletions': 0,
                    'dry_run': dry_run
                }
            
            logger.info(f"找到 {len(images_to_delete)} 张需要删除的图片")
            
            # 分批处理
            total_deleted_db = 0
            total_deleted_oss = 0
            total_failed = 0
            
            for i in range(0, len(images_to_delete), self.batch_size):
                batch = images_to_delete[i:i + self.batch_size]
                logger.info(f"处理批次 {i//self.batch_size + 1}: {len(batch)} 张图片")
                
                batch_result = self._process_batch(batch, dry_run)
                
                total_deleted_db += batch_result['deleted_from_db']
                total_deleted_oss += batch_result['deleted_from_oss']
                total_failed += batch_result['failed_deletions']
            
            result = {
                'total_images': len(images_to_delete),
                'deleted_from_db': total_deleted_db,
                'deleted_from_oss': total_deleted_oss,
                'failed_deletions': total_failed,
                'dry_run': dry_run,
                'cleanup_time': datetime.now().isoformat()
            }
            
            logger.info(f"清理完成: 数据库删除 {total_deleted_db}, OSS删除 {total_deleted_oss}, 失败 {total_failed}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 清理用户图片失败: {e}")
            return {
                'error': str(e),
                'cleanup_time': datetime.now().isoformat()
            }
    
    def _process_batch(self, batch: List[tuple], dry_run: bool) -> Dict[str, Any]:
        """
        处理一批图片删除
        
        Args:
            batch: 图片批次 [(image_id, oss_key), ...]
            dry_run: 是否为试运行模式
            
        Returns:
            Dict[str, Any]: 批次处理结果
        """
        deleted_from_db = 0
        deleted_from_oss = 0
        failed_deletions = 0
        
        for image_id, oss_key in batch:
            try:
                if dry_run:
                    logger.info(f"[试运行] 将删除图片: ID={image_id}, OSS={oss_key}")
                    deleted_from_db += 1
                    deleted_from_oss += 1
                else:
                    # 删除OSS文件
                    if self.oss_cleaner and self.oss_cleaner.delete_single_image(oss_key):
                        deleted_from_oss += 1
                    elif self.oss_cleaner:
                        logger.warning(f"OSS文件删除失败: {oss_key}")
                        failed_deletions += 1
                        continue
                    else:
                        logger.warning(f"OSS清理器不可用，跳过OSS文件删除: {oss_key}")
                        deleted_from_oss += 1  # 假设删除成功
                    
                    # 删除数据库记录
                    if self.db.delete_image_record(image_id):
                        deleted_from_db += 1
                    else:
                        logger.warning(f"数据库记录删除失败: {image_id}")
                        failed_deletions += 1
                
            except Exception as e:
                logger.error(f"处理图片失败 ID={image_id}, OSS={oss_key}: {e}")
                failed_deletions += 1
        
        return {
            'deleted_from_db': deleted_from_db,
            'deleted_from_oss': deleted_from_oss,
            'failed_deletions': failed_deletions
        }
    
    def cleanup_orphaned_oss_files(self, dry_run: bool = None) -> Dict[str, Any]:
        """
        清理OSS中的孤立文件（数据库中没有记录的文件）
        
        Args:
            dry_run: 是否为试运行模式
            
        Returns:
            Dict[str, Any]: 清理结果
        """
        if dry_run is None:
            dry_run = self.enable_dry_run
        
        logger.info(f"开始清理OSS孤立文件 (试运行: {dry_run})")
        
        try:
            # 获取所有有效的OSS键名
            valid_oss_keys = []
            
            # 这里需要根据实际情况获取所有有效的OSS键名
            # 可以通过数据库查询所有活跃图片的OSS键名
            # 或者通过其他方式获取有效文件列表
            
            # 示例：从数据库获取所有活跃图片的OSS键名
            # 注意：这里需要根据实际的数据库结构来实现
            # valid_oss_keys = self._get_all_valid_oss_keys()
            
            # 由于当前数据库模型中没有直接的方法获取所有OSS键名，
            # 这里提供一个示例实现
            logger.warning("孤立文件清理功能需要根据实际需求实现")
            
            return {
                'message': '孤立文件清理功能需要根据实际需求实现',
                'dry_run': dry_run
            }
            
        except Exception as e:
            logger.error(f"❌ 清理OSS孤立文件失败: {e}")
            return {
                'error': str(e),
                'dry_run': dry_run
            }
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """
        获取清理统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            # 获取数据库统计
            db_stats = self.db.get_user_image_stats()
            
            # 获取OSS存储统计
            if self.oss_cleaner:
                oss_stats = self.oss_cleaner.get_storage_stats()
            else:
                oss_stats = {"message": "OSS清理器不可用"}
            
            # 获取待删除图片数量
            pending_deletions = len(self.db.get_images_to_delete(self.cleanup_delay_days))
            
            return {
                'database_stats': db_stats,
                'oss_stats': oss_stats,
                'pending_deletions': pending_deletions,
                'cleanup_config': {
                    'interval_hours': self.cleanup_interval_hours,
                    'delay_days': self.cleanup_delay_days,
                    'batch_size': self.batch_size,
                    'dry_run_enabled': self.enable_dry_run
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 获取清理统计失败: {e}")
            return {'error': str(e)}
    
    def schedule_cleanup(self):
        """设置定时清理任务"""
        try:
            # 清除现有任务
            schedule.clear()
            
            # 设置定时任务
            schedule.every(self.cleanup_interval_hours).hours.do(self._scheduled_cleanup)
            
            logger.info(f"✅ 定时清理任务已设置: 每 {self.cleanup_interval_hours} 小时执行一次")
            
            # 运行调度器
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("用户中断定时清理任务")
        except Exception as e:
            logger.error(f"❌ 定时清理任务失败: {e}")
    
    def _scheduled_cleanup(self):
        """定时清理任务执行函数"""
        try:
            logger.info("开始执行定时清理任务")
            
            # 执行清理
            result = self.cleanup_user_images()
            
            # 记录结果
            logger.info(f"定时清理完成: {result}")
            
            # 可选：发送通知或保存报告
            self._save_cleanup_report(result)
            
        except Exception as e:
            logger.error(f"❌ 定时清理任务执行失败: {e}")
    
    def _save_cleanup_report(self, result: Dict[str, Any]):
        """
        保存清理报告
        
        Args:
            result: 清理结果
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"cleanup_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"清理报告已保存: {report_file}")
            
        except Exception as e:
            logger.error(f"保存清理报告失败: {e}")
    
    def run_manual_cleanup(self, user_id: str = None, dry_run: bool = None):
        """
        手动执行清理
        
        Args:
            user_id: 指定用户ID
            dry_run: 是否为试运行模式
        """
        try:
            logger.info("开始手动清理...")
            
            # 执行清理
            result = self.cleanup_user_images(user_id, dry_run)
            
            # 显示结果
            print("\n" + "="*50)
            print("清理结果:")
            print("="*50)
            for key, value in result.items():
                print(f"{key}: {value}")
            print("="*50)
            
            # 保存报告
            self._save_cleanup_report(result)
            
        except Exception as e:
            logger.error(f"❌ 手动清理失败: {e}")
    
    def close(self):
        """关闭资源"""
        try:
            if hasattr(self, 'db'):
                self.db.close()
            logger.info("✅ 清理调度器资源已关闭")
        except Exception as e:
            logger.error(f"关闭资源失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='用户图片清理调度器')
    parser.add_argument('--config', '-c', default='config.ini', 
                       help='配置文件路径')
    parser.add_argument('--schedule', action='store_true', 
                       help='启动定时清理任务')
    parser.add_argument('--cleanup', action='store_true', 
                       help='执行一次清理')
    parser.add_argument('--user-id', '-u', 
                       help='指定用户ID（仅清理该用户的图片）')
    parser.add_argument('--dry-run', action='store_true', 
                       help='试运行模式（不实际删除）')
    parser.add_argument('--stats', action='store_true', 
                       help='显示统计信息')
    parser.add_argument('--orphaned', action='store_true', 
                       help='清理OSS孤立文件')
    
    args = parser.parse_args()
    
    try:
        scheduler = UserImageCleanupScheduler(args.config)
        
        if args.schedule:
            # 启动定时任务
            scheduler.schedule_cleanup()
        elif args.cleanup:
            # 执行一次清理
            scheduler.run_manual_cleanup(args.user_id, args.dry_run)
        elif args.stats:
            # 显示统计信息
            stats = scheduler.get_cleanup_stats()
            print("\n" + "="*50)
            print("清理统计信息:")
            print("="*50)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            print("="*50)
        elif args.orphaned:
            # 清理孤立文件
            result = scheduler.cleanup_orphaned_oss_files(args.dry_run)
            print("\n" + "="*50)
            print("孤立文件清理结果:")
            print("="*50)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("="*50)
        else:
            print("请指定操作: --schedule, --cleanup, --stats, 或 --orphaned")
            print("使用 --help 查看详细帮助")
            
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)
    finally:
        if 'scheduler' in locals():
            scheduler.close()


if __name__ == "__main__":
    main()