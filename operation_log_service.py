#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志服务层
提供操作日志的查询、统计和分析功能
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import asdict
import json

from operation_log_models import OperationLogDatabase, OperationLogQuery, OperationLogStats
from aop_operation_logger import OperationLog, OperationType, OperationStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OperationLogService:
    """操作日志服务类"""
    
    def __init__(self, config_file: str = 'config.ini'):
        """初始化服务"""
        self.db = OperationLogDatabase(config_file)
        logger.info("✅ 操作日志服务初始化成功")
    
    def log_operation(self, operation_log: OperationLog) -> bool:
        """记录操作日志"""
        try:
            log_data = operation_log.to_dict()
            return self.db.insert_log(log_data)
        except Exception as e:
            logger.error(f"❌ 记录操作日志失败: {e}")
            return False
    
    def get_logs(self, 
                user_id: Optional[str] = None,
                username: Optional[str] = None,
                operation_type: Optional[str] = None,
                operation_name: Optional[str] = None,
                module_name: Optional[str] = None,
                status: Optional[str] = None,
                start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                ip_address: Optional[str] = None,
                limit: int = 100,
                offset: int = 0,
                order_by: str = "timestamp",
                order_desc: bool = True) -> List[Dict[str, Any]]:
        """
        获取操作日志列表
        
        Args:
            user_id: 用户ID
            username: 用户名
            operation_type: 操作类型
            operation_name: 操作名称
            module_name: 模块名称
            status: 操作状态
            start_date: 开始日期
            end_date: 结束日期
            ip_address: IP地址
            limit: 限制数量
            offset: 偏移量
            order_by: 排序字段
            order_desc: 是否降序
        
        Returns:
            List[Dict[str, Any]]: 操作日志列表
        """
        try:
            query = OperationLogQuery(
                user_id=user_id,
                username=username,
                operation_type=operation_type,
                operation_name=operation_name,
                module_name=module_name,
                status=status,
                start_date=start_date,
                end_date=end_date,
                ip_address=ip_address,
                limit=limit,
                offset=offset,
                order_by=order_by,
                order_desc=order_desc
            )
            
            return self.db.query_logs(query)
        except Exception as e:
            logger.error(f"❌ 获取操作日志失败: {e}")
            return []
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取操作日志"""
        try:
            logs = self.get_logs(limit=1)
            for log in logs:
                if log.get('log_id') == log_id:
                    return log
            return None
        except Exception as e:
            logger.error(f"❌ 获取操作日志失败: {e}")
            return None
    
    def get_user_operation_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的操作日志"""
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_recent_logs(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的操作日志"""
        start_date = datetime.now() - timedelta(hours=hours)
        return self.get_logs(start_date=start_date, limit=limit)
    
    def get_failed_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取失败的操作日志"""
        return self.get_logs(status='failed', limit=limit)
    
    def get_operation_type_logs(self, operation_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指定操作类型的日志"""
        return self.get_logs(operation_type=operation_type, limit=limit)
    
    def get_module_logs(self, module_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取指定模块的日志"""
        return self.get_logs(module_name=module_name, limit=limit)
    
    def get_statistics(self, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取操作日志统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            stats = self.db.get_log_statistics(start_date, end_date)
            return asdict(stats)
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}
    
    def get_daily_statistics(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取每日统计信息"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stats = self.db.get_log_statistics(start_date, end_date)
            return stats.daily_stats
        except Exception as e:
            logger.error(f"❌ 获取每日统计失败: {e}")
            return []
    
    def get_user_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stats = self.db.get_log_statistics(start_date, end_date)
            return {
                'user_stats': stats.user_stats,
                'total_users': len(stats.user_stats),
                'most_active_user': max(stats.user_stats.items(), key=lambda x: x[1]) if stats.user_stats else None
            }
        except Exception as e:
            logger.error(f"❌ 获取用户统计失败: {e}")
            return {}
    
    def get_operation_type_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取操作类型统计信息"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stats = self.db.get_log_statistics(start_date, end_date)
            return {
                'operation_type_stats': stats.operation_type_stats,
                'total_types': len(stats.operation_type_stats),
                'most_common_type': max(stats.operation_type_stats.items(), key=lambda x: x[1]) if stats.operation_type_stats else None
            }
        except Exception as e:
            logger.error(f"❌ 获取操作类型统计失败: {e}")
            return {}
    
    def get_module_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取模块统计信息"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stats = self.db.get_log_statistics(start_date, end_date)
            return {
                'module_stats': stats.module_stats,
                'total_modules': len(stats.module_stats),
                'most_active_module': max(stats.module_stats.items(), key=lambda x: x[1]) if stats.module_stats else None
            }
        except Exception as e:
            logger.error(f"❌ 获取模块统计失败: {e}")
            return {}
    
    def get_performance_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取性能统计信息"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            stats = self.db.get_log_statistics(start_date, end_date)
            
            return {
                'avg_execution_time': round(stats.avg_execution_time, 2),
                'error_rate': round(stats.error_rate, 2),
                'success_rate': round(100 - stats.error_rate, 2),
                'total_operations': stats.total_logs,
                'successful_operations': stats.success_logs,
                'failed_operations': stats.failed_logs
            }
        except Exception as e:
            logger.error(f"❌ 获取性能统计失败: {e}")
            return {}
    
    def search_logs(self, 
                   keyword: str,
                   search_fields: List[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        搜索操作日志
        
        Args:
            keyword: 搜索关键词
            search_fields: 搜索字段列表
            limit: 限制数量
        
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        try:
            if not search_fields:
                search_fields = ['operation_name', 'description', 'username', 'module_name']
            
            # 获取所有日志进行搜索（这里可以优化为数据库级别的搜索）
            all_logs = self.get_logs(limit=10000)  # 获取更多日志进行搜索
            
            results = []
            keyword_lower = keyword.lower()
            
            for log in all_logs:
                for field in search_fields:
                    if field in log and log[field]:
                        field_value = str(log[field]).lower()
                        if keyword_lower in field_value:
                            results.append(log)
                            break
                
                if len(results) >= limit:
                    break
            
            return results[:limit]
        except Exception as e:
            logger.error(f"❌ 搜索操作日志失败: {e}")
            return []
    
    def get_error_analysis(self, days: int = 7) -> Dict[str, Any]:
        """获取错误分析"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            failed_logs = self.get_logs(
                status='failed',
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            # 错误类型统计
            error_types = {}
            error_messages = {}
            error_modules = {}
            
            for log in failed_logs:
                error_msg = log.get('error_message', 'Unknown error')
                
                # 错误类型统计
                error_type = self._categorize_error(error_msg)
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
                # 错误消息统计
                error_messages[error_msg] = error_messages.get(error_msg, 0) + 1
                
                # 错误模块统计
                module = log.get('module_name', 'Unknown')
                error_modules[module] = error_modules.get(module, 0) + 1
            
            return {
                'total_errors': len(failed_logs),
                'error_types': error_types,
                'common_errors': sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10],
                'error_modules': error_modules,
                'error_rate': len(failed_logs) / max(1, len(self.get_logs(start_date=start_date, end_date=end_date, limit=10000))) * 100
            }
        except Exception as e:
            logger.error(f"❌ 获取错误分析失败: {e}")
            return {}
    
    def _categorize_error(self, error_message: str) -> str:
        """错误分类"""
        error_lower = error_message.lower()
        
        if any(keyword in error_lower for keyword in ['timeout', '超时']):
            return 'Timeout'
        elif any(keyword in error_lower for keyword in ['connection', '连接']):
            return 'Connection'
        elif any(keyword in error_lower for keyword in ['permission', '权限', 'access denied']):
            return 'Permission'
        elif any(keyword in error_lower for keyword in ['not found', '未找到', '404']):
            return 'Not Found'
        elif any(keyword in error_lower for keyword in ['validation', '验证', 'invalid']):
            return 'Validation'
        elif any(keyword in error_lower for keyword in ['database', '数据库', 'sql']):
            return 'Database'
        elif any(keyword in error_lower for keyword in ['network', '网络']):
            return 'Network'
        else:
            return 'Other'
    
    def export_logs(self, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   format: str = 'json') -> str:
        """
        导出操作日志
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            format: 导出格式 (json, csv)
        
        Returns:
            str: 导出文件路径
        """
        try:
            logs = self.get_logs(start_date=start_date, end_date=end_date, limit=10000)
            
            if format == 'json':
                return self._export_json(logs, start_date, end_date)
            elif format == 'csv':
                return self._export_csv(logs, start_date, end_date)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
        except Exception as e:
            logger.error(f"❌ 导出日志失败: {e}")
            return ""
    
    def _export_json(self, logs: List[Dict[str, Any]], start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """导出为JSON格式"""
        import os
        from datetime import datetime
        
        filename = f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join("exports", filename)
        
        os.makedirs("exports", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'export_info': {
                    'export_time': datetime.now().isoformat(),
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'total_logs': len(logs)
                },
                'logs': logs
            }, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def _export_csv(self, logs: List[Dict[str, Any]], start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        """导出为CSV格式"""
        import csv
        import os
        from datetime import datetime
        
        filename = f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join("exports", filename)
        
        os.makedirs("exports", exist_ok=True)
        
        if not logs:
            return filepath
        
        # 获取所有字段
        all_fields = set()
        for log in logs:
            all_fields.update(log.keys())
        
        fieldnames = sorted(list(all_fields))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in logs:
                # 处理复杂数据类型
                csv_log = {}
                for key, value in log.items():
                    if isinstance(value, (dict, list)):
                        csv_log[key] = json.dumps(value, ensure_ascii=False)
                    else:
                        csv_log[key] = str(value) if value is not None else ''
                
                writer.writerow(csv_log)
        
        return filepath
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """清理旧日志"""
        try:
            deleted_count = self.db.delete_old_logs(days)
            logger.info(f"✅ 清理了 {deleted_count} 条旧日志")
            return deleted_count
        except Exception as e:
            logger.error(f"❌ 清理旧日志失败: {e}")
            return 0
    
    def get_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        """获取仪表板数据"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 基础统计
            stats = self.get_statistics(start_date, end_date)
            
            # 最近日志
            recent_logs = self.get_recent_logs(hours=24, limit=20)
            
            # 错误分析
            error_analysis = self.get_error_analysis(days)
            
            # 性能统计
            performance = self.get_performance_statistics(days)
            
            return {
                'summary': {
                    'total_logs': stats.get('total_logs', 0),
                    'success_logs': stats.get('success_logs', 0),
                    'failed_logs': stats.get('failed_logs', 0),
                    'error_rate': performance.get('error_rate', 0),
                    'avg_execution_time': performance.get('avg_execution_time', 0)
                },
                'recent_logs': recent_logs,
                'error_analysis': error_analysis,
                'operation_type_stats': stats.get('operation_type_stats', {}),
                'user_stats': stats.get('user_stats', {}),
                'module_stats': stats.get('module_stats', {}),
                'daily_stats': stats.get('daily_stats', [])
            }
        except Exception as e:
            logger.error(f"❌ 获取仪表板数据失败: {e}")
            return {}
    
    def close(self):
        """关闭服务"""
        try:
            self.db.close()
            logger.info("✅ 操作日志服务已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭操作日志服务失败: {e}")

# 全局服务实例
_operation_log_service = None

def get_operation_log_service() -> OperationLogService:
    """获取操作日志服务实例"""
    global _operation_log_service
    if _operation_log_service is None:
        _operation_log_service = OperationLogService()
    return _operation_log_service