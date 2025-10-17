#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享返佣裂变系统 - 追踪分析模块
Referral Commission Fission System - Tracking Analytics

功能特性：
1. 实时数据追踪
2. 用户行为分析
3. 转化漏斗分析
4. 返佣效果评估
5. 数据报表生成
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrackingAnalytics:
    """追踪分析类"""
    
    def __init__(self, db_path: str = "referral_system.db"):
        self.db_path = db_path
        self.setup_matplotlib()
    
    def setup_matplotlib(self):
        """设置matplotlib中文字体"""
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_user_behavior_data(self, user_id: str = None, days: int = 30) -> Dict:
        """获取用户行为数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 时间范围
        start_date = datetime.now() - timedelta(days=days)
        
        # 基础查询条件
        where_clause = "WHERE created_at >= ?"
        params = [start_date]
        
        if user_id:
            where_clause += " AND user_id = ?"
            params.append(user_id)
        
        # 用户注册数据
        cursor.execute(f'''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users {where_clause}
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', params)
        user_registrations = dict(cursor.fetchall())
        
        # 链接点击数据
        cursor.execute(f'''
            SELECT DATE(cr.clicked_at) as date, COUNT(*) as count
            FROM click_records cr
            JOIN referral_links rl ON cr.link_id = rl.link_id
            {where_clause.replace('user_id', 'rl.user_id')}
            GROUP BY DATE(cr.clicked_at)
            ORDER BY date
        ''', params)
        link_clicks = dict(cursor.fetchall())
        
        # 转化数据
        cursor.execute(f'''
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM commissions {where_clause}
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', params)
        conversions = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'user_registrations': user_registrations,
            'link_clicks': link_clicks,
            'conversions': conversions
        }
    
    def get_conversion_funnel(self, days: int = 30) -> Dict:
        """获取转化漏斗数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 总点击量
        cursor.execute('''
            SELECT COUNT(*) FROM click_records cr
            JOIN referral_links rl ON cr.link_id = rl.link_id
            WHERE cr.clicked_at >= ?
        ''', (start_date,))
        total_clicks = cursor.fetchone()[0]
        
        # 通过分享链接注册的用户数
        cursor.execute('''
            SELECT COUNT(*) FROM users u
            JOIN referral_links rl ON u.referrer_id = rl.user_id
            WHERE u.created_at >= ?
        ''', (start_date,))
        registrations_from_links = cursor.fetchone()[0]
        
        # 总注册用户数
        cursor.execute('''
            SELECT COUNT(*) FROM users WHERE created_at >= ?
        ''', (start_date,))
        total_registrations = cursor.fetchone()[0]
        
        # 转化用户数
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM commissions WHERE created_at >= ?
        ''', (start_date,))
        conversions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_clicks': total_clicks,
            'registrations_from_links': registrations_from_links,
            'total_registrations': total_registrations,
            'conversions': conversions,
            'click_to_registration_rate': registrations_from_links / total_clicks if total_clicks > 0 else 0,
            'registration_to_conversion_rate': conversions / total_registrations if total_registrations > 0 else 0,
            'overall_conversion_rate': conversions / total_clicks if total_clicks > 0 else 0
        }
    
    def get_commission_analysis(self, days: int = 30) -> Dict:
        """获取返佣分析数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        
        # 返佣统计
        cursor.execute('''
            SELECT 
                commission_type,
                COUNT(*) as count,
                SUM(amount) as total_amount,
                AVG(amount) as avg_amount
            FROM commissions 
            WHERE created_at >= ?
            GROUP BY commission_type
        ''', (start_date,))
        
        commission_stats = {}
        for row in cursor.fetchall():
            commission_stats[row[0]] = {
                'count': row[1],
                'total_amount': row[2],
                'avg_amount': row[3]
            }
        
        # 返佣趋势
        cursor.execute('''
            SELECT DATE(created_at) as date, SUM(amount) as daily_amount
            FROM commissions 
            WHERE created_at >= ? AND status = 'confirmed'
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (start_date,))
        commission_trend = dict(cursor.fetchall())
        
        # 用户返佣排行
        cursor.execute('''
            SELECT 
                u.username,
                u.total_commission,
                COUNT(c.commission_id) as commission_count
            FROM users u
            LEFT JOIN commissions c ON u.user_id = c.referrer_id
            WHERE c.created_at >= ? OR c.created_at IS NULL
            GROUP BY u.user_id
            ORDER BY u.total_commission DESC
            LIMIT 10
        ''', (start_date,))
        top_earners = cursor.fetchall()
        
        conn.close()
        
        return {
            'commission_stats': commission_stats,
            'commission_trend': commission_trend,
            'top_earners': top_earners
        }
    
    def get_user_retention_analysis(self, days: int = 30) -> Dict:
        """获取用户留存分析"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取用户注册日期
        cursor.execute('''
            SELECT user_id, created_at FROM users 
            WHERE created_at >= ?
            ORDER BY created_at
        ''', (datetime.now() - timedelta(days=days),))
        
        user_registrations = cursor.fetchall()
        
        # 计算留存率
        retention_data = {}
        for user_id, reg_date in user_registrations:
            reg_date = datetime.strptime(reg_date, '%Y-%m-%d %H:%M:%S').date()
            
            # 检查用户是否有后续活动（点击或转化）
            cursor.execute('''
                SELECT COUNT(*) FROM (
                    SELECT 1 FROM click_records cr
                    JOIN referral_links rl ON cr.link_id = rl.link_id
                    WHERE rl.user_id = ? AND DATE(cr.clicked_at) > ?
                    UNION
                    SELECT 1 FROM commissions WHERE user_id = ? AND DATE(created_at) > ?
                )
            ''', (user_id, reg_date, user_id, reg_date))
            
            has_activity = cursor.fetchone()[0] > 0
            retention_data[user_id] = {
                'reg_date': reg_date,
                'retained': has_activity
            }
        
        conn.close()
        
        # 按注册日期分组计算留存率
        daily_retention = defaultdict(lambda: {'total': 0, 'retained': 0})
        for user_id, data in retention_data.items():
            date_key = data['reg_date'].strftime('%Y-%m-%d')
            daily_retention[date_key]['total'] += 1
            if data['retained']:
                daily_retention[date_key]['retained'] += 1
        
        # 计算留存率
        retention_rates = {}
        for date, stats in daily_retention.items():
            retention_rates[date] = stats['retained'] / stats['total'] if stats['total'] > 0 else 0
        
        return {
            'daily_retention': dict(daily_retention),
            'retention_rates': retention_rates,
            'overall_retention': sum(data['retained'] for data in retention_data.values()) / len(retention_data) if retention_data else 0
        }
    
    def generate_analytics_report(self, days: int = 30, output_file: str = None) -> str:
        """生成分析报告"""
        logger.info(f"开始生成{days}天分析报告...")
        
        # 获取各项数据
        behavior_data = self.get_user_behavior_data(days=days)
        funnel_data = self.get_conversion_funnel(days=days)
        commission_data = self.get_commission_analysis(days=days)
        retention_data = self.get_user_retention_analysis(days=days)
        
        # 生成报告内容
        report = f"""
# 分享返佣裂变系统分析报告

## 报告时间范围
- 开始时间: {(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')}
- 结束时间: {datetime.now().strftime('%Y-%m-%d')}
- 分析天数: {days}天

## 1. 用户行为分析

### 1.1 用户注册趋势
- 总注册用户: {sum(behavior_data['user_registrations'].values())}人
- 平均每日注册: {sum(behavior_data['user_registrations'].values()) / days:.1f}人/天

### 1.2 链接点击分析
- 总点击次数: {sum(behavior_data['link_clicks'].values())}次
- 平均每日点击: {sum(behavior_data['link_clicks'].values()) / days:.1f}次/天

### 1.3 转化分析
- 总转化次数: {sum(behavior_data['conversions'].values())}次
- 平均每日转化: {sum(behavior_data['conversions'].values()) / days:.1f}次/天

## 2. 转化漏斗分析

### 2.1 漏斗数据
- 总点击量: {funnel_data['total_clicks']}次
- 通过链接注册: {funnel_data['registrations_from_links']}人
- 总注册用户: {funnel_data['total_registrations']}人
- 转化用户: {funnel_data['conversions']}人

### 2.2 转化率
- 点击到注册转化率: {funnel_data['click_to_registration_rate']:.2%}
- 注册到转化转化率: {funnel_data['registration_to_conversion_rate']:.2%}
- 整体转化率: {funnel_data['overall_conversion_rate']:.2%}

## 3. 返佣分析

### 3.1 返佣统计
"""
        
        for comm_type, stats in commission_data['commission_stats'].items():
            report += f"- {comm_type}: {stats['count']}次, 总金额: ¥{stats['total_amount']:.2f}, 平均: ¥{stats['avg_amount']:.2f}\n"
        
        report += f"""
### 3.2 返佣趋势
- 总返佣金额: ¥{sum(commission_data['commission_trend'].values()):.2f}
- 平均每日返佣: ¥{sum(commission_data['commission_trend'].values()) / days:.2f}

### 3.3 返佣排行榜 (Top 10)
"""
        
        for i, (username, total_commission, count) in enumerate(commission_data['top_earners'][:10], 1):
            report += f"{i}. {username}: ¥{total_commission:.2f} ({count}次)\n"
        
        report += f"""
## 4. 用户留存分析

### 4.1 留存率统计
- 整体留存率: {retention_data['overall_retention']:.2%}
- 活跃用户数: {sum(data['retained'] for data in retention_data['daily_retention'].values())}人

## 5. 关键指标总结

| 指标 | 数值 | 说明 |
|------|------|------|
| 总用户数 | {sum(behavior_data['user_registrations'].values())} | 分析期间内注册的用户总数 |
| 总点击量 | {sum(behavior_data['link_clicks'].values())} | 分享链接的总点击次数 |
| 总转化数 | {sum(behavior_data['conversions'].values())} | 成功转化的订单数 |
| 整体转化率 | {funnel_data['overall_conversion_rate']:.2%} | 从点击到转化的整体转化率 |
| 总返佣金额 | ¥{sum(commission_data['commission_trend'].values()):.2f} | 分析期间内的总返佣金额 |
| 用户留存率 | {retention_data['overall_retention']:.2%} | 用户注册后的活跃留存率 |

## 6. 建议与优化

### 6.1 转化率优化
- 当前整体转化率为 {funnel_data['overall_conversion_rate']:.2%}
- 建议优化分享链接的吸引力和转化页面设计
- 考虑增加激励机制提高转化率

### 6.2 用户留存优化
- 当前用户留存率为 {retention_data['overall_retention']:.2%}
- 建议增加用户粘性功能，如积分系统、等级制度等
- 定期推送个性化内容提高用户活跃度

### 6.3 返佣策略优化
- 当前返佣总额为 ¥{sum(commission_data['commission_trend'].values()):.2f}
- 建议根据用户层级调整返佣比例
- 考虑增加特殊奖励机制激励高价值用户

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # 保存报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"分析报告已保存到: {output_file}")
        
        return report
    
    def create_visualization_charts(self, days: int = 30, output_dir: str = "charts"):
        """创建可视化图表"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取数据
        behavior_data = self.get_user_behavior_data(days=days)
        funnel_data = self.get_conversion_funnel(days=days)
        commission_data = self.get_commission_analysis(days=days)
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        fig_size = (12, 8)
        
        # 1. 用户注册趋势图
        plt.figure(figsize=fig_size)
        dates = sorted(behavior_data['user_registrations'].keys())
        counts = [behavior_data['user_registrations'].get(d, 0) for d in dates]
        
        plt.plot(dates, counts, marker='o', linewidth=2, markersize=6)
        plt.title(f'用户注册趋势 ({days}天)', fontsize=16, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('注册用户数', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/user_registration_trend.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 转化漏斗图
        plt.figure(figsize=fig_size)
        funnel_stages = ['点击', '注册', '转化']
        funnel_values = [
            funnel_data['total_clicks'],
            funnel_data['total_registrations'],
            funnel_data['conversions']
        ]
        
        bars = plt.bar(funnel_stages, funnel_values, color=['#667eea', '#764ba2', '#38a169'])
        plt.title(f'转化漏斗分析 ({days}天)', fontsize=16, fontweight='bold')
        plt.ylabel('数量', fontsize=12)
        
        # 添加数值标签
        for bar, value in zip(bars, funnel_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(funnel_values)*0.01,
                    f'{value}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/conversion_funnel.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 返佣趋势图
        plt.figure(figsize=fig_size)
        comm_dates = sorted(commission_data['commission_trend'].keys())
        comm_amounts = [commission_data['commission_trend'].get(d, 0) for d in comm_dates]
        
        plt.plot(comm_dates, comm_amounts, marker='s', linewidth=2, markersize=6, color='#e53e3e')
        plt.title(f'返佣趋势 ({days}天)', fontsize=16, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('返佣金额 (¥)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/commission_trend.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. 返佣类型分布饼图
        plt.figure(figsize=fig_size)
        comm_types = list(commission_data['commission_stats'].keys())
        comm_counts = [commission_data['commission_stats'][t]['count'] for t in comm_types]
        
        colors = ['#667eea', '#764ba2', '#38a169', '#e53e3e', '#f6ad55']
        plt.pie(comm_counts, labels=comm_types, autopct='%1.1f%%', colors=colors[:len(comm_types)])
        plt.title(f'返佣类型分布 ({days}天)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/commission_type_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"可视化图表已保存到: {output_dir}/")
    
    def get_real_time_metrics(self) -> Dict:
        """获取实时指标"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 今日数据
        today = datetime.now().date()
        
        # 今日注册用户
        cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?', (today,))
        today_registrations = cursor.fetchone()[0]
        
        # 今日点击量
        cursor.execute('''
            SELECT COUNT(*) FROM click_records cr
            JOIN referral_links rl ON cr.link_id = rl.link_id
            WHERE DATE(cr.clicked_at) = ?
        ''', (today,))
        today_clicks = cursor.fetchone()[0]
        
        # 今日转化
        cursor.execute('SELECT COUNT(*) FROM commissions WHERE DATE(created_at) = ?', (today,))
        today_conversions = cursor.fetchone()[0]
        
        # 今日返佣
        cursor.execute('SELECT SUM(amount) FROM commissions WHERE DATE(created_at) = ? AND status = "confirmed"', (today,))
        today_commission = cursor.fetchone()[0] or 0
        
        # 实时活跃用户（最近1小时有活动的用户）
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute('''
            SELECT COUNT(DISTINCT rl.user_id) FROM click_records cr
            JOIN referral_links rl ON cr.link_id = rl.link_id
            WHERE cr.clicked_at >= ?
        ''', (one_hour_ago,))
        active_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'today_registrations': today_registrations,
            'today_clicks': today_clicks,
            'today_conversions': today_conversions,
            'today_commission': today_commission,
            'active_users_1h': active_users,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """主函数 - 演示分析功能"""
    analytics = TrackingAnalytics()
    
    print("=== 分享返佣裂变系统 - 追踪分析演示 ===\n")
    
    # 1. 生成分析报告
    print("1. 生成30天分析报告...")
    report = analytics.generate_analytics_report(days=30, output_file="analytics_report.md")
    print("分析报告已生成: analytics_report.md")
    
    # 2. 创建可视化图表
    print("\n2. 创建可视化图表...")
    analytics.create_visualization_charts(days=30, output_dir="charts")
    print("图表已保存到: charts/ 目录")
    
    # 3. 获取实时指标
    print("\n3. 实时指标:")
    metrics = analytics.get_real_time_metrics()
    print(f"今日注册: {metrics['today_registrations']}人")
    print(f"今日点击: {metrics['today_clicks']}次")
    print(f"今日转化: {metrics['today_conversions']}次")
    print(f"今日返佣: ¥{metrics['today_commission']:.2f}")
    print(f"1小时活跃用户: {metrics['active_users_1h']}人")
    
    # 4. 转化漏斗分析
    print("\n4. 转化漏斗分析:")
    funnel = analytics.get_conversion_funnel(days=30)
    print(f"总点击: {funnel['total_clicks']}次")
    print(f"总注册: {funnel['total_registrations']}人")
    print(f"总转化: {funnel['conversions']}人")
    print(f"整体转化率: {funnel['overall_conversion_rate']:.2%}")
    
    # 5. 用户留存分析
    print("\n5. 用户留存分析:")
    retention = analytics.get_user_retention_analysis(days=30)
    print(f"整体留存率: {retention['overall_retention']:.2%}")

if __name__ == "__main__":
    main()