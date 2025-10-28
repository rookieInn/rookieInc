#!/usr/bin/env python3
"""
Python协程并发执行详解
演示如何使用协程实现高效的并发编程
"""

import asyncio
import time
import random
from typing import List, Any
import aiohttp
import json


# 1. 基础并发示例
async def basic_concurrency():
    """基础并发示例"""
    print("\n=== 基础并发示例 ===")
    
    async def worker(name: str, work_time: float):
        print(f"Worker {name} 开始工作")
        await asyncio.sleep(work_time)
        print(f"Worker {name} 完成工作")
        return f"Worker {name} 的结果"
    
    # 创建多个工作协程
    workers = [
        worker("A", 1.0),
        worker("B", 1.5),
        worker("C", 2.0)
    ]
    
    # 并发执行
    start_time = time.time()
    results = await asyncio.gather(*workers)
    end_time = time.time()
    
    print(f"并发执行结果: {results}")
    print(f"总耗时: {end_time - start_time:.2f}秒")


# 2. 使用 asyncio.gather 的不同方式
async def gather_variations():
    """asyncio.gather 的不同使用方式"""
    print("\n=== asyncio.gather 变体 ===")
    
    async def task(name: str, delay: float, should_fail: bool = False):
        print(f"任务 {name} 开始")
        await asyncio.sleep(delay)
        if should_fail:
            raise ValueError(f"任务 {name} 失败")
        print(f"任务 {name} 完成")
        return f"任务 {name} 结果"
    
    # 1. 基本用法
    print("1. 基本用法:")
    tasks = [task(f"Task{i}", 0.5) for i in range(3)]
    results = await asyncio.gather(*tasks)
    print(f"基本结果: {results}")
    
    # 2. 带异常处理
    print("\n2. 带异常处理:")
    mixed_tasks = [
        task("Success1", 0.5),
        task("Failure", 0.8, should_fail=True),
        task("Success2", 1.0)
    ]
    
    try:
        results = await asyncio.gather(*mixed_tasks)
        print(f"成功结果: {results}")
    except ValueError as e:
        print(f"捕获异常: {e}")
    
    # 3. 返回异常而不是抛出
    print("\n3. 返回异常:")
    results = await asyncio.gather(*mixed_tasks, return_exceptions=True)
    print(f"包含异常的结果: {results}")
    
    # 4. 部分成功处理
    print("\n4. 部分成功处理:")
    successful_results = [r for r in results if not isinstance(r, Exception)]
    exceptions = [r for r in results if isinstance(r, Exception)]
    
    print(f"成功的结果: {successful_results}")
    print(f"异常: {exceptions}")


# 3. 使用 asyncio.create_task
async def create_task_example():
    """asyncio.create_task 示例"""
    print("\n=== asyncio.create_task 示例 ===")
    
    async def long_running_task(name: str, duration: float):
        print(f"长时间任务 {name} 开始")
        await asyncio.sleep(duration)
        print(f"长时间任务 {name} 完成")
        return f"长时间任务 {name} 结果"
    
    # 创建任务
    task1 = asyncio.create_task(long_running_task("Task1", 2.0))
    task2 = asyncio.create_task(long_running_task("Task2", 1.5))
    task3 = asyncio.create_task(long_running_task("Task3", 1.0))
    
    print("任务已创建，可以继续做其他工作...")
    
    # 在等待任务完成时做其他工作
    for i in range(3):
        print(f"做其他工作 {i+1}")
        await asyncio.sleep(0.3)
    
    # 等待所有任务完成
    results = await asyncio.gather(task1, task2, task3)
    print(f"所有任务完成: {results}")


# 4. 任务取消和超时
async def task_cancellation():
    """任务取消和超时示例"""
    print("\n=== 任务取消和超时 ===")
    
    async def cancellable_task(name: str, duration: float):
        try:
            print(f"可取消任务 {name} 开始")
            await asyncio.sleep(duration)
            print(f"可取消任务 {name} 完成")
            return f"任务 {name} 结果"
        except asyncio.CancelledError:
            print(f"任务 {name} 被取消")
            raise
    
    # 1. 任务超时
    print("1. 任务超时:")
    try:
        result = await asyncio.wait_for(
            cancellable_task("TimeoutTask", 3.0),
            timeout=1.5
        )
        print(f"任务结果: {result}")
    except asyncio.TimeoutError:
        print("任务超时!")
    
    # 2. 手动取消任务
    print("\n2. 手动取消任务:")
    task = asyncio.create_task(cancellable_task("CancelTask", 2.0))
    
    # 等待一段时间后取消
    await asyncio.sleep(1.0)
    task.cancel()
    
    try:
        result = await task
        print(f"任务结果: {result}")
    except asyncio.CancelledError:
        print("任务被手动取消")


# 5. 协程池和限制并发数
async def coroutine_pool():
    """协程池和限制并发数"""
    print("\n=== 协程池示例 ===")
    
    async def worker_with_semaphore(semaphore: asyncio.Semaphore, worker_id: int):
        async with semaphore:
            print(f"Worker {worker_id} 获得信号量")
            await asyncio.sleep(1.0)  # 模拟工作
            print(f"Worker {worker_id} 释放信号量")
            return f"Worker {worker_id} 完成"
    
    # 限制同时运行的协程数量为3
    semaphore = asyncio.Semaphore(3)
    
    # 创建10个任务
    tasks = [
        worker_with_semaphore(semaphore, i)
        for i in range(10)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"协程池结果: {results}")
    print(f"总耗时: {end_time - start_time:.2f}秒")


# 6. 生产者-消费者模式
async def producer_consumer():
    """生产者-消费者模式"""
    print("\n=== 生产者-消费者模式 ===")
    
    async def producer(queue: asyncio.Queue, producer_id: int, count: int):
        """生产者协程"""
        for i in range(count):
            item = f"Producer{producer_id}-Item{i}"
            await queue.put(item)
            print(f"生产者 {producer_id} 生产: {item}")
            await asyncio.sleep(0.1)
        
        # 发送结束信号
        await queue.put(None)
        print(f"生产者 {producer_id} 完成")
    
    async def consumer(queue: asyncio.Queue, consumer_id: int):
        """消费者协程"""
        while True:
            item = await queue.get()
            if item is None:
                break
            
            print(f"消费者 {consumer_id} 消费: {item}")
            await asyncio.sleep(0.2)  # 模拟处理时间
            queue.task_done()
        
        print(f"消费者 {consumer_id} 完成")
    
    # 创建队列
    queue = asyncio.Queue(maxsize=5)
    
    # 创建生产者和消费者
    producers = [
        asyncio.create_task(producer(queue, i, 3))
        for i in range(2)
    ]
    
    consumers = [
        asyncio.create_task(consumer(queue, i))
        for i in range(2)
    ]
    
    # 等待所有生产者完成
    await asyncio.gather(*producers)
    
    # 等待队列为空
    await queue.join()
    
    # 取消消费者
    for consumer_task in consumers:
        consumer_task.cancel()
    
    print("生产者-消费者模式完成")


# 7. 协程间通信
async def coroutine_communication():
    """协程间通信示例"""
    print("\n=== 协程间通信 ===")
    
    async def sender(event: asyncio.Event, data: str):
        """发送者协程"""
        print(f"发送者准备发送: {data}")
        await asyncio.sleep(1.0)  # 模拟准备时间
        print(f"发送者发送: {data}")
        event.set()  # 设置事件
    
    async def receiver(event: asyncio.Event, receiver_id: int):
        """接收者协程"""
        print(f"接收者 {receiver_id} 等待数据...")
        await event.wait()  # 等待事件
        print(f"接收者 {receiver_id} 收到数据!")
    
    # 创建事件
    event = asyncio.Event()
    
    # 创建发送者和接收者
    sender_task = asyncio.create_task(sender(event, "重要数据"))
    receivers = [
        asyncio.create_task(receiver(event, i))
        for i in range(3)
    ]
    
    # 等待所有任务完成
    await asyncio.gather(sender_task, *receivers)


# 8. 实际应用：并发网络请求
async def concurrent_network_requests():
    """并发网络请求示例"""
    print("\n=== 并发网络请求 ===")
    
    # 模拟网络请求（不使用真实网络）
    async def mock_http_request(url: str, delay: float = 1.0):
        """模拟HTTP请求"""
        print(f"开始请求: {url}")
        await asyncio.sleep(delay)
        return {
            "url": url,
            "status": 200,
            "data": f"来自 {url} 的响应数据"
        }
    
    # 多个URL
    urls = [
        "https://api1.example.com",
        "https://api2.example.com",
        "https://api3.example.com",
        "https://api4.example.com",
        "https://api5.example.com"
    ]
    
    # 并发请求
    start_time = time.time()
    tasks = [mock_http_request(url, random.uniform(0.5, 2.0)) for url in urls]
    responses = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"并发请求完成，耗时: {end_time - start_time:.2f}秒")
    for response in responses:
        print(f"响应: {response['url']} - {response['status']}")


# 9. 协程性能对比
async def performance_comparison():
    """协程性能对比"""
    print("\n=== 性能对比 ===")
    
    async def single_task(delay: float):
        await asyncio.sleep(delay)
        return f"任务完成，延迟: {delay}"
    
    # 串行执行
    print("1. 串行执行:")
    start_time = time.time()
    for i in range(5):
        result = await single_task(0.2)
        print(f"  串行任务 {i+1}: {result}")
    serial_time = time.time() - start_time
    print(f"串行总耗时: {serial_time:.2f}秒")
    
    # 并发执行
    print("\n2. 并发执行:")
    start_time = time.time()
    tasks = [single_task(0.2) for _ in range(5)]
    results = await asyncio.gather(*tasks)
    concurrent_time = time.time() - start_time
    
    for i, result in enumerate(results):
        print(f"  并发任务 {i+1}: {result}")
    print(f"并发总耗时: {concurrent_time:.2f}秒")
    
    print(f"\n性能提升: {serial_time/concurrent_time:.1f}x")


# 主函数
async def main():
    """主函数"""
    print("Python协程并发执行详解")
    print("=" * 50)
    
    # 运行所有示例
    await basic_concurrency()
    await gather_variations()
    await create_task_example()
    await task_cancellation()
    await coroutine_pool()
    await producer_consumer()
    await coroutine_communication()
    await concurrent_network_requests()
    await performance_comparison()


if __name__ == "__main__":
    asyncio.run(main())