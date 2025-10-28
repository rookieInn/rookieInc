#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志分析工具 - 统计指定时间段内各日志级别的条数
支持多种日志格式，包括标准Python logging格式
"""

import re
import argparse
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import glob


class LogAnalyzer:
    def __init__(self):
        # 常见的日志级别
        self.log_levels = ['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL', 'FATAL']
        
        # 时间格式模式（按优先级排序）
        self.time_patterns = [
            # 2025-09-09 02:40:14,059
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:,\d{3})?)',
            # 2025-09-09 02:40:14
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            # 09/09/2025 02:40:14
            r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
            # Sep 09 02:40:14
            r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',
        ]
        
        # 对应的日期时间格式
        self.time_formats = [
            '%Y-%m-%d %H:%M:%S,%f',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%b %d %H:%M:%S',
        ]

    def parse_timestamp(self, line):
        """从日志行中提取时间戳"""
        for pattern, fmt in zip(self.time_patterns, self.time_formats):
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(1)
                    # 处理毫秒部分
                    if ',' in timestamp_str:
                        timestamp_str = timestamp_str.replace(',', '.')
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
        return None

    def extract_log_level(self, line):
        """从日志行中提取日志级别"""
        # 查找日志级别（通常在时间戳之后）
        for level in self.log_levels:
            # 使用更精确的匹配，避免误匹配
            pattern = r'-\s+' + level + r'\s+-'
            if re.search(pattern, line):
                return level
        return None

    def analyze_log_file(self, file_path, start_time=None, end_time=None):
        """分析单个日志文件"""
        results = defaultdict(int)
        total_lines = 0
        parsed_lines = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    total_lines += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    # 提取时间戳
                    timestamp = self.parse_timestamp(line)
                    if not timestamp:
                        continue
                    
                    # 检查时间范围
                    if start_time and timestamp < start_time:
                        continue
                    if end_time and timestamp > end_time:
                        continue
                    
                    # 提取日志级别
                    log_level = self.extract_log_level(line)
                    if log_level:
                        results[log_level] += 1
                        parsed_lines += 1
                    else:
                        # 如果没有识别到日志级别，归类为UNKNOWN
                        results['UNKNOWN'] += 1
                        parsed_lines += 1
                        
        except FileNotFoundError:
            print(f"错误：找不到文件 {file_path}")
            return None
        except Exception as e:
            print(f"错误：读取文件 {file_path} 时出错: {e}")
            return None
        
        return {
            'results': dict(results),
            'total_lines': total_lines,
            'parsed_lines': parsed_lines,
            'file_path': file_path
        }

    def find_log_files(self, pattern):
        """查找匹配的日志文件"""
        if '*' in pattern or '?' in pattern:
            return glob.glob(pattern)
        else:
            return [pattern] if Path(pattern).exists() else []

    def print_results(self, analysis_results, show_details=True):
        """打印分析结果"""
        if not analysis_results:
            print("没有找到有效的日志文件或分析结果")
            return
        
        for result in analysis_results:
            if not result:
                continue
                
            print(f"\n{'='*60}")
            print(f"文件: {result['file_path']}")
            print(f"总行数: {result['total_lines']}")
            print(f"解析行数: {result['parsed_lines']}")
            print(f"{'='*60}")
            
            if show_details:
                print("日志级别统计:")
                print("-" * 40)
                
                # 按日志级别排序显示
                sorted_levels = sorted(result['results'].items(), 
                                     key=lambda x: self.log_levels.index(x[0]) if x[0] in self.log_levels else 999)
                
                for level, count in sorted_levels:
                    print(f"{level:12}: {count:6} 条")
                
                print("-" * 40)
                print(f"{'总计':12}: {sum(result['results'].values()):6} 条")
            else:
                # 简化输出
                for level, count in sorted(result['results'].items()):
                    print(f"{level}: {count}")

    def run(self, args):
        """运行日志分析"""
        # 解析时间参数
        start_time = None
        end_time = None
        
        if args.start_time:
            try:
                start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("错误：开始时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式")
                return
        
        if args.end_time:
            try:
                end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("错误：结束时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式")
                return
        
        # 查找日志文件
        log_files = self.find_log_files(args.log_file)
        
        if not log_files:
            print(f"错误：没有找到匹配的日志文件: {args.log_file}")
            return
        
        print(f"找到 {len(log_files)} 个日志文件")
        
        # 分析每个文件
        all_results = []
        for log_file in log_files:
            print(f"正在分析: {log_file}")
            result = self.analyze_log_file(log_file, start_time, end_time)
            all_results.append(result)
        
        # 打印结果
        self.print_results(all_results, not args.quiet)
        
        # 如果指定了多个文件，显示汇总
        if len(log_files) > 1:
            print(f"\n{'='*60}")
            print("汇总统计:")
            print(f"{'='*60}")
            
            total_summary = defaultdict(int)
            for result in all_results:
                if result:
                    for level, count in result['results'].items():
                        total_summary[level] += count
            
            for level, count in sorted(total_summary.items()):
                print(f"{level:12}: {count:6} 条")
            print("-" * 40)
            print(f"{'总计':12}: {sum(total_summary.values()):6} 条")


def main():
    parser = argparse.ArgumentParser(
        description='日志分析工具 - 统计指定时间段内各日志级别的条数',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析单个日志文件
  python log_analyzer.py bookmark_sync.log
  
  # 分析指定时间段的日志
  python log_analyzer.py bookmark_sync.log --start-time "2025-09-09 00:00:00" --end-time "2025-09-09 23:59:59"
  
  # 分析多个日志文件
  python log_analyzer.py "*.log"
  
  # 只显示统计结果（不显示详细信息）
  python log_analyzer.py bookmark_sync.log --quiet
        """
    )
    
    parser.add_argument('log_file', help='日志文件路径（支持通配符）')
    parser.add_argument('--start-time', help='开始时间 (格式: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', help='结束时间 (格式: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--quiet', '-q', action='store_true', help='只显示统计结果，不显示详细信息')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    analyzer.run(args)


if __name__ == '__main__':
    main()