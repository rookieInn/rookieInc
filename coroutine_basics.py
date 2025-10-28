#!/usr/bin/env python3
"""
Python协程基础示例
演示协程的基本概念和用法
"""

import asyncio
import time
import random
from typing import List


# 1. 基础协程函数
async def simple_coroutine():
    """最简单的协程函数"""
    print("协程开始执行")
    await asyncio.sleep(1)  # 模拟异步操作
    print("协程执行完成")
    return "协程返回值"


# 2. 带参数的协程
async def greet(name: str, delay: float = 1.0):
    """带参数的协程函数"""
    print(f"开始问候 {name}")
    await asyncio.sleep(delay)
    print(f"你好, {name}!")
    return f"问候完成: {name}"


# 3. 模拟网络请求的协程
async def fetch_data(url: str, delay: float = 2.0):
    """模拟网络请求"""
    print(f"开始请求: {url}")
    await asyncio.sleep(delay)  # 模拟网络延迟
    data = f"来自 {url} 的数据"
    print(f"请求完成: {url}")
    return data


# 4. 协程并发执行
async def concurrent_example():
    """演示协程并发执行"""
    print("\n=== 并发执行示例 ===")
    
    # 使用 asyncio.gather 并发执行多个协程
    tasks = [
        fetch_data("https://api1.com", 1.0),
        fetch_data("https://api2.com", 1.5),
        fetch_data("https://api3.com", 2.0)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    print(f"并发执行结果: {results}")
    print(f"总耗时: {end_time - start_time:.2f}秒")


# 5. 使用 asyncio.create_task
async def task_example():
    """演示使用 create_task 创建任务"""
    print("\n=== Task 示例 ===")
    
    # 创建任务
    task1 = asyncio.create_task(fetch_data("https://task1.com", 1.0))
    task2 = asyncio.create_task(fetch_data("https://task2.com", 1.5))
    
    # 等待任务完成
    result1 = await task1
    result2 = await task2
    
    print(f"Task1 结果: {result1}")
    print(f"Task2 结果: {result2}")


# 6. 协程异常处理
async def error_handling_example():
    """演示协程异常处理"""
    print("\n=== 异常处理示例 ===")
    
    async def risky_operation():
        await asyncio.sleep(1)
        if random.random() > 0.5:
            raise ValueError("随机错误!")
        return "操作成功"
    
    try:
        result = await risky_operation()
        print(f"操作结果: {result}")
    except ValueError as e:
        print(f"捕获到错误: {e}")


# 7. 协程生成器
async def coroutine_generator(n: int):
    """协程生成器示例"""
    print(f"\n=== 协程生成器示例 (生成 {n} 个值) ===")
    
    for i in range(n):
        print(f"生成值: {i}")
        await asyncio.sleep(0.5)
        yield i


# 8. 实际应用场景：批量处理
async def batch_processing_example():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    async def process_item(item_id: int):
        """处理单个项目"""
        print(f"开始处理项目 {item_id}")
        await asyncio.sleep(random.uniform(0.5, 2.0))  # 模拟处理时间
        result = f"项目 {item_id} 处理完成"
        print(result)
        return result
    
    # 批量处理10个项目
    items = list(range(1, 11))
    tasks = [process_item(item_id) for item_id in items]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()
    
    print(f"\n批量处理完成，总耗时: {end_time - start_time:.2f}秒")
    print(f"成功处理: {len([r for r in results if not isinstance(r, Exception)])} 个项目")


# 9. 协程超时控制
async def timeout_example():
    """超时控制示例"""
    print("\n=== 超时控制示例 ===")
    
    async def slow_operation():
        await asyncio.sleep(3)  # 3秒操作
        return "操作完成"
    
    try:
        # 设置2秒超时
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
        print(f"操作结果: {result}")
    except asyncio.TimeoutError:
        print("操作超时!")


# 10. 协程同步原语
async def synchronization_example():
    """同步原语示例"""
    print("\n=== 同步原语示例 ===")
    
    # 使用锁
    lock = asyncio.Lock()
    shared_resource = 0
    
    async def worker(worker_id: int):
        nonlocal shared_resource
        async with lock:
            print(f"Worker {worker_id} 获得锁")
            await asyncio.sleep(0.5)
            shared_resource += 1
            print(f"Worker {worker_id} 更新共享资源: {shared_resource}")
    
    # 创建多个工作协程
    workers = [worker(i) for i in range(3)]
    await asyncio.gather(*workers)
    print(f"最终共享资源值: {shared_resource}")


# 主函数
async def main():
    """主函数，演示所有协程用法"""
    print("Python协程使用示例")
    print("=" * 50)
    
    # 1. 基础协程
    print("\n1. 基础协程:")
    result = await simple_coroutine()
    print(f"返回值: {result}")
    
    # 2. 带参数协程
    print("\n2. 带参数协程:")
    await greet("张三", 0.5)
    
    # 3. 并发执行
    await concurrent_example()
    
    # 4. Task示例
    await task_example()
    
    # 5. 异常处理
    await error_handling_example()
    
    # 6. 协程生成器
    print("\n6. 协程生成器:")
    async for value in coroutine_generator(3):
        print(f"接收到值: {value}")
    
    # 7. 批量处理
    await batch_processing_example()
    
    # 8. 超时控制
    await timeout_example()
    
    # 9. 同步原语
    await synchronization_example()


if __name__ == "__main__":
    # 运行主协程
    asyncio.run(main())