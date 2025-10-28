#!/usr/bin/env python3
"""
asyncio.gather 和 asyncio.create_task 详解
演示asyncio库中最重要的并发工具的使用方法
"""

import asyncio
import time
import random
from typing import List, Any, Union
import functools


# 1. asyncio.gather 详解
async def gather_detailed_examples():
    """asyncio.gather 详细示例"""
    print("\n=== asyncio.gather 详解 ===")
    
    async def task(name: str, delay: float, should_fail: bool = False):
        print(f"任务 {name} 开始执行")
        await asyncio.sleep(delay)
        if should_fail:
            raise ValueError(f"任务 {name} 执行失败")
        print(f"任务 {name} 执行完成")
        return f"任务 {name} 的结果"
    
    # 1.1 基本用法
    print("1.1 基本用法:")
    tasks = [task(f"Task{i}", 0.5) for i in range(3)]
    results = await asyncio.gather(*tasks)
    print(f"基本结果: {results}")
    
    # 1.2 带 return_exceptions=True
    print("\n1.2 带异常处理:")
    mixed_tasks = [
        task("Success1", 0.5),
        task("Failure", 1.0, should_fail=True),
        task("Success2", 0.8)
    ]
    
    results = await asyncio.gather(*mixed_tasks, return_exceptions=True)
    print(f"包含异常的结果: {results}")
    
    # 1.3 部分成功处理
    successful = [r for r in results if not isinstance(r, Exception)]
    exceptions = [r for r in results if isinstance(r, Exception)]
    print(f"成功的结果: {successful}")
    print(f"异常: {exceptions}")
    
    # 1.4 使用 gather 进行错误恢复
    print("\n1.4 错误恢复:")
    async def recoverable_task(name: str, delay: float):
        try:
            return await task(name, delay, should_fail=random.random() > 0.7)
        except ValueError:
            print(f"任务 {name} 失败，尝试恢复...")
            await asyncio.sleep(0.1)
            return f"任务 {name} 恢复后的结果"
    
    recovery_tasks = [recoverable_task(f"Recovery{i}", 0.3) for i in range(5)]
    recovery_results = await asyncio.gather(*recovery_tasks)
    print(f"恢复后结果: {recovery_results}")


# 2. asyncio.create_task 详解
async def create_task_detailed_examples():
    """asyncio.create_task 详细示例"""
    print("\n=== asyncio.create_task 详解 ===")
    
    async def background_task(name: str, duration: float):
        print(f"后台任务 {name} 开始")
        await asyncio.sleep(duration)
        print(f"后台任务 {name} 完成")
        return f"后台任务 {name} 结果"
    
    # 2.1 基本用法
    print("1. 基本用法:")
    task1 = asyncio.create_task(background_task("Task1", 1.0))
    task2 = asyncio.create_task(background_task("Task2", 1.5))
    
    # 在任务运行期间做其他工作
    print("任务已启动，可以做其他工作...")
    await asyncio.sleep(0.5)
    print("其他工作完成")
    
    # 等待任务完成
    result1 = await task1
    result2 = await task2
    print(f"任务结果: {result1}, {result2}")
    
    # 2.2 任务状态检查
    print("\n2. 任务状态检查:")
    task = asyncio.create_task(background_task("StatusTask", 1.0))
    
    print(f"任务创建后状态: {task.done()}")
    await asyncio.sleep(0.5)
    print(f"任务运行中状态: {task.done()}")
    await task
    print(f"任务完成后状态: {task.done()}")
    
    # 2.3 任务取消
    print("\n3. 任务取消:")
    task = asyncio.create_task(background_task("CancelTask", 2.0))
    
    # 等待一段时间后取消
    await asyncio.sleep(0.5)
    cancelled = task.cancel()
    print(f"任务取消结果: {cancelled}")
    
    try:
        result = await task
        print(f"任务结果: {result}")
    except asyncio.CancelledError:
        print("任务被成功取消")
    
    # 2.4 任务异常处理
    print("\n4. 任务异常处理:")
    async def failing_task():
        await asyncio.sleep(0.5)
        raise ValueError("任务执行失败")
    
    task = asyncio.create_task(failing_task())
    
    try:
        result = await task
        print(f"任务结果: {result}")
    except ValueError as e:
        print(f"捕获任务异常: {e}")


# 3. gather vs create_task 对比
async def gather_vs_create_task():
    """gather vs create_task 对比"""
    print("\n=== gather vs create_task 对比 ===")
    
    async def sample_task(name: str, delay: float):
        print(f"任务 {name} 开始")
        await asyncio.sleep(delay)
        print(f"任务 {name} 完成")
        return f"任务 {name} 结果"
    
    # 使用 gather
    print("1. 使用 asyncio.gather:")
    start_time = time.time()
    gather_tasks = [
        sample_task(f"Gather{i}", 0.5)
        for i in range(3)
    ]
    gather_results = await asyncio.gather(*gather_tasks)
    gather_time = time.time() - start_time
    print(f"gather 结果: {gather_results}")
    print(f"gather 耗时: {gather_time:.2f}秒")
    
    # 使用 create_task
    print("\n2. 使用 asyncio.create_task:")
    start_time = time.time()
    create_tasks = [
        asyncio.create_task(sample_task(f"Create{i}", 0.5))
        for i in range(3)
    ]
    create_results = await asyncio.gather(*create_tasks)
    create_time = time.time() - start_time
    print(f"create_task 结果: {create_results}")
    print(f"create_task 耗时: {create_time:.2f}秒")
    
    # 3. 混合使用
    print("\n3. 混合使用:")
    # 先创建一些任务
    early_tasks = [
        asyncio.create_task(sample_task(f"Early{i}", 0.3))
        for i in range(2)
    ]
    
    # 在早期任务运行时创建更多任务
    await asyncio.sleep(0.1)
    late_tasks = [
        sample_task(f"Late{i}", 0.4)
        for i in range(2)
    ]
    
    # 等待所有任务完成
    all_results = await asyncio.gather(*early_tasks, *late_tasks)
    print(f"混合结果: {all_results}")


# 4. 高级 gather 用法
async def advanced_gather_usage():
    """高级 gather 用法"""
    print("\n=== 高级 gather 用法 ===")
    
    async def task_with_priority(name: str, priority: int, delay: float):
        print(f"优先级 {priority} 任务 {name} 开始")
        await asyncio.sleep(delay)
        print(f"优先级 {priority} 任务 {name} 完成")
        return {"name": name, "priority": priority, "result": f"任务 {name} 结果"}
    
    # 4.1 按优先级分组执行
    print("1. 按优先级分组执行:")
    high_priority_tasks = [
        task_with_priority(f"High{i}", 1, 0.3)
        for i in range(2)
    ]
    
    medium_priority_tasks = [
        task_with_priority(f"Medium{i}", 2, 0.5)
        for i in range(2)
    ]
    
    low_priority_tasks = [
        task_with_priority(f"Low{i}", 3, 0.7)
        for i in range(2)
    ]
    
    # 先执行高优先级任务
    high_results = await asyncio.gather(*high_priority_tasks)
    print(f"高优先级结果: {high_results}")
    
    # 然后并发执行中低优先级任务
    medium_low_results = await asyncio.gather(*medium_priority_tasks, *low_priority_tasks)
    print(f"中低优先级结果: {medium_low_results}")
    
    # 4.2 动态任务创建
    print("\n2. 动态任务创建:")
    async def dynamic_task_creator():
        tasks = []
        for i in range(3):
            task = asyncio.create_task(
                task_with_priority(f"Dynamic{i}", i+1, 0.4)
            )
            tasks.append(task)
            await asyncio.sleep(0.1)  # 模拟动态创建间隔
        
        return await asyncio.gather(*tasks)
    
    dynamic_results = await dynamic_task_creator()
    print(f"动态任务结果: {dynamic_results}")


# 5. 任务组合模式
async def task_composition_patterns():
    """任务组合模式"""
    print("\n=== 任务组合模式 ===")
    
    async def data_fetcher(source: str, delay: float):
        print(f"从 {source} 获取数据")
        await asyncio.sleep(delay)
        return f"来自 {source} 的数据"
    
    async def data_processor(data: str, process_time: float):
        print(f"处理数据: {data}")
        await asyncio.sleep(process_time)
        return f"处理后的 {data}"
    
    # 5.1 管道模式
    print("1. 管道模式:")
    # 先获取数据
    fetch_tasks = [
        data_fetcher(f"Source{i}", 0.5)
        for i in range(3)
    ]
    raw_data = await asyncio.gather(*fetch_tasks)
    
    # 然后处理数据
    process_tasks = [
        data_processor(data, 0.3)
        for data in raw_data
    ]
    processed_data = await asyncio.gather(*process_tasks)
    
    print(f"管道结果: {processed_data}")
    
    # 5.2 扇出扇入模式
    print("\n2. 扇出扇入模式:")
    async def fan_out_fan_in():
        # 扇出：创建多个获取任务
        fetch_tasks = [
            asyncio.create_task(data_fetcher(f"FanSource{i}", 0.4))
            for i in range(4)
        ]
        
        # 等待所有获取任务完成
        all_data = await asyncio.gather(*fetch_tasks)
        
        # 扇入：创建多个处理任务
        process_tasks = [
            asyncio.create_task(data_processor(data, 0.2))
            for data in all_data
        ]
        
        # 等待所有处理任务完成
        return await asyncio.gather(*process_tasks)
    
    fan_results = await fan_out_fan_in()
    print(f"扇出扇入结果: {fan_results}")


# 6. 错误处理和重试
async def error_handling_and_retry():
    """错误处理和重试"""
    print("\n=== 错误处理和重试 ===")
    
    async def unreliable_task(name: str, success_rate: float = 0.7):
        await asyncio.sleep(0.2)
        if random.random() > success_rate:
            raise ValueError(f"任务 {name} 随机失败")
        return f"任务 {name} 成功"
    
    async def retry_task(name: str, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                return await unreliable_task(name, 0.6)
            except ValueError as e:
                print(f"任务 {name} 第 {attempt + 1} 次尝试失败: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1 * (attempt + 1))  # 指数退避
                else:
                    raise e
    
    # 1. 基本重试
    print("1. 基本重试:")
    retry_tasks = [retry_task(f"Retry{i}") for i in range(3)]
    retry_results = await asyncio.gather(*retry_tasks, return_exceptions=True)
    print(f"重试结果: {retry_results}")
    
    # 2. 部分重试
    print("\n2. 部分重试:")
    async def selective_retry():
        tasks = [
            asyncio.create_task(unreliable_task(f"Selective{i}", 0.8))
            for i in range(5)
        ]
        
        results = []
        for i, task in enumerate(tasks):
            try:
                result = await task
                results.append(result)
            except ValueError:
                print(f"任务 {i} 失败，尝试重试...")
                try:
                    retry_result = await retry_task(f"Retry{i}")
                    results.append(retry_result)
                except ValueError:
                    results.append(f"任务 {i} 最终失败")
        
        return results
    
    selective_results = await selective_retry()
    print(f"选择性重试结果: {selective_results}")


# 7. 性能优化技巧
async def performance_optimization():
    """性能优化技巧"""
    print("\n=== 性能优化技巧 ===")
    
    async def cpu_intensive_task(n: int):
        """模拟CPU密集型任务"""
        result = 0
        for i in range(n):
            result += i * i
        return result
    
    async def io_intensive_task(delay: float):
        """模拟IO密集型任务"""
        await asyncio.sleep(delay)
        return f"IO任务完成，延迟: {delay}"
    
    # 1. 混合任务优化
    print("1. 混合任务优化:")
    start_time = time.time()
    
    # 创建IO任务
    io_tasks = [
        asyncio.create_task(io_intensive_task(0.5))
        for _ in range(3)
    ]
    
    # 在IO任务运行时执行CPU任务
    cpu_result = cpu_intensive_task(100000)
    
    # 等待IO任务完成
    io_results = await asyncio.gather(*io_tasks)
    
    end_time = time.time()
    print(f"CPU结果: {cpu_result}")
    print(f"IO结果: {io_results}")
    print(f"混合执行时间: {end_time - start_time:.2f}秒")
    
    # 2. 批量处理优化
    print("\n2. 批量处理优化:")
    async def batch_processor(items: List[str], batch_size: int = 3):
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [
                asyncio.create_task(io_intensive_task(0.3))
                for _ in batch
            ]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
        return results
    
    items = [f"Item{i}" for i in range(10)]
    batch_results = await batch_processor(items, 3)
    print(f"批量处理结果数量: {len(batch_results)}")


# 主函数
async def main():
    """主函数"""
    print("asyncio.gather 和 asyncio.create_task 详解")
    print("=" * 60)
    
    # 运行所有示例
    await gather_detailed_examples()
    await create_task_detailed_examples()
    await gather_vs_create_task()
    await advanced_gather_usage()
    await task_composition_patterns()
    await error_handling_and_retry()
    await performance_optimization()


if __name__ == "__main__":
    asyncio.run(main())