#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常用户检测-调度脚本
- 每日定时运行 abuse_reporter.py 并发送报告
"""
import time
import schedule
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_once():
    logger.info('开始执行异常用户检测日报任务')
    try:
        result = subprocess.run(["python3", "abuse_reporter.py", "--days", "1"], capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            logger.info('异常用户检测日报任务完成')
        else:
            logger.error('异常用户检测日报任务失败')
            logger.error(result.stdout)
            logger.error(result.stderr)
    except Exception as e:
        logger.error(f'执行任务出错: {e}')


def main():
    # 默认每天 02:10 运行
    schedule.every().day.at("02:10").do(run_once)
    logger.info('异常用户检测调度器启动，计划任务: 每日 02:10 运行')
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    main()
