#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nginx访问日志分析工具
分析nginx访问日志，统计各个URL的访问次数，并生成报告
"""

import re
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
import os
import sys
from urllib.parse import urlparse, parse_qs
import gzip


class NginxLogAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.url_counter = Counter()
        self.status_code_counter = Counter()
        self.user_agent_counter = Counter()
        self.referer_counter = Counter()
        self.ip_counter = Counter()
        self.hourly_stats = defaultdict(int)
        self.daily_stats = defaultdict(int)
        self.method_counter = Counter()
        self.response_size_stats = defaultdict(list)
        
        # nginx日志格式的正则表达式
        # 默认格式: $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
        self.log_pattern = re.compile(
            r'(?P<ip>\S+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>\S+)" '
            r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" '
            r'"(?P<user_agent>[^"]*)"'
        )
    
    def parse_log_line(self, line):
        """解析单行日志"""
        match = self.log_pattern.match(line.strip())
        if match:
            return match.groupdict()
        return None
    
    def read_log_file(self):
        """读取日志文件，支持gzip压缩"""
        if not os.path.exists(self.log_file_path):
            raise FileNotFoundError(f"日志文件不存在: {self.log_file_path}")
        
        if self.log_file_path.endswith('.gz'):
            return gzip.open(self.log_file_path, 'rt', encoding='utf-8')
        else:
            return open(self.log_file_path, 'r', encoding='utf-8')
    
    def analyze_logs(self):
        """分析日志文件"""
        print(f"开始分析日志文件: {self.log_file_path}")
        
        try:
            with self.read_log_file() as f:
                line_count = 0
                parsed_count = 0
                
                for line in f:
                    line_count += 1
                    if line_count % 10000 == 0:
                        print(f"已处理 {line_count} 行...")
                    
                    log_entry = self.parse_log_line(line)
                    if log_entry:
                        parsed_count += 1
                        self._process_log_entry(log_entry)
                
                print(f"日志分析完成: 总行数 {line_count}, 成功解析 {parsed_count} 行")
                
        except Exception as e:
            print(f"读取日志文件时出错: {e}")
            return False
        
        return True
    
    def _process_log_entry(self, log_entry):
        """处理单条日志记录"""
        # 统计URL访问次数
        url = log_entry['url']
        self.url_counter[url] += 1
        
        # 统计状态码
        status = log_entry['status']
        self.status_code_counter[status] += 1
        
        # 统计用户代理
        user_agent = log_entry['user_agent']
        if user_agent and user_agent != '-':
            self.user_agent_counter[user_agent] += 1
        
        # 统计来源页面
        referer = log_entry['referer']
        if referer and referer != '-':
            self.referer_counter[referer] += 1
        
        # 统计IP地址
        ip = log_entry['ip']
        self.ip_counter[ip] += 1
        
        # 统计HTTP方法
        method = log_entry['method']
        self.method_counter[method] += 1
        
        # 统计响应大小
        size = int(log_entry['size'])
        self.response_size_stats[url].append(size)
        
        # 解析时间戳进行时间统计
        try:
            timestamp_str = log_entry['timestamp']
            # 解析nginx时间格式: 25/Dec/2023:10:30:45 +0800
            dt = datetime.strptime(timestamp_str.split()[0], '%d/%b/%Y:%H:%M:%S')
            self.hourly_stats[dt.hour] += 1
            self.daily_stats[dt.date()] += 1
        except:
            pass
    
    def get_top_urls(self, limit=20):
        """获取访问次数最多的URL"""
        return self.url_counter.most_common(limit)
    
    def get_status_code_stats(self):
        """获取状态码统计"""
        return dict(self.status_code_counter)
    
    def get_user_agent_stats(self, limit=10):
        """获取用户代理统计"""
        return self.user_agent_counter.most_common(limit)
    
    def get_referer_stats(self, limit=10):
        """获取来源页面统计"""
        return self.referer_counter.most_common(limit)
    
    def get_ip_stats(self, limit=10):
        """获取IP地址统计"""
        return self.ip_counter.most_common(limit)
    
    def get_method_stats(self):
        """获取HTTP方法统计"""
        return dict(self.method_counter)
    
    def get_hourly_stats(self):
        """获取小时访问统计"""
        return dict(self.hourly_stats)
    
    def get_daily_stats(self):
        """获取每日访问统计"""
        return {str(date): count for date, count in self.daily_stats.items()}
    
    def get_response_size_stats(self):
        """获取响应大小统计"""
        stats = {}
        for url, sizes in self.response_size_stats.items():
            if sizes:
                stats[url] = {
                    'count': len(sizes),
                    'avg_size': sum(sizes) / len(sizes),
                    'min_size': min(sizes),
                    'max_size': max(sizes),
                    'total_size': sum(sizes)
                }
        return stats
    
    def generate_report(self, output_file=None):
        """生成分析报告"""
        report = {
            'analysis_time': datetime.now().isoformat(),
            'log_file': self.log_file_path,
            'summary': {
                'total_requests': sum(self.url_counter.values()),
                'unique_urls': len(self.url_counter),
                'unique_ips': len(self.ip_counter),
                'date_range': {
                    'start': str(min(self.daily_stats.keys())) if self.daily_stats else None,
                    'end': str(max(self.daily_stats.keys())) if self.daily_stats else None
                }
            },
            'top_urls': self.get_top_urls(50),
            'status_codes': self.get_status_code_stats(),
            'http_methods': self.get_method_stats(),
            'top_user_agents': self.get_user_agent_stats(20),
            'top_referers': self.get_referer_stats(20),
            'top_ips': self.get_ip_stats(20),
            'hourly_distribution': self.get_hourly_stats(),
            'daily_distribution': self.get_daily_stats(),
            'response_size_stats': self.get_response_size_stats()
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"报告已保存到: {output_file}")
        
        return report
    
    def print_summary_report(self):
        """打印简要报告到控制台"""
        print("\n" + "="*60)
        print("NGINX访问日志分析报告")
        print("="*60)
        
        print(f"\n📊 总体统计:")
        print(f"   总请求数: {sum(self.url_counter.values()):,}")
        print(f"   唯一URL数: {len(self.url_counter):,}")
        print(f"   唯一IP数: {len(self.ip_counter):,}")
        
        if self.daily_stats:
            print(f"   日期范围: {min(self.daily_stats.keys())} 到 {max(self.daily_stats.keys())}")
        
        print(f"\n🔝 访问次数最多的URL (前20个):")
        for i, (url, count) in enumerate(self.get_top_urls(20), 1):
            print(f"   {i:2d}. {url} - {count:,} 次")
        
        print(f"\n📈 状态码分布:")
        for status, count in sorted(self.get_status_code_stats().items()):
            print(f"   {status}: {count:,} 次")
        
        print(f"\n🌐 HTTP方法分布:")
        for method, count in self.get_method_stats().items():
            print(f"   {method}: {count:,} 次")
        
        print(f"\n⏰ 小时访问分布 (前10个):")
        hourly = self.get_hourly_stats()
        for hour in sorted(hourly.keys())[:10]:
            print(f"   {hour:02d}:00 - {hourly[hour]:,} 次")
        
        print(f"\n🖥️  访问最多的IP (前10个):")
        for i, (ip, count) in enumerate(self.get_ip_stats(10), 1):
            print(f"   {i:2d}. {ip} - {count:,} 次")
        
        print(f"\n🔗 主要来源页面 (前10个):")
        for i, (referer, count) in enumerate(self.get_referer_stats(10), 1):
            print(f"   {i:2d}. {referer} - {count:,} 次")


def main():
    parser = argparse.ArgumentParser(description='Nginx访问日志分析工具')
    parser.add_argument('log_file', help='nginx访问日志文件路径')
    parser.add_argument('-o', '--output', help='输出报告文件路径 (JSON格式)')
    parser.add_argument('--top-urls', type=int, default=20, help='显示前N个访问最多的URL (默认: 20)')
    parser.add_argument('--quiet', action='store_true', help='只输出简要信息')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.log_file):
        print(f"错误: 日志文件不存在: {args.log_file}")
        sys.exit(1)
    
    try:
        analyzer = NginxLogAnalyzer(args.log_file)
        
        if analyzer.analyze_logs():
            if not args.quiet:
                analyzer.print_summary_report()
            
            if args.output:
                analyzer.generate_report(args.output)
                print(f"\n✅ 分析完成! 详细报告已保存到: {args.output}")
            else:
                print(f"\n✅ 分析完成!")
        else:
            print("❌ 日志分析失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()