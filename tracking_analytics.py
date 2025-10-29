#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
埋点数据分析和统计功能
提供各种数据分析和可视化功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import json
import logging
from tracking_models import TrackingDatabase

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackingAnalytics:
    """埋点数据分析类"""
    
    def __init__(self, db: TrackingDatabase):
        """
        初始化分析器
        
        Args:
            db: 数据库连接实例
        """
        self.db = db
    
    def get_user_behavior_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取用户行为摘要
        
        Args:
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 用户行为摘要
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取事件统计
            event_stats = self.db.get_event_statistics(start_date, end_date)
            
            # 获取页面统计
            page_stats = self.db.get_page_statistics(start_date, end_date)
            
            # 计算用户活跃度
            active_users = self._get_active_users(start_date, end_date)
            
            # 计算会话统计
            session_stats = self._get_session_statistics(start_date, end_date)
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'overview': {
                    'total_events': event_stats.get('total_events', 0),
                    'total_page_views': sum(p['views'] for p in page_stats.get('pages', [])),
                    'active_users': active_users['unique_users'],
                    'total_sessions': session_stats['total_sessions']
                },
                'event_types': event_stats.get('event_types', []),
                'top_pages': page_stats.get('pages', [])[:10],
                'user_activity': active_users,
                'session_metrics': session_stats
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户行为摘要失败: {e}")
            return {}
    
    def _get_active_users(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取活跃用户统计"""
        try:
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date,
                            "$lte": end_date
                        },
                        "user_id": {"$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "event_count": {"$sum": 1},
                        "last_activity": {"$max": "$timestamp"},
                        "sessions": {"$addToSet": "$session_id"}
                    }
                },
                {
                    "$project": {
                        "user_id": "$_id",
                        "event_count": 1,
                        "last_activity": 1,
                        "session_count": {"$size": "$sessions"}
                    }
                }
            ]
            
            users = list(self.db.events_collection.aggregate(pipeline))
            
            return {
                'unique_users': len(users),
                'users': users,
                'avg_events_per_user': sum(u['event_count'] for u in users) / len(users) if users else 0
            }
            
        except Exception as e:
            logger.error(f"❌ 获取活跃用户统计失败: {e}")
            return {'unique_users': 0, 'users': [], 'avg_events_per_user': 0}
    
    def _get_session_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """获取会话统计"""
        try:
            pipeline = [
                {
                    "$match": {
                        "timestamp": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$session_id",
                        "user_id": {"$first": "$user_id"},
                        "start_time": {"$min": "$timestamp"},
                        "end_time": {"$max": "$timestamp"},
                        "event_count": {"$sum": 1},
                        "page_views": {
                            "$sum": {
                                "$cond": [{"$eq": ["$event_type", "page_view"]}, 1, 0]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "session_id": "$_id",
                        "user_id": 1,
                        "start_time": 1,
                        "end_time": 1,
                        "event_count": 1,
                        "page_views": 1,
                        "duration_minutes": {
                            "$divide": [
                                {"$subtract": ["$end_time", "$start_time"]},
                                60000
                            ]
                        }
                    }
                }
            ]
            
            sessions = list(self.db.events_collection.aggregate(pipeline))
            
            if not sessions:
                return {
                    'total_sessions': 0,
                    'avg_duration_minutes': 0,
                    'avg_events_per_session': 0,
                    'avg_page_views_per_session': 0
                }
            
            durations = [s['duration_minutes'] for s in sessions if s['duration_minutes'] > 0]
            
            return {
                'total_sessions': len(sessions),
                'avg_duration_minutes': sum(durations) / len(durations) if durations else 0,
                'avg_events_per_session': sum(s['event_count'] for s in sessions) / len(sessions),
                'avg_page_views_per_session': sum(s['page_views'] for s in sessions) / len(sessions),
                'sessions': sessions
            }
            
        except Exception as e:
            logger.error(f"❌ 获取会话统计失败: {e}")
            return {
                'total_sessions': 0,
                'avg_duration_minutes': 0,
                'avg_events_per_session': 0,
                'avg_page_views_per_session': 0
            }
    
    def get_funnel_analysis(self, funnel_steps: List[str], days: int = 7) -> Dict[str, Any]:
        """
        获取漏斗分析
        
        Args:
            funnel_steps: 漏斗步骤列表，按顺序排列
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 漏斗分析结果
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取每个步骤的用户数
            step_counts = []
            for i, step in enumerate(funnel_steps):
                pipeline = [
                    {
                        "$match": {
                            "timestamp": {"$gte": start_date, "$lte": end_date},
                            "event_type": step
                        }
                    },
                    {
                        "$group": {
                            "_id": "$user_id",
                            "count": {"$sum": 1}
                        }
                    },
                    {
                        "$count": "unique_users"
                    }
                ]
                
                result = list(self.db.events_collection.aggregate(pipeline))
                count = result[0]['unique_users'] if result else 0
                step_counts.append({
                    'step': step,
                    'users': count,
                    'conversion_rate': 0  # 将在下面计算
                })
            
            # 计算转化率
            for i in range(len(step_counts)):
                if i == 0:
                    step_counts[i]['conversion_rate'] = 100.0
                else:
                    previous_users = step_counts[i-1]['users']
                    current_users = step_counts[i]['users']
                    if previous_users > 0:
                        step_counts[i]['conversion_rate'] = (current_users / previous_users) * 100
                    else:
                        step_counts[i]['conversion_rate'] = 0.0
            
            return {
                'funnel_steps': step_counts,
                'overall_conversion': step_counts[-1]['conversion_rate'] if step_counts else 0,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 漏斗分析失败: {e}")
            return {}
    
    def get_retention_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        获取用户留存分析
        
        Args:
            days: 分析天数
            
        Returns:
            Dict[str, Any]: 留存分析结果
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 获取用户首次访问时间
            first_visit_pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": start_date, "$lte": end_date},
                        "user_id": {"$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "first_visit": {"$min": "$timestamp"}
                    }
                }
            ]
            
            first_visits = list(self.db.events_collection.aggregate(first_visit_pipeline))
            first_visit_dict = {v['_id']: v['first_visit'] for v in first_visits}
            
            # 计算留存率
            retention_data = []
            for day in range(1, 8):  # 1-7天留存
                cohort_users = []
                retained_users = []
                
                for user_id, first_visit in first_visit_dict.items():
                    cohort_date = first_visit.date()
                    if cohort_date >= (end_date - timedelta(days=days-day)).date():
                        cohort_users.append(user_id)
                        
                        # 检查用户在首次访问后第N天是否活跃
                        check_date = first_visit + timedelta(days=day)
                        check_start = check_date.replace(hour=0, minute=0, second=0, microsecond=0)
                        check_end = check_start + timedelta(days=1)
                        
                        user_events = self.db.events_collection.find({
                            "user_id": user_id,
                            "timestamp": {"$gte": check_start, "$lt": check_end}
                        })
                        
                        if list(user_events):
                            retained_users.append(user_id)
                
                retention_rate = (len(retained_users) / len(cohort_users) * 100) if cohort_users else 0
                retention_data.append({
                    'day': day,
                    'cohort_size': len(cohort_users),
                    'retained_users': len(retained_users),
                    'retention_rate': retention_rate
                })
            
            return {
                'retention_data': retention_data,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 留存分析失败: {e}")
            return {}
    
    def generate_visualization_report(self, days: int = 7, output_dir: str = 'analytics_reports') -> str:
        """
        生成可视化报告
        
        Args:
            days: 分析天数
            output_dir: 输出目录
            
        Returns:
            str: 报告文件路径
        """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取数据
            summary = self.get_user_behavior_summary(days)
            
            # 创建图表
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle(f'用户行为分析报告 - 最近{days}天', fontsize=16, fontweight='bold')
            
            # 1. 事件类型分布
            if summary.get('event_types'):
                event_types = [e['event_type'] for e in summary['event_types']]
                event_counts = [e['count'] for e in summary['event_types']]
                
                axes[0, 0].pie(event_counts, labels=event_types, autopct='%1.1f%%')
                axes[0, 0].set_title('事件类型分布')
            
            # 2. 页面访问TOP10
            if summary.get('top_pages'):
                pages = [p['page_url'][:30] + '...' if len(p['page_url']) > 30 else p['page_url'] 
                        for p in summary['top_pages'][:10]]
                views = [p['views'] for p in summary['top_pages'][:10]]
                
                axes[0, 1].barh(range(len(pages)), views)
                axes[0, 1].set_yticks(range(len(pages)))
                axes[0, 1].set_yticklabels(pages)
                axes[0, 1].set_title('页面访问TOP10')
                axes[0, 1].set_xlabel('访问次数')
            
            # 3. 用户活跃度趋势（模拟数据）
            dates = [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(days-1, -1, -1)]
            # 这里应该从实际数据中获取每日活跃用户数
            daily_active_users = [summary['overview']['active_users'] // days] * days
            
            axes[1, 0].plot(dates, daily_active_users, marker='o')
            axes[1, 0].set_title('每日活跃用户数')
            axes[1, 0].set_xlabel('日期')
            axes[1, 0].set_ylabel('活跃用户数')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # 4. 关键指标
            metrics = [
                f"总事件数: {summary['overview']['total_events']:,}",
                f"页面访问: {summary['overview']['total_page_views']:,}",
                f"活跃用户: {summary['overview']['active_users']:,}",
                f"总会话数: {summary['overview']['total_sessions']:,}"
            ]
            
            axes[1, 1].text(0.1, 0.8, '\n'.join(metrics), transform=axes[1, 1].transAxes,
                           fontsize=12, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            axes[1, 1].set_title('关键指标')
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            
            # 保存报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = os.path.join(output_dir, f'analytics_report_{timestamp}.png')
            plt.savefig(report_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"✅ 可视化报告已生成: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ 生成可视化报告失败: {e}")
            return ""
    
    def export_data_to_csv(self, days: int = 7, output_dir: str = 'analytics_reports') -> Dict[str, str]:
        """
        导出数据到CSV文件
        
        Args:
            days: 分析天数
            output_dir: 输出目录
            
        Returns:
            Dict[str, str]: 导出的文件路径
        """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            exported_files = {}
            
            # 导出事件数据
            events = self.db.get_events_by_date_range(start_date, end_date)
            if events:
                events_df = pd.DataFrame(events)
                events_file = os.path.join(output_dir, f'events_{timestamp}.csv')
                events_df.to_csv(events_file, index=False, encoding='utf-8-sig')
                exported_files['events'] = events_file
            
            # 导出页面访问数据
            pageviews = self.db.get_page_views_by_date_range(start_date, end_date)
            if pageviews:
                pageviews_df = pd.DataFrame(pageviews)
                pageviews_file = os.path.join(output_dir, f'pageviews_{timestamp}.csv')
                pageviews_df.to_csv(pageviews_file, index=False, encoding='utf-8-sig')
                exported_files['pageviews'] = pageviews_file
            
            logger.info(f"✅ 数据导出完成: {exported_files}")
            return exported_files
            
        except Exception as e:
            logger.error(f"❌ 数据导出失败: {e}")
            return {}
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """
        获取实时统计信息
        
        Returns:
            Dict[str, Any]: 实时统计信息
        """
        try:
            now = datetime.now()
            last_hour = now - timedelta(hours=1)
            last_24h = now - timedelta(hours=24)
            
            # 最近1小时事件数
            recent_events = self.db.events_collection.count_documents({
                "timestamp": {"$gte": last_hour}
            })
            
            # 最近24小时事件数
            daily_events = self.db.events_collection.count_documents({
                "timestamp": {"$gte": last_24h}
            })
            
            # 当前在线用户（最近5分钟有活动的用户）
            online_threshold = now - timedelta(minutes=5)
            online_users = len(self.db.events_collection.distinct("user_id", {
                "timestamp": {"$gte": online_threshold},
                "user_id": {"$ne": None}
            }))
            
            return {
                'timestamp': now.isoformat(),
                'recent_events_1h': recent_events,
                'recent_events_24h': daily_events,
                'online_users': online_users,
                'status': 'healthy' if self.db else 'unhealthy'
            }
            
        except Exception as e:
            logger.error(f"❌ 获取实时统计失败: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'recent_events_1h': 0,
                'recent_events_24h': 0,
                'online_users': 0,
                'status': 'error',
                'error': str(e)
            }

    def detect_abusive_users(
        self,
        days: int = 1,
        per_minute_threshold: int = 120,
        daily_event_threshold: int = 5000,
        form_submit_threshold: int = 300,
        identical_event_ratio_threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        识别疑似异常/攻击用户（对输入框或接口进行循环调用）

        判定维度：
        - 每分钟事件数过高（按 user_id / ip_address 分组）
        - 单日总事件数异常高
        - form_submit 类型事件异常高
        - 同质化事件比例过高（同一 page_url + element_id + event_type 占比）

        Returns:
            Dict[str, Any]: { 'period': {...}, 'abusers': [...], 'stats': {...} }
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        candidates: List[Dict[str, Any]] = []
        try:
            # 取出近期的事件（限制字段以减小内存）
            cursor = self.db.events_collection.find(
                {"timestamp": {"$gte": start_date, "$lte": end_date}},
                {
                    "user_id": 1,
                    "session_id": 1,
                    "event_type": 1,
                    "page_url": 1,
                    "element_id": 1,
                    "ip_address": 1,
                    "timestamp": 1,
                    "user_agent": 1,
                }
            )

            events: List[Dict[str, Any]] = list(cursor)
            if not events:
                return {
                    'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat(), 'days': days},
                    'abusers': [],
                    'stats': {'total_events': 0}
                }

            # 1) 每分钟速率检测（按 user_id 和 ip_address）
            from collections import defaultdict
            per_minute_counts_user: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
            per_minute_counts_ip: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

            # 2) 总量、表单提交、同质事件统计
            key_counts_user: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
            key_counts_ip: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
            totals_user: Dict[str, int] = defaultdict(int)
            totals_ip: Dict[str, int] = defaultdict(int)
            form_submits_user: Dict[str, int] = defaultdict(int)
            form_submits_ip: Dict[str, int] = defaultdict(int)

            for ev in events:
                ts = ev.get('timestamp')
                minute_key = ts.strftime('%Y-%m-%d %H:%M') if isinstance(ts, datetime) else str(ts)[:16]
                user_id = ev.get('user_id') or 'anonymous'
                ip = ev.get('ip_address') or 'unknown'
                event_type = ev.get('event_type') or 'unknown'
                page_url = ev.get('page_url') or ''
                element_id = ev.get('element_id') or ''

                signature = f"{event_type}|{page_url}|{element_id}"

                # 每分钟速率
                per_minute_counts_user[user_id][minute_key] += 1
                per_minute_counts_ip[ip][minute_key] += 1

                # 总量与类别
                totals_user[user_id] += 1
                totals_ip[ip] += 1
                key_counts_user[user_id][signature] += 1
                key_counts_ip[ip][signature] += 1
                if event_type == 'form_submit':
                    form_submits_user[user_id] += 1
                    form_submits_ip[ip] += 1

            def analyze(entity_id: str, per_minute: Dict[str, int], totals: int, form_submits: int, key_counts: Dict[str, int], id_type: str) -> Optional[Dict[str, Any]]:
                if totals == 0:
                    return None
                peak = max(per_minute.values()) if per_minute else 0
                dominant = max(key_counts.values()) if key_counts else 0
                identical_ratio = (dominant / totals) if totals > 0 else 0
                triggers = []
                if peak >= per_minute_threshold:
                    triggers.append(f"peak_per_minute>={per_minute_threshold}")
                if totals >= daily_event_threshold:
                    triggers.append(f"daily_events>={daily_event_threshold}")
                if form_submits >= form_submit_threshold:
                    triggers.append(f"form_submit>={form_submit_threshold}")
                if identical_ratio >= identical_event_ratio_threshold and totals >= 50:
                    triggers.append(f"identical_ratio>={identical_event_ratio_threshold}")
                if not triggers:
                    return None
                return {
                    id_type: entity_id,
                    'peak_per_minute': peak,
                    'daily_events': totals,
                    'form_submits': form_submits,
                    'identical_event_ratio': round(identical_ratio, 3),
                    'top_signature': max(key_counts, key=key_counts.get) if key_counts else '',
                    'triggers': triggers,
                }

            # 汇总嫌疑 user_id
            abusers: List[Dict[str, Any]] = []
            for uid, minutes in per_minute_counts_user.items():
                candidate = analyze(uid, minutes, totals_user[uid], form_submits_user[uid], key_counts_user[uid], 'user_id')
                if candidate:
                    abusers.append(candidate)

            # 汇总嫌疑 ip
            for ip, minutes in per_minute_counts_ip.items():
                candidate = analyze(ip, minutes, totals_ip[ip], form_submits_ip[ip], key_counts_ip[ip], 'ip_address')
                if candidate:
                    abusers.append(candidate)

            # 去重：如果同一主体既以 user_id 又以 ip 呈现，按更强触发排序
            abusers.sort(key=lambda x: (-(x['peak_per_minute']), -(x['daily_events'])))

            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'stats': {
                    'total_events': len(events),
                    'unique_users': len(totals_user),
                    'unique_ips': len(totals_ip)
                },
                'abusers': abusers[:200]
            }
        except Exception as e:
            logger.error(f"❌ 异常用户识别失败: {e}")
            return {
                'period': {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat(), 'days': days},
                'abusers': [],
                'error': str(e)
            }

def main():
    """主函数 - 演示分析功能"""
    try:
        # 初始化数据库连接
        db = TrackingDatabase()
        analytics = TrackingAnalytics(db)
        
        print("🔍 开始数据分析...")
        
        # 获取用户行为摘要
        summary = analytics.get_user_behavior_summary(days=7)
        print(f"📊 用户行为摘要: {json.dumps(summary, indent=2, ensure_ascii=False)}")
        
        # 获取实时统计
        realtime = analytics.get_real_time_stats()
        print(f"⏰ 实时统计: {json.dumps(realtime, indent=2, ensure_ascii=False)}")
        
        # 生成可视化报告
        report_path = analytics.generate_visualization_report(days=7)
        if report_path:
            print(f"📈 可视化报告已生成: {report_path}")
        
        # 导出数据
        exported_files = analytics.export_data_to_csv(days=7)
        if exported_files:
            print(f"📁 数据已导出: {exported_files}")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}")

if __name__ == '__main__':
    main()